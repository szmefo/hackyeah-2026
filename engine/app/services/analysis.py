"""One transient FIT + CGM upload becomes an evidence-linked run story.

All displayed numbers come from measurements or labelled calculations. Imported
run signals select useful windows; their HR-zone estimates are never exposed.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from io import BytesIO
from statistics import mean, median
from typing import Any

from app.services.fit_adapter import adapt_fit_activity_to_streams
from app.services.fit_parser import FitParseError, parse_fit_bytes
from app.services.glucose import GlucoseParseError, parse_glucose_csv, resolve_timezone
from app.services.run_signal_extractor import ProfileCtx, cumulative_distance_m, extract_run_signals


class AnalysisError(ValueError):
    def __init__(self, code: str, detail_pl: str) -> None:
        super().__init__(code)
        self.code = code
        self.detail_pl = detail_pl


def _number(value: Any, *, positive: bool = False) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(result) or (positive and result <= 0):
        return None
    return result


def _rounded(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def _record_times(content: bytes, start: datetime) -> list[float]:
    """Audit raw record stamps: parser's compatibility fallback is not CGM-safe.

    The Background IP parser normalizes duplicates and missing stamps. We reject
    those files for alignment rather than pretending normalized times are real.
    Re-decoding is bounded by the upload limit and reveals no GPS or identity.
    """
    from garmin_fit_sdk import Decoder, Stream

    messages, errors = Decoder(Stream.from_bytes_io(BytesIO(content))).read(
        convert_datetimes_to_dates=False, convert_types_to_strings=True
    )
    if errors:
        raise AnalysisError("decode_failed", "Nie można odczytać FIT. Wyeksportuj plik ponownie.")
    if len(messages.get("session_mesgs", [])) > 1:
        raise AnalysisError("multiple_sessions", "FIT zawiera więcej niż jedną sesję. Wyeksportuj pojedynczy bieg.")
    records = messages.get("record_mesgs", [])
    if len(records) < 2 or len(records) > 60_000:
        raise AnalysisError("fit_samples", "FIT musi zawierać od 2 do 60 000 próbek biegu.")
    epoch = datetime(1989, 12, 31, tzinfo=timezone.utc)
    times = []
    for record in records:
        raw = record.get("timestamp")
        seconds = _number(raw)
        if seconds is None:
            raise AnalysisError(
                "fit_timestamps", "Brakuje czasu przy próbkach FIT. Nie można uczciwie połączyć ich z glukozą."
            )
        try:
            timestamp = epoch + timedelta(seconds=seconds)
        except OverflowError as exc:
            raise AnalysisError("fit_timestamps", "FIT zawiera nieprawidłowe daty.") from exc
        relative = (timestamp - start).total_seconds()
        if relative < 0 or (times and relative <= times[-1]):
            raise AnalysisError(
                "fit_timestamps", "Czasy próbek FIT są powtórzone lub nieuporządkowane. Wyeksportuj plik ponownie."
            )
        times.append(relative)
    return times


def _coverage(events: list[dict], duration: float) -> tuple[float, list[dict]]:
    """Coverage intervals are short numeric-to-numeric intervals, never flags."""
    intervals = []
    for previous, current in zip(events, events[1:]):
        if previous["value"] is None or current["value"] is None:
            continue
        delta = current["minute"] - previous["minute"]
        if 0 < delta <= 10:
            left = max(0.0, previous["minute"])
            right = min(duration, current["minute"])
            if right > left:
                intervals.append((left, right))
    merged: list[list[float]] = []
    for left, right in intervals:
        if merged and left <= merged[-1][1]:
            merged[-1][1] = max(right, merged[-1][1])
        else:
            merged.append([left, right])
    covered = sum(right - left for left, right in merged)
    gaps = []
    cursor = 0.0
    for left, right in merged:
        if left > cursor:
            gaps.append({"start": _rounded(cursor), "end": _rounded(left)})
        cursor = right
    if cursor < duration:
        gaps.append({"start": _rounded(cursor), "end": _rounded(duration)})
    return covered, gaps


def _segments(events: list[dict], duration: float) -> list[list[dict]]:
    segments: list[list[dict]] = []
    current: list[dict] = []
    previous_minute: float | None = None
    for event in events:
        minute = event["minute"]
        if minute < 0 or minute > duration:
            continue
        if event["value"] is None:
            if current:
                segments.append(current)
            current, previous_minute = [], None
            continue
        if previous_minute is not None and minute - previous_minute > 15:
            if current:
                segments.append(current)
            current = []
        current.append({"minute": _rounded(minute), "value": event["value"]})
        previous_minute = minute
    if current:
        segments.append(current)
    return segments


def _chart_samples(rows: list[dict], focus_minutes: list[float] | None = None) -> list[dict]:
    """Keep channel-missing boundaries and time gaps before uniform thinning."""
    expanded = []
    for index, row in enumerate(rows):
        if index and row["minute"] - rows[index - 1]["minute"] > 1:
            expanded.append({"minute": (row["minute"] + rows[index - 1]["minute"]) / 2,
                             "pace": None, "hr": None, "altitude": None, "distanceKm": None})
        expanded.append(row)
    if len(expanded) <= 600:
        return expanded
    mandatory = {0, len(expanded) - 1}
    for minute in focus_minutes or []:
        mandatory.add(min(range(len(expanded)), key=lambda index: abs(expanded[index]["minute"] - minute)))
    for index in range(1, len(expanded)):
        if any((expanded[index][key] is None) != (expanded[index - 1][key] is None)
               for key in ("pace", "hr", "altitude")):
            mandatory.update((index - 1, index))
    if len(mandatory) > 600:
        raise AnalysisError("fit_fragmented", "FIT zawiera zbyt wiele przerw. Wyeksportuj krótszy odcinek biegu.")
    budget = 600 - len(mandatory)
    remaining = [index for index in range(len(expanded)) if index not in mandatory]
    if budget:
        mandatory.update(remaining[round(i * (len(remaining) - 1) / max(1, budget - 1))] for i in range(budget))
    return [expanded[index] for index in sorted(mandatory)]


def _altitude_ascent(rows: list[dict]) -> float | None:
    """Positive changes in minute medians, within measured continuous segments.

    Minute binning reduces one-second altitude noise. Missing height samples and
    record gaps longer than 60 seconds terminate a segment: no change across that
    boundary is counted. None means no pair of usable minute bins exists.
    """
    segments: list[list[dict]] = []
    current: list[dict] = []
    for row in rows:
        if row["altitude"] is None:
            if current:
                segments.append(current)
            current = []
            continue
        if current and row["minute"] - current[-1]["minute"] > 1:
            segments.append(current)
            current = []
        current.append(row)
    if current:
        segments.append(current)
    ascent = 0.0
    has_pair = False
    for segment in segments:
        bins: dict[int, list[float]] = {}
        for row in segment:
            bins.setdefault(math.floor(row["minute"]), []).append(row["altitude"])
        heights = [median(values) for values in bins.values()]
        for previous, height in zip(heights, heights[1:]):
            has_pair = True
            ascent += max(0.0, height - previous)
    return round(ascent, 3) if has_pair else None


def analyze_upload(fit_bytes: bytes, csv_bytes: bytes, timezone_name: str = "Europe/Warsaw", synthetic: bool = False) -> dict:
    if not fit_bytes or len(fit_bytes) > 2 * 1024 * 1024:
        raise AnalysisError("fit_size", "FIT musi być niepusty i mieć najwyżej 2 MB.")
    try:
        zone = resolve_timezone(timezone_name)
        readings = parse_glucose_csv(csv_bytes, timezone_name)
    except GlucoseParseError as exc:
        raise AnalysisError(exc.code, exc.detail_pl) from exc
    try:
        activity = parse_fit_bytes(fit_bytes)
    except FitParseError as exc:
        raise AnalysisError(exc.code, "Nie można odczytać pojedynczego biegu z FIT. Wyeksportuj plik ponownie.") from exc
    except (ValueError, TypeError, OverflowError) as exc:
        raise AnalysisError("decode_failed", "Nie można odczytać FIT. Wyeksportuj plik ponownie.") from exc
    if not activity.get("is_run"):
        raise AnalysisError("not_running", "Ten FIT nie zawiera biegu. Wgraj pojedynczą aktywność biegową.")
    try:
        start = datetime.fromisoformat(activity["start_time_utc"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AnalysisError("fit_start", "FIT nie zawiera daty rozpoczęcia potrzebnej do połączenia danych.") from exc
    if start.tzinfo is None or not 2000 <= start.year <= 2100:
        raise AnalysisError("fit_start", "FIT zawiera nieprawidłową datę rozpoczęcia.")
    times = _record_times(fit_bytes, start)
    duration_seconds = max(times[-1], _number(activity.get("elapsed_time"), positive=True) or 0)
    if not 60 <= duration_seconds <= 12 * 60 * 60:
        raise AnalysisError("fit_duration", "Obsługujemy pojedynczy bieg trwający od 1 minuty do 12 godzin.")
    duration = duration_seconds / 60
    parsed_samples = activity.get("samples") or {}
    if parsed_samples.get("time_axis") != "timestamp" or len(parsed_samples.get("time_seconds", [])) != len(times):
        raise AnalysisError("fit_timestamps", "Nie można odtworzyć prawdziwej osi czasu FIT.")
    parsed_samples["time_seconds"] = times
    # Keep absence and invalid measurements unknown before imported adapter use.
    for key in ("heartrate", "velocity_ms", "altitude", "cadence", "distance_m"):
        values = parsed_samples.get(key) or []
        parsed_samples[key] = [_number(value, positive=key in ("heartrate", "cadence")) for value in values]
    streams = adapt_fit_activity_to_streams(activity)
    streams["pace_per_km"] = [pace if 2 <= pace <= 20 else None for pace in streams["pace_per_km"]]
    native_distance = streams.get("distance_m") or []
    distance_complete = bool(native_distance) and all(value is not None and value >= 0 for value in native_distance)
    if distance_complete and any(right < left for left, right in zip(native_distance, native_distance[1:])):
        raise AnalysisError("fit_distance", "Dystans w FIT cofa się. Wyeksportuj pojedynczy bieg ponownie.")
    distance_source = "FIT distance samples" if distance_complete else "unknown"
    distances = native_distance if native_distance else [None] * len(times)
    if not distance_complete and all(value is not None for value in streams["pace_per_km"]) and all(
        right - left <= 60 for left, right in zip(times, times[1:])
    ):
        distances = cumulative_distance_m(streams["pace_per_km"], times)
        distance_source = "estimated from measured speed and time"
    summary_distance = _number(activity.get("distance"), positive=True)
    if summary_distance is not None:
        total_distance = summary_distance / 1000
        total_distance_source = "FIT session summary"
    elif distances and distances[-1] is not None:
        total_distance = distances[-1] / 1000
        total_distance_source = distance_source
    else:
        total_distance, total_distance_source = None, "unknown"
    rows = [{"minute": round(t / 60, 4), "pace": _rounded(streams["pace_per_km"][index]),
             "hr": streams["heartrate"][index], "altitude": _rounded(streams["altitude"][index]),
             "distanceKm": _rounded(distances[index] / 1000) if distances[index] is not None else None}
            for index, t in enumerate(times)]
    events = [{"minute": (reading.timestamp - start).total_seconds() / 60,
               "value": reading.value, "flag": reading.flag} for reading in readings]
    # Retain nearby readings only for context windows, not global point counts.
    nearby = [event for event in events if -10 <= event["minute"] <= duration + 10]
    in_run = [event for event in nearby if 0 <= event["minute"] <= duration]
    if not in_run:
        raise AnalysisError("no_glucose_overlap", "Odczyty CSV nie pokrywają się z biegiem. Sprawdź datę i strefę czasową eksportu.")
    numeric = [event for event in in_run if event["value"] is not None]
    covered, gaps = _coverage(nearby, duration)
    # Internal max-HR default is demanded by imported API; omit zones/confidence.
    signals = extract_run_signals(streams, ProfileCtx(max_hr=190, max_hr_source="default"))
    registry: dict[str, dict] = {}

    def fact(identifier: str, value: Any, unit: str, description: str) -> str:
        registry[identifier] = {"value": value, "unit": unit, "description": description}
        return identifier

    average_values = [row["pace"] for row in rows if row["pace"] is not None]
    # Pace is elapsed duration per measured total distance; no invented average
    # if distance unavailable. Mean sampled pace is explicitly labelled fallback.
    average_pace = duration / total_distance if total_distance else (mean(average_values) if average_values else None)
    facts = {"coveragePct": round(100 * covered / duration), "coveredMinutes": round(covered, 3),
             "minGlucose": min((event["value"] for event in numeric), default=None),
             "below70Count": sum(event["value"] < 70 for event in numeric),
             "below54Count": sum(event["value"] < 54 for event in numeric), "readingCount": len(numeric),
             "averagePace": _rounded(average_pace), "belowRangeCount": sum(event["flag"] == "below_range" for event in in_run),
             "aboveRangeCount": sum(event["flag"] == "above_range" for event in in_run),
             "basis": "Liczba i minimum dotyczą odczytów punktowych podczas biegu. Pokrycie obejmuje przedziały między liczbowymi odczytami oddalonymi o najwyżej 10 minut, także tuż poza biegiem; przedziały przycięto do czasu biegu. Flagi Low/High nie są liczbami. Bez wyliczania czasu poniżej progu."}
    for key, unit in (("coveragePct", "%"), ("coveredMinutes", "min"), ("minGlucose", "mg/dL"),
                      ("below70Count", "readings"), ("below54Count", "readings"), ("readingCount", "readings"),
                      ("averagePace", "min/km"), ("belowRangeCount", "flags"), ("aboveRangeCount", "flags")):
        fact(f"run.{key}", facts[key], unit, f"Whole-run {key}; numeric readings only unless flag count")
    fact("run.duration", round(duration, 3), "min", "Elapsed time of the run, including pauses")
    fact("run.distance", _rounded(total_distance), "km", total_distance_source)
    candidates: list[tuple[float, str, Any]] = []
    low = min(numeric, key=lambda event: event["value"]) if numeric else None
    flagged = next((event for event in in_run if event["flag"] == "below_range"), None)
    if flagged or (low and low["value"] < 70):
        candidates.append(((flagged or low)["minute"], "glucose", None))
    if gaps:
        biggest = max(gaps, key=lambda gap: gap["end"] - gap["start"])
        if biggest["end"] - biggest["start"] >= 10:
            candidates.append(((biggest["start"] + biggest["end"]) / 2, "gap", None))
    for signal in sorted(signals.moments, key=lambda signal: ({"high": 0, "medium": 1, "low": 2}[signal.severity.value], signal.start_s)):
        minute = (signal.start_s + signal.end_s) / 120
        # Grade adjustment over the whole run is not a moment-specific uphill.
        if signal.type.value == "grade_adjustment":
            material = [(abs(raw - adjusted), index) for index, (raw, adjusted) in enumerate(zip(streams["pace_per_km"], signals.gap_pace_per_km))
                        if raw is not None and adjusted is not None]
            if material:
                minute = times[max(material)[1]] / 60
        candidates.append((min(duration, max(0, minute)), signal.type.value, signal))
    if not candidates:
        candidates.append((low["minute"] if low else duration / 2, "overview", None))
    selected = []
    for candidate in candidates:
        if all(abs(candidate[0] - existing[0]) >= 5 for existing in selected):
            selected.append(candidate)
        if len(selected) == 5:
            break
    selected.sort(key=lambda candidate: candidate[0])
    moments = []
    for ordinal, (minute, reason, signal) in enumerate(selected, 1):
        identifier = f"moment-{ordinal}"
        left, right = max(0, minute - 10), min(duration, minute + 10)
        window_events = [event for event in nearby if left <= event["minute"] <= right]
        window_numbers = [event["value"] for event in window_events if event["value"] is not None]
        minimum = min(window_numbers, default=None)
        window_rows = [row for row in rows if left <= row["minute"] <= right]
        nearest = min(rows, key=lambda row: abs(row["minute"] - minute))
        # Do not display an old watch reading as a current sample across a gap.
        if abs(nearest["minute"] - minute) > 1:
            nearest = {"pace": None, "hr": None, "distanceKm": None}
        altitude_rows = [row for row in window_rows if row["altitude"] is not None]
        altitude_change = (altitude_rows[-1]["altitude"] - altitude_rows[0]["altitude"]
                           if len(altitude_rows) >= 2 else None)
        altitude_ascent = _altitude_ascent(window_rows)
        altitude_partial = (
            len(altitude_rows) < len(window_rows) or len(altitude_rows) < 2
            or any(b["minute"] - a["minute"] > 1 for a, b in zip(window_rows, window_rows[1:]))
            or (bool(altitude_rows) and (altitude_rows[0]["minute"] - left > 1 or right - altitude_rows[-1]["minute"] > 1))
        )
        fact(f"{identifier}.glucose.minimum", minimum, "mg/dL", "Minimum numeric CGM reading in selected ±10 minute window")
        fact(f"{identifier}.glucose.count", len(window_numbers), "readings", "Numeric CGM point readings in selected window")
        fact(f"{identifier}.altitude.change", _rounded(altitude_change), "m", "Last minus first available altitude in selected window")
        fact(f"{identifier}.altitude.ascent", altitude_ascent, "m",
             "Accumulated positive changes between elapsed-minute median measured altitudes in selected window; missing altitude or record gaps longer than 60 seconds split segments; no changes counted across segment boundaries")
        fact(f"{identifier}.pace", nearest["pace"], "min/km", "Nearest measured pace, within one minute of selected moment")
        fact(f"{identifier}.hr", nearest["hr"], "bpm", "Nearest measured heart rate, within one minute of selected moment")
        fact(f"{identifier}.window.start", round(left, 3), "min", "Context window start, elapsed time from FIT session start")
        fact(f"{identifier}.window.end", round(right, 3), "min", "Context window end, elapsed time from FIT session start")
        # Minimized model input still contains patterns and their sample counts,
        # rather than only one instantaneous value. Means are sample-weighted;
        # no missing measurements are interpolated or carried forward.
        for half, half_rows in (("firstHalf", [row for row in window_rows if row["minute"] < minute]),
                                ("secondHalf", [row for row in window_rows if row["minute"] >= minute])):
            for channel, unit in (("pace", "min/km"), ("hr", "bpm")):
                values = [row[channel] for row in half_rows if row[channel] is not None]
                fact(f"{identifier}.{channel}.{half}.average", _rounded(mean(values)) if values else None,
                     unit, f"Sample-weighted {channel} mean in {half} of selected window; missing samples excluded")
                fact(f"{identifier}.{channel}.{half}.count", len(values), "samples",
                     f"Number of measured {channel} samples contributing to {half} average")
        numeric_events = [event for event in window_events if event["value"] is not None]
        first_glucose = numeric_events[0] if numeric_events else None
        last_glucose = numeric_events[-1] if numeric_events else None
        for edge, event in (("first", first_glucose), ("last", last_glucose)):
            fact(f"{identifier}.glucose.{edge}", event["value"] if event else None, "mg/dL",
                 f"{edge.capitalize()} numeric CGM point in selected window; no interpolation")
            fact(f"{identifier}.glucose.{edge}.minute", round(event["minute"], 3) if event else None, "min",
                 f"Timestamp of {edge} numeric CGM point, relative to FIT session start")
        glucose_delta = (last_glucose["value"] - first_glucose["value"] if len(numeric_events) >= 2 else None)
        fact(f"{identifier}.glucose.delta", _rounded(glucose_delta), "mg/dL",
             "Last minus first numeric CGM point in selected window; endpoint change, not a continuous curve or cause")
        baseline_rows = [row for row in rows if max(0, minute - 5) <= row["minute"] < minute]
        baseline_values = [row["pace"] for row in baseline_rows if row["pace"] is not None]
        baseline = mean(baseline_values) if baseline_values else None
        pace_delta = nearest["pace"] - baseline if nearest["pace"] is not None and baseline is not None else None
        fact(f"{identifier}.pace.baseline.average", _rounded(baseline), "min/km",
             "Sample-weighted measured pace mean in preceding 5 minutes; missing samples excluded")
        fact(f"{identifier}.pace.baseline.count", len(baseline_values), "samples", "Measured pace samples in preceding 5 minutes")
        fact(f"{identifier}.pace.changeVsBaseline", _rounded(pace_delta), "min/km",
             "Current measured pace minus preceding 5-minute measured sample mean; positive means slower")
        fact(f"{identifier}.pace.changeVsBaselinePct", _rounded(100 * pace_delta / baseline) if pace_delta is not None else None,
             "%", "Current measured pace change versus preceding 5-minute measured sample mean; no causal attribution")
        fact(f"{identifier}.altitude.count", len(altitude_rows), "samples", "Available measured altitude samples in selected window")
        fact(f"{identifier}.altitude.partial", "yes" if altitude_partial else "no", "coverage flag",
             "Whether height samples or timestamp coverage are incomplete in selected window")
        factors = []
        unknowns = ["Odczyt sensora i zmiana tempa nie dowodzą przyczyny.", "Brak informacji o posiłku.", "Nie zapisano odczuć biegacza."]
        if not window_numbers:
            factors.append({"id": "no_glucose_data", "label": "Brak liczbowych odczytów glukozy", "evidence": "W wybranym oknie nie ma liczbowych odczytów EGV.", "factId": f"{identifier}.glucose.count"})
            unknowns.insert(0, "Brak liczbowych odczytów glukozy w wybranym oknie.")
        if minimum is not None and minimum < 70:
            factors.append({"id": "low_glucose_nearby", "label": "Odczyt glukozy poniżej 70", "evidence": f"Najniższy odczyt w oknie: {minimum:g} mg/dL.", "factId": f"{identifier}.glucose.minimum"})
        flag_count = sum(event["flag"] == "below_range" for event in window_events)
        fact(f"{identifier}.glucose.belowRangeCount", flag_count, "flags", "Below-range CGM flags in selected window; not numeric readings")
        if flag_count:
            factors.append({"id": "below_range", "label": "Flaga Low", "evidence": "Sensor oznaczył odczyt jako Low; brak dokładnej liczby.", "factId": f"{identifier}.glucose.belowRangeCount"})
        if altitude_ascent is not None and altitude_ascent >= 10:
            factors.append({"id": "uphill", "label": "Podbieg w oknie", "evidence": f"Mierzony wzrost wysokości w oknie: {altitude_ascent:g} m; liczony między medianami minutowymi, bez łączenia przerw.", "factId": f"{identifier}.altitude.ascent"})
        if signal is not None:
            neutral_labels = {"cliff": "Zmiana tempa", "positive_split": "Wolniejsza druga część", "decoupling": "Zmiana relacji tętna i tempa", "cadence_decay": "Zmiana kadencji", "grade_adjustment": "Tempo i teren"}
            # Store numeric evidence from the approved detector without diagnostic labels.
            evidence_ids = []
            for key, value in signal.evidence.items():
                if isinstance(value, (int, float)) and math.isfinite(value):
                    evidence_ids.append(fact(f"{identifier}.signal.{key}", value, "detector metric", f"Run signal {signal.type.value}: {key}"))
            if evidence_ids and reason != "grade_adjustment":
                factors.append({"id": reason, "label": neutral_labels.get(reason, "Zmiana w biegu"), "evidence": "Wskaźnik zmiany obliczony z pomiarów zegarka; nie wskazuje przyczyny.", "factId": evidence_ids[0]})
        if altitude_change is None:
            unknowns.append("Brak wystarczających pomiarów wysokości do porównania terenu.")
        elif altitude_partial:
            unknowns.append("Pomiary wysokości obejmują tylko część okna. Nie znamy pełnego przebiegu terenu i nie możemy rozdzielić jego wpływu.")
        if any(b["minute"] - a["minute"] > 15 or a["value"] is None or b["value"] is None
               for a, b in zip(window_events, window_events[1:])):
            unknowns.append("Zmiana między pierwszym i ostatnim odczytem nie opisuje glukozy w lukach ani poza zakresem sensora.")
        if nearest["hr"] is None:
            unknowns.append("Brak pomiaru tętna w tym momencie.")
        if nearest["pace"] is None:
            unknowns.append("Brak pomiaru tempa w tym momencie.")
        has_low = (minimum is not None and minimum < 70) or bool(flag_count)
        uphill = altitude_ascent is not None and altitude_ascent >= 10
        if not window_numbers and not flag_count:
            label, title = "Luka w danych", "Tutaj historia jest niepełna."
            narrative = "Nie mamy liczbowych odczytów glukozy w tym oknie. Nie można porównać ich z przebiegiem biegu."
        elif has_low and uphill:
            label, title = "Dwa sygnały", "Niższy odczyt glukozy i wzrost wysokości w jednym oknie."
            narrative = "W tym oknie występują niższe odczyty glukozy oraz wzrost wysokości. Dane nie pozwalają rozdzielić ich wpływu ani potwierdzić przyczyny zmiany tempa."
        elif has_low:
            label, title = "Odczyt do omówienia", "Niższy odczyt glukozy w kontekście biegu."
            narrative = "W oknie wokół tego momentu wystąpił niższy odczyt lub flaga Low. To obserwacja z sensora, bez rozpoznania przyczyny ani zalecenia leczenia."
        elif reason == "gap":
            label, title = "Luka w danych", "W pobliżu są odczyty, ale pomiędzy nimi brakuje danych."
            narrative = "Pojedyncze odczyty w oknie nie uzupełniają przerwy. Nie przypisujemy glukozy do każdej sekundy biegu."
        elif signal is not None:
            label, title = "Zmiana w biegu", "Warto porównać sygnały z tego odcinka."
            narrative = "Pomiary zegarka wskazały zmianę. Odczyty glukozy i teren są pokazane obok; ich współwystępowanie nie dowodzi przyczyny."
        else:
            label, title = "Przegląd odcinka", "Ten odcinek łączy oba źródła."
            narrative = "W tym oknie są odczyty glukozy i pomiary biegu. Pokazujemy obserwacje bez orzekania, co spowodowało zmianę."
        moments.append({"id": identifier, "minute": round(minute, 3), "label": label, "title": title,
                        "distanceKm": nearest["distanceKm"], "windowStart": round(left, 3), "windowEnd": round(right, 3),
                        "minGlucose": minimum, "readingCount": len(window_numbers), "pace": nearest["pace"], "hr": nearest["hr"],
                        "altitudeChange": _rounded(altitude_change), "altitudeAscent": altitude_ascent, "factors": factors, "narrative": narrative,
                        "unknowns": unknowns, "question": "Jak omówić te odczyty w kontekście wysiłku i ograniczeń sensora?",
                        "separable": not (has_low and uphill) and not altitude_partial})
    strengths = []
    for strength in signals.strengths:
        label = {"negative_split": "Druga część biegu miała szybsze tempo.", "even_pacing": "Średnie tempo obu części biegu było zbliżone.",
                 "cardiac_steady": "Wskaźnik relacji tętna i tempa nie wykazał dużej zmiany.", "cadence_stable": "Kadencja pozostała względnie równa.",
                 "strong_finish": "Końcowy odcinek miał szybsze tempo niż środkowy."}.get(strength.type.value)
        if label:
            strengths.append(label)
    warnings = []
    if any(reading.source_unit == "mmol/L" for reading in readings):
        warnings.append("Glukozę przeliczono z mmol/L na mg/dL współczynnikiem 18,0182.")
    if distance_source == "estimated from measured speed and time":
        warnings.append("Pozycję na trasie oszacowano z pomiarów prędkości i czasu; nie użyto GPS.")
    if any(gap["end"] - gap["start"] > 1 for gap in gaps):
        warnings.append("Glukoza nie obejmuje całego biegu. Luki pozostały widoczne.")
    if not strengths:
        strengths.append("Połączono czas zegarka i sensora bez uzupełniania brakujących pomiarów.")
    return {"schemaVersion": 1, "synthetic": bool(synthetic), "title": "Bieg demonstracyjny" if synthetic else "Twój wgrany bieg",
            "date": start.astimezone(zone).date().isoformat(), "start": start.astimezone(zone).isoformat(), "timezone": timezone_name,
            "durationMinutes": round(duration, 3), "distanceKm": _rounded(total_distance), "samples": _chart_samples(rows, [moment["minute"] for moment in moments]),
            "glucose": [{"minute": _rounded(event["minute"]), "value": event["value"]} for event in numeric],
            "glucoseFlags": [{"minute": _rounded(event["minute"]), "flag": event["flag"]} for event in in_run if event["flag"]],
            "glucoseSegments": _segments(nearby, duration), "gaps": gaps, "moments": moments, "facts": facts,
            "provenance": {"kind": "synthetic" if synthetic else "uploaded", "engineUsed": True, "clinicalValidation": False,
                           "distanceSource": distance_source, "totalDistanceSource": total_distance_source,
                           "glucoseSource": "Dexcom-style CSV EGV", "timestampBasis": "FIT UTC timestamps + declared CSV timezone"},
            "factRegistry": registry, "strengths": strengths, "warnings": warnings}
