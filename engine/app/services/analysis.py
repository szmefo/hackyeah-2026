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


_WINDOW_MINUTES = 10
_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
_SIGNAL_LABELS = {"cliff": "Zwolnienie tempa", "positive_split": "Wolniejsza druga część",
                  "decoupling": "Zmiana relacji tętna i tempa", "cadence_decay": "Zmiana kadencji",
                  "grade_adjustment": "Tempo i teren"}
# Plain sentences about the run itself; no zone or %HRmax vocabulary.
_STRENGTH_SENTENCES = {
    "negative_split": "Druga połowa biegu była szybsza od pierwszej: siły rozłożone tak, że starczyło ich na końcówkę.",
    "even_pacing": "Obie połowy biegu miały bardzo podobne tempo: równy, kontrolowany wysiłek od startu do mety.",
    "cardiac_steady": "Tętno nie rosło wyraźnie przy tym samym tempie aż do końca biegu: wysiłek był stabilny.",
    "cadence_stable": "Rytm kroków utrzymał się do końca biegu bez wyraźnego spadku.",
    "strong_finish": "Końcówka była szybsza niż środek biegu: mocny finisz.",
}


def _describe(context: dict, kinds: set[str], signal_kinds: set[str], terrain_unknown: bool) -> tuple[str, str, str, str]:
    """Deterministic label, title, narrative and question for one moment.

    Wording states co-occurrence only. The title names what anchors this moment
    (the lowest reading, a Low flag, a slowdown, a sensor gap) so two moments
    in one run never read the same.
    """
    state, uphill = context["glucoseState"], context["uphill"]
    slowdown = "cliff" in signal_kinds
    anchored_low = "lowest" in kinds or "low_flag" in kinds
    low_anchor = ("Odczyt oznaczony przez sensor jako Low" if "low_flag" in kinds
                  else "Najniższy odczyt glukozy w biegu")
    pace_clause = ", a tempo spadło" if slowdown else ""
    pace_and = " i tempo spadło" if slowdown else ""
    numeric_low = context["minimum"] is not None and context["minimum"] < 70
    low_text = ("odczyt glukozy poniżej 70 mg/dL i flaga Low" if numeric_low and context["lowFlags"]
                else "flaga Low z sensora" if context["lowFlags"] else "odczyt glukozy poniżej 70 mg/dL")
    if state == "missing":
        label = "Luka w danych"
        if uphill and slowdown:
            title = "Zwolnienie na podbiegu bez odczytów glukozy."
        elif uphill:
            title = "Podbieg w czasie przerwy w odczytach sensora."
        elif slowdown:
            title = "Zwolnienie tempa w czasie przerwy w odczytach sensora."
        else:
            title = "Przerwa w odczytach sensora."
        terrain = " W tym czasie teren się wznosił" + pace_and + "." if uphill else (
            " W tym czasie tempo spadło." if slowdown else "")
        narrative = ("Sensor nie zapisał w tym oknie żadnego liczbowego odczytu glukozy." + terrain +
                     " Nie wiemy, jaka była wtedy glukoza, więc tego odcinka nie da się z nią porównać"
                     " ani oddzielić jej możliwego udziału od innych czynników.")
        question = "Jak ograniczyć przerwy w odczytach sensora podczas biegu i jak traktować takie luki?"
    elif state == "low" and uphill:
        label = "Dwa sygnały"
        if anchored_low:
            title = low_anchor + ", w tym samym oknie co podbieg."
        elif slowdown:
            title = "Zwolnienie na podbiegu przy niskim odczycie glukozy."
        else:
            title = "Niski odczyt glukozy i podbieg w jednym oknie."
        narrative = ("W tym oknie jednocześnie wystąpił " + low_text +
                     " oraz wzrost wysokości" + pace_clause + ". Oba sygnały wystąpiły razem, więc dane"
                     " nie pozwalają rozdzielić ich wpływu ani wskazać przyczyny zmiany tempa.")
        question = "Jak odróżnić spadek glukozy od zmęczenia na podbiegu, gdy wystąpiły w tym samym czasie?"
    elif state == "low":
        label = "Odczyt do omówienia"
        flat = not terrain_unknown
        if anchored_low:
            title = low_anchor + (", bez podbiegu w oknie." if flat else ".")
        elif slowdown:
            title = "Zwolnienie tempa przy niskim odczycie glukozy" + (" bez podbiegu w oknie." if flat else ".")
        else:
            title = "Niski odczyt glukozy w kontekście biegu."
        terrain = (" Nie było tu podbiegu, więc teren nie współwystępował z tym odczytem." if flat else
                   " Pomiary wysokości są niepełne, więc nie wiadomo, jak zmieniał się teren.")
        narrative = ("W tym oknie wystąpił " + low_text + pace_clause + "." +
                     terrain + " To obserwacja z sensora, bez rozpoznania przyczyny ani zalecenia leczenia.")
        question = "Jak omówić ten niski odczyt w kontekście wysiłku i ograniczeń sensora?"
    elif state == "high":
        label = "Dwa sygnały" if uphill else "Odczyt do omówienia"
        title = ("Wysoki odczyt glukozy i podbieg w jednym oknie." if uphill
                 else "Wysoki odczyt glukozy w kontekście biegu.")
        numeric_high = context["maximum"] is not None and context["maximum"] > 180
        high_text = ("odczyt glukozy powyżej 180 mg/dL i flaga High" if numeric_high and context["highFlags"]
                     else "flaga High z sensora" if context["highFlags"] else "odczyt glukozy powyżej 180 mg/dL")
        narrative = ("W tym oknie wystąpił " + high_text +
                     (" oraz wzrost wysokości" + pace_clause + ". Dane nie pozwalają rozdzielić ich wpływu."
                      if uphill else pace_clause + ". To obserwacja z sensora, bez rozpoznania przyczyny.")
                     )
        question = "Jak omówić ten wysoki odczyt w kontekście wysiłku i ograniczeń sensora?"
    elif state == "partial":
        label = "Niepełne dane"
        title = ("Podbieg przy niepełnych odczytach glukozy." if uphill
                 else "Odczyty glukozy z przerwą w tym oknie.")
        terrain = (", a teren się wznosił" + pace_and) if uphill else pace_clause
        narrative = ("W części okna brakuje odczytów sensora" + terrain + ". Dostępne odczyty nie uzupełniają"
                     " przerwy, więc nie wiadomo, jaka była"
                     " glukoza przez cały ten odcinek, i nie da się oddzielić jej możliwego udziału.")
        question = "Jak traktować przerwy w odczytach sensora przy omawianiu wysiłku?"
    elif uphill:
        label = "Podbieg, glukoza w zakresie"
        title = ("Zwolnienie na podbiegu, glukoza w zakresie." if slowdown
                 else "Podbieg przy glukozie w zakresie.")
        narrative = ("W tym oknie teren się wznosił" + pace_and + ", a wszystkie odczyty glukozy mieściły się"
                     " w zakresie 70–180 mg/dL. W danych widać podbieg, nie spadek glukozy. To współwystępowanie,"
                     " nie dowód przyczyny.")
        question = "Czy takie zwolnienie przy glukozie w zakresie warto omawiać w kontekście cukrzycy?"
    elif signal_kinds:
        label = "Zmiana w biegu"
        title = ("Zwolnienie tempa przy glukozie w zakresie." if slowdown
                 else "Zmiana w biegu przy glukozie w zakresie.")
        terrain = "" if terrain_unknown else " W tym oknie nie było podbiegu."
        narrative = ("Pomiary zegarka wskazały zmianę, a wszystkie odczyty glukozy w oknie mieściły się"
                     " w zakresie 70–180 mg/dL." + terrain + " Ich współwystępowanie nie dowodzi przyczyny.")
        question = "Jak omówić tę zmianę w biegu przy glukozie w zakresie?"
    else:
        label = "Przegląd odcinka"
        title = "Ten odcinek łączy oba źródła."
        narrative = ("W tym oknie są odczyty glukozy w zakresie 70–180 mg/dL i pomiary biegu."
                     " Pokazujemy obserwacje bez orzekania, co spowodowało zmianę.")
        question = "Jak omówić te odczyty w kontekście wysiłku i ograniczeń sensora?"
    return label, title, narrative, question


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
        # Name both time ranges so the user can see which export to pick.
        fmt = "%d.%m.%Y %H:%M"
        local = [reading.timestamp.astimezone(zone) for reading in readings]
        span = (f" Bieg: {start.astimezone(zone).strftime(fmt)}–"
                f"{(start + timedelta(minutes=duration)).astimezone(zone).strftime('%H:%M')}."
                + (f" Odczyty w CSV: {min(local).strftime(fmt)}–{max(local).strftime(fmt)} ({timezone_name})."
                   if local else ""))
        raise AnalysisError("no_glucose_overlap", "Odczyty CSV nie pokrywają się z biegiem." + span +
                            " Wyeksportuj CSV z dnia biegu albo sprawdź strefę czasową eksportu.")
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
    low = min(numeric, key=lambda event: event["value"]) if numeric else None
    flagged = next((event for event in in_run if event["flag"] == "below_range"), None)
    point_signals: list[tuple[float, Any]] = []
    long_signals: list[tuple[float, Any]] = []
    for signal in sorted(signals.moments, key=lambda signal: (_SEVERITY_RANK[signal.severity.value], signal.start_s)):
        minute = (signal.start_s + signal.end_s) / 120
        # Grade adjustment over the whole run is not a moment-specific uphill.
        if signal.type.value == "grade_adjustment":
            material = [(abs(raw - adjusted), index) for index, (raw, adjusted) in enumerate(zip(streams["pace_per_km"], signals.gap_pace_per_km))
                        if raw is not None and adjusted is not None]
            if material:
                minute = times[max(material)[1]] / 60
            point_signals.append((min(duration, max(0, minute)), signal))
        elif (signal.end_s - signal.start_s) / 60 > 2 * _WINDOW_MINUTES:
            # A pattern spanning half the run has no single moment: its midpoint
            # would be an arbitrary anchor duplicating real moments nearby.
            long_signals.append((min(duration, max(0, minute)), signal))
        else:
            point_signals.append((min(duration, max(0, minute)), signal))
    # Priority order: a low reading, the largest CGM gap, short watch events.
    candidates: list[dict] = []
    if flagged or (low and low["value"] < 70):
        candidates.append({"minute": (flagged or low)["minute"], "kinds": {"low_flag" if flagged else "lowest"}, "signals": []})
    if gaps:
        biggest = max(gaps, key=lambda gap: gap["end"] - gap["start"])
        if biggest["end"] - biggest["start"] >= 10:
            candidates.append({"minute": (biggest["start"] + biggest["end"]) / 2, "kinds": {"gap"}, "signals": []})
    for minute, signal in point_signals:
        candidates.append({"minute": minute, "kinds": {"signal"}, "signals": [signal]})
    if not candidates:
        for minute, signal in long_signals:
            candidates.append({"minute": minute, "kinds": {"signal"}, "signals": [signal]})
    if not candidates:
        candidates.append({"minute": low["minute"] if low else duration / 2, "kinds": {"overview"}, "signals": []})

    def window(minute: float) -> dict:
        """Measured context of one ±10 min window, used for selection and story."""
        left, right = max(0, minute - _WINDOW_MINUTES), min(duration, minute + _WINDOW_MINUTES)
        window_events = [event for event in nearby if left <= event["minute"] <= right]
        window_numbers = [event["value"] for event in window_events if event["value"] is not None]
        window_rows = [row for row in rows if left <= row["minute"] <= right]
        altitude_rows = [row for row in window_rows if row["altitude"] is not None]
        ascent = _altitude_ascent(window_rows)
        altitude_partial = (
            len(altitude_rows) < len(window_rows) or len(altitude_rows) < 2
            or any(b["minute"] - a["minute"] > 1 for a, b in zip(window_rows, window_rows[1:]))
            or (bool(altitude_rows) and (altitude_rows[0]["minute"] - left > 1 or right - altitude_rows[-1]["minute"] > 1))
        )
        low_flags = sum(event["flag"] == "below_range" for event in window_events)
        high_flags = sum(event["flag"] == "above_range" for event in window_events)
        minimum, maximum = min(window_numbers, default=None), max(window_numbers, default=None)
        missing_minutes = sum(max(0.0, min(right, gap["end"]) - max(left, gap["start"])) for gap in gaps)
        has_low = (minimum is not None and minimum < 70) or bool(low_flags)
        has_high = (maximum is not None and maximum > 180) or bool(high_flags)
        if not window_numbers and not low_flags and not high_flags:
            glucose_state = "missing"
        elif has_low:
            glucose_state = "low"
        elif has_high:
            glucose_state = "high"
        elif missing_minutes > 1:
            glucose_state = "partial"
        else:
            glucose_state = "in_range"
        return {"left": left, "right": right, "events": window_events, "numbers": window_numbers, "rows": window_rows,
                "altitudeRows": altitude_rows, "ascent": ascent, "altitudePartial": altitude_partial,
                "minimum": minimum, "maximum": maximum, "lowFlags": low_flags, "highFlags": high_flags,
                "glucosePartial": missing_minutes > 1, "glucoseState": glucose_state,
                "hasLow": has_low, "hasHigh": has_high, "uphill": ascent is not None and ascent >= 10}

    def story_key(context: dict) -> tuple[str, bool]:
        return context["glucoseState"], context["uphill"]

    def specificity(kinds: set[str]) -> int:
        return min({"low_flag": 0, "lowest": 0, "signal": 1, "gap": 2, "overview": 3}[kind] for kind in kinds)

    selected: list[dict] = []
    for candidate in candidates:
        if all(abs(candidate["minute"] - existing["minute"]) >= 5 for existing in selected):
            selected.append(dict(candidate, kinds=set(candidate["kinds"]), signals=list(candidate["signals"])))
        if len(selected) == 5:
            break
    # Windows overlapping by at least half with the same glucose/terrain story
    # describe one moment twice: keep the most specific anchor, merge evidence.
    kept: list[dict] = []
    for candidate in selected:
        candidate["context"] = window(candidate["minute"])
        twin = next((item for item in kept if abs(item["minute"] - candidate["minute"]) <= _WINDOW_MINUTES
                     and story_key(item["context"]) == story_key(candidate["context"])), None)
        if twin is None:
            kept.append(candidate)
            continue
        if specificity(candidate["kinds"]) < specificity(twin["kinds"]):
            twin["minute"], twin["context"] = candidate["minute"], candidate["context"]
        twin["kinds"] |= candidate["kinds"]
        twin["signals"] += candidate["signals"]
    deduped: list[dict] = []
    for candidate in kept:
        if all(abs(candidate["minute"] - existing["minute"]) >= 5 for existing in deduped):
            deduped.append(candidate)
    deduped.sort(key=lambda candidate: candidate["minute"])
    moments = []
    used_titles: set[str] = set()
    for ordinal, candidate in enumerate(deduped, 1):
        identifier = f"moment-{ordinal}"
        minute, context = candidate["minute"], candidate["context"]
        left, right = context["left"], context["right"]
        window_events, window_numbers, window_rows = context["events"], context["numbers"], context["rows"]
        altitude_rows, altitude_ascent, altitude_partial = context["altitudeRows"], context["ascent"], context["altitudePartial"]
        minimum, maximum = context["minimum"], context["maximum"]
        nearest = min(rows, key=lambda row: abs(row["minute"] - minute))
        # Do not display an old watch reading as a current sample across a gap.
        if abs(nearest["minute"] - minute) > 1:
            nearest = {"pace": None, "hr": None, "distanceKm": None}
        altitude_change = (altitude_rows[-1]["altitude"] - altitude_rows[0]["altitude"]
                           if len(altitude_rows) >= 2 else None)
        fact(f"{identifier}.glucose.minimum", minimum, "mg/dL", "Minimum numeric CGM reading in selected ±10 minute window")
        fact(f"{identifier}.glucose.maximum", maximum, "mg/dL", "Maximum numeric CGM reading in selected ±10 minute window")
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
        fact(f"{identifier}.glucose.partial", "yes" if context["glucosePartial"] else "no", "coverage flag",
             "Whether the selected window contains more than one minute without numeric CGM coverage")
        factors = []
        unknowns = ["Odczyt sensora i zmiana tempa nie dowodzą przyczyny.", "Brak informacji o posiłku.", "Nie zapisano odczuć biegacza."]
        if not window_numbers:
            factors.append({"id": "no_glucose_data", "label": "Brak liczbowych odczytów glukozy", "evidence": "W wybranym oknie nie ma liczbowych odczytów EGV.", "factId": f"{identifier}.glucose.count"})
            unknowns.insert(0, "Brak liczbowych odczytów glukozy w wybranym oknie.")
        if minimum is not None and minimum < 70:
            factors.append({"id": "low_glucose_nearby", "label": "Odczyt glukozy poniżej 70", "evidence": f"Najniższy odczyt w oknie: {minimum:g} mg/dL.", "factId": f"{identifier}.glucose.minimum"})
        fact(f"{identifier}.glucose.belowRangeCount", context["lowFlags"], "flags", "Below-range CGM flags in selected window; not numeric readings")
        fact(f"{identifier}.glucose.aboveRangeCount", context["highFlags"], "flags", "Above-range CGM flags in selected window; not numeric readings")
        if context["lowFlags"]:
            factors.append({"id": "below_range", "label": "Flaga Low", "evidence": "Sensor oznaczył odczyt jako Low; brak dokładnej liczby.", "factId": f"{identifier}.glucose.belowRangeCount"})
        if maximum is not None and maximum > 180:
            factors.append({"id": "high_glucose_nearby", "label": "Odczyt glukozy powyżej 180", "evidence": f"Najwyższy odczyt w oknie: {maximum:g} mg/dL.", "factId": f"{identifier}.glucose.maximum"})
        if context["highFlags"]:
            factors.append({"id": "above_range", "label": "Flaga High", "evidence": "Sensor oznaczył odczyt jako High; brak dokładnej liczby.", "factId": f"{identifier}.glucose.aboveRangeCount"})
        if context["uphill"]:
            factors.append({"id": "uphill", "label": "Podbieg w oknie", "evidence": f"Mierzony wzrost wysokości w oknie: {altitude_ascent:g} m; liczony między medianami minutowymi, bez łączenia przerw.", "factId": f"{identifier}.altitude.ascent"})
        # Short watch events overlapping this window belong to it as well, one
        # per type (nearest to the anchor). Half-run patterns only when anchor.
        attached: dict[str, tuple[float, Any]] = {}
        overlapping = [signal for _, signal in point_signals if signal.start_s / 60 <= right and signal.end_s / 60 >= left]
        for signal in candidate["signals"] + overlapping:
            kind = signal.type.value
            distance = abs((signal.start_s + signal.end_s) / 120 - minute)
            if kind not in attached or distance < attached[kind][0]:
                attached[kind] = (distance, signal)
        signal_kinds = set()
        for kind, (_, signal) in sorted(attached.items()):
            # Store numeric evidence from the approved detector without diagnostic labels.
            evidence_ids = [fact(f"{identifier}.signal.{kind}.{key}", value, "detector metric", f"Run signal {kind}: {key}")
                            for key, value in signal.evidence.items()
                            if isinstance(value, (int, float)) and math.isfinite(value)]
            fact(f"{identifier}.signal.{kind}.start", round(signal.start_s / 60, 3), "min", f"Run signal {kind}: start of detected span")
            fact(f"{identifier}.signal.{kind}.end", round(signal.end_s / 60, 3), "min", f"Run signal {kind}: end of detected span")
            if evidence_ids and kind != "grade_adjustment":
                signal_kinds.add(kind)
                factors.append({"id": kind, "label": _SIGNAL_LABELS.get(kind, "Zmiana w biegu"), "evidence": "Wskaźnik zmiany obliczony z pomiarów zegarka; nie wskazuje przyczyny.", "factId": evidence_ids[0]})
        if altitude_change is None:
            unknowns.append("Brak wystarczających pomiarów wysokości do porównania terenu.")
        elif altitude_partial:
            unknowns.append("Pomiary wysokości obejmują tylko część okna. Nie znamy pełnego przebiegu terenu i nie możemy rozdzielić jego wpływu.")
        if context["glucosePartial"] and window_numbers:
            unknowns.append("W części okna brakuje odczytów glukozy. Nie wiemy, jaka była glukoza w tej przerwie.")
        if any(b["minute"] - a["minute"] > 15 or a["value"] is None or b["value"] is None
               for a, b in zip(window_events, window_events[1:])):
            unknowns.append("Zmiana między pierwszym i ostatnim odczytem nie opisuje glukozy w lukach ani poza zakresem sensora.")
        if nearest["hr"] is None:
            unknowns.append("Brak pomiaru tętna w tym momencie.")
        if nearest["pace"] is None:
            unknowns.append("Brak pomiaru tempa w tym momencie.")
        # separable answers: do the data allow telling apart the influence of
        # co-occurring factors? Only if glucose and terrain were both fully
        # measured in the window and they do not point at the same stretch.
        separable = (context["glucoseState"] in ("low", "high", "in_range") and not context["glucosePartial"]
                     and not altitude_partial and not ((context["hasLow"] or context["hasHigh"]) and context["uphill"]))
        if not separable:
            unknowns.append("Dane nie pozwalają rozdzielić wpływu współwystępujących czynników.")
        label, title, narrative, question = _describe(context, candidate["kinds"], signal_kinds,
                                                      altitude_partial or altitude_change is None)
        if title in used_titles:
            title = "Ponownie: " + title[0].lower() + title[1:]
        used_titles.add(title)
        moments.append({"id": identifier, "minute": round(minute, 3), "label": label, "title": title,
                        "distanceKm": nearest["distanceKm"], "windowStart": round(left, 3), "windowEnd": round(right, 3),
                        "minGlucose": minimum, "readingCount": len(window_numbers), "pace": nearest["pace"], "hr": nearest["hr"],
                        "altitudeChange": _rounded(altitude_change), "altitudeAscent": altitude_ascent, "factors": factors, "narrative": narrative,
                        "unknowns": unknowns, "question": question, "separable": separable})
    strengths = list(dict.fromkeys(_STRENGTH_SENTENCES[strength.type.value] for strength in signals.strengths
                                   if strength.type.value in _STRENGTH_SENTENCES))
    # Neutral observation, not praise: only when CGM covered the whole run.
    if numeric and not any(gap["end"] - gap["start"] > 1 for gap in gaps) and facts["below70Count"] == 0 \
            and facts["belowRangeCount"] == 0:
        strengths.append("Odczyty sensora objęły cały bieg i żaden z nich nie był niższy niż 70 mg/dL.")
    warnings = []
    if any(reading.source_unit == "mmol/L" for reading in readings):
        warnings.append("Glukozę przeliczono z mmol/L na mg/dL współczynnikiem 18,0182.")
    if distance_source == "estimated from measured speed and time":
        warnings.append("Pozycję na trasie oszacowano z pomiarów prędkości i czasu; nie użyto GPS.")
    if any(gap["end"] - gap["start"] > 1 for gap in gaps):
        warnings.append("Glukoza nie obejmuje całego biegu. Luki pozostały widoczne.")
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
