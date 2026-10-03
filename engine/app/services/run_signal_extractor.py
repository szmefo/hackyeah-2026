"""Pure run-signal extractor (#A) — zero DB, zero Anthropic.

This module is the single source of truth for per-run physiological signal
extraction. It takes raw Strava streams + a lightweight ``ProfileCtx`` and emits
typed ``RunSignals`` (a list of ``Moment`` events plus aggregate metrics).

Design contract (ADR 2026-06-02 §"Module boundary (#A)"):
  * NO imports from ``app.models`` / DB / SQLAlchemy.
  * NO imports from ``anthropic`` / LLM layer.
  * Caller resolves ``max_hr`` and passes it in ``ProfileCtx`` (the extractor
    never reads the DB to discover it — see ADR §max_hr resolution).

Because it is pure, this module can be built and tested in parallel with the
UUID auth migration: it touches no shared table.

The legacy dict-returning ``detect_pace_drop_summary`` and the ``zone_1..5``
``calculate_hr_zones_legacy`` live here too — they are the original
``training_analyzer`` helpers moved verbatim so the LLM call-sites
(``training_analyzer``, ``managed_agent_training``) keep their existing
behaviour while the typed engine (``Moment`` / ``RunSignals``) becomes the new
primary contract.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Pace sanity bounds (#87, 2026-05-07)
# ---------------------------------------------------------------------------
# Strava `pace_per_km` stream contains GPS-pause artefacts — values can spike
# to 8000+ min/km when the athlete stops moving. Every aggregation clips outside
# this band first, so the Generator never sees impossible values.
PACE_MIN_VALID = 2.0   # min/km — sub-2:00 is faster than the world record
PACE_MAX_VALID = 20.0  # min/km — anything slower is walking/standing, not running

# Detection thresholds v1 (ADR §"Decyzje Grega — ROZSTRZYGNIĘTE", 2026-06-02).
# Start values to tune against real data.
DECOUPLING_THRESHOLD = 0.05          # >5% HR/pace efficiency drift
POSITIVE_SPLIT_THRESHOLD = 0.05      # >5% slower 2nd half
CLIFF_THRESHOLD_PCT = 15.0           # >15% over baseline (computed on GAP)
CADENCE_DECAY_THRESHOLD = -1.5       # spm per 10 minutes
GRADE_ADJUSTMENT_MATERIAL_PCT = 0.10  # >10% raw vs GAP delta = informational moment
SHORT_STREAM_DURATION_S = 600        # < 10 min → low confidence


# ---------------------------------------------------------------------------
# Typed shapes (Pydantic boundary contract — never bare dict)
# ---------------------------------------------------------------------------


class MomentType(str, Enum):
    """The kinds of physiological events the extractor can flag.

    These are the *problem-centric* moments (something that cost the athlete).
    Things that went WELL live on the separate ``StrengthType`` ladder so the
    problem timeline stays honest and a good run still gets a "co poszło dobrze".
    """

    DECOUPLING = "decoupling"
    CLIFF = "cliff"                  # bonk / sustained pace collapse
    POSITIVE_SPLIT = "positive_split"
    GRADE_ADJUSTMENT = "grade_adjustment"
    CADENCE_DECAY = "cadence_decay"


class StrengthType(str, Enum):
    """The kinds of things that went RIGHT on a run (#82 point 3).

    The analysis was problem-centric — every run read like a list of failures.
    A well-executed run has to surface at least one of these so the athlete
    hears what to repeat, not only what to fix.
    """

    NEGATIVE_SPLIT = "negative_split"    # 2nd half genuinely faster — textbook
    EVEN_PACING = "even_pacing"          # both halves within a hair of each other
    CARDIAC_STEADY = "cardiac_steady"    # ~0% drift — well fuelled + hydrated
    CADENCE_STABLE = "cadence_stable"    # steps held to the end, no shuffle
    STRONG_FINISH = "strong_finish"      # closed faster than the middle


class Severity(str, Enum):
    """Severity / confidence ladder shared by moments and overall confidence."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Moment(BaseModel):
    """A single typed event on the run timeline."""

    type: MomentType
    start_s: int                    # offset within time_seconds
    end_s: int
    severity: Severity
    evidence: dict = Field(default_factory=dict)  # numeric proof, internal
    # Real distance at the moment's start, derived from the distance/pace stream
    # (#82 point 2). Optional so pre-#82 stored payloads still validate; the km
    # label is the rounded convenience view the UI shows ("km 32").
    distance_m: Optional[float] = None
    km: Optional[float] = None


class Strength(BaseModel):
    """A single "what went well" signal on the run (#82 point 3)."""

    type: StrengthType
    severity: Severity              # HIGH = standout, LOW = quietly fine
    evidence: dict = Field(default_factory=dict)


class ProfileCtx(BaseModel):
    """Lightweight context derived from athlete_profile — NOT a DB entity.

    ``max_hr`` is always resolved by the caller (ADR §max_hr resolution):
    ``profile.max_hr`` → ``220 - age`` → fallback ``190``.
    """

    max_hr: int
    max_hr_source: str              # "profile" | "age_formula" | "default"
    age: Optional[int] = None
    weight_kg: Optional[float] = None


class RunSignals(BaseModel):
    """Top-level extractor output — typed moments + aggregate metrics."""

    moments: list[Moment] = Field(default_factory=list)
    strengths: list[Strength] = Field(default_factory=list)  # #82: what went well
    gap_pace_per_km: list[float] = Field(default_factory=list)
    hr_zones: dict = Field(default_factory=dict)   # semantic keys, not Z1
    split_ratio: Optional[float] = None            # 2nd/1st half avg pace; >1 = positive split
    decoupling_pct: Optional[float] = None
    cadence_trend: Optional[float] = None          # slope; negative = decay
    duration_s: int = 0
    confidence: Severity = Severity.MEDIUM
    schema_version: int = 1


# ---------------------------------------------------------------------------
# Sanitization (moved verbatim from training_analyzer L136-152)
# ---------------------------------------------------------------------------


def sanitize_pace_stream(values: list[float] | None) -> list[float]:
    """Drop None / non-positive / out-of-band pace samples.

    Args:
        values: Raw `pace_per_km` stream from Strava. May contain None, 0,
                or extreme spikes from GPS pause windows.

    Returns:
        New list of pace values in [PACE_MIN_VALID, PACE_MAX_VALID]. Order is
        preserved relative to the input but `time_seconds` alignment is lost —
        callers that need positional alignment must filter time_seconds in the
        same step (see detect_pace_drop_summary).
    """
    return [
        v for v in (values or [])
        if v is not None and PACE_MIN_VALID <= v <= PACE_MAX_VALID
    ]


# ---------------------------------------------------------------------------
# Grade-adjusted pace (GAP)
# ---------------------------------------------------------------------------


def grade_adjusted_pace(
    pace_per_km: list[float],
    altitude: list[float],
    time_seconds: list[float],
) -> list[float]:
    """Correct pace for terrain gradient so uphill slowdown is not a false bonk.

    Uses a linear grade-cost model: each 1% of incline costs ~3.3% of pace
    (running-economy approximation, symmetric for descents which "speed up"
    the adjusted baseline). The gradient at sample ``i`` is the altitude delta
    over the horizontal distance covered in that interval, derived from pace and
    elapsed time. Samples without enough data to compute a gradient pass through
    unchanged.

    Args:
        pace_per_km: Raw pace stream (min/km).
        altitude: Altitude stream (m), positionally aligned with pace.
        time_seconds: Elapsed time per sample (s), positionally aligned.

    Returns:
        Grade-adjusted pace stream, same length as ``pace_per_km``. On a flat
        course this is ~identical to the input.
    """
    n = len(pace_per_km)
    if n == 0:
        return []
    if len(altitude) != n or len(time_seconds) != n:
        # Cannot compute gradient without aligned altitude/time → no adjustment.
        return list(pace_per_km)

    gap: list[float] = []
    # Grade cost coefficient: fractional pace change per unit grade (rise/run).
    # ~3.3% pace cost per 1% incline → 3.3 per 1.0 grade fraction.
    grade_cost = 3.3

    for i in range(n):
        pace = pace_per_km[i]
        if pace is None or pace <= 0:
            gap.append(pace)
            continue
        if i == 0:
            gap.append(pace)
            continue

        alt_prev, alt_cur = altitude[i - 1], altitude[i]
        t_prev, t_cur = time_seconds[i - 1], time_seconds[i]
        if alt_prev is None or alt_cur is None or t_prev is None or t_cur is None:
            gap.append(pace)
            continue

        dt_s = t_cur - t_prev
        if dt_s <= 0 or pace < PACE_MIN_VALID or pace > PACE_MAX_VALID:
            gap.append(pace)
            continue

        # Horizontal distance covered in this interval (km), from pace + time.
        dist_km = (dt_s / 60.0) / pace
        if dist_km <= 0:
            gap.append(pace)
            continue

        rise_m = alt_cur - alt_prev
        run_m = dist_km * 1000.0
        grade = rise_m / run_m if run_m > 0 else 0.0
        # Clamp grade to a sane band so a noisy altitude spike can't explode GAP.
        grade = max(-0.30, min(0.30, grade))

        # Uphill (grade > 0) → adjusted pace is FASTER than raw (we discount the
        # terrain penalty), so the athlete's effort looks steady on flat-equivalent.
        adjusted = pace / (1.0 + grade_cost * grade)
        gap.append(round(adjusted, 3))

    return gap


# ---------------------------------------------------------------------------
# Pace-drop detection
# ---------------------------------------------------------------------------


def _baseline_pace(pace_values: list[float], n_baseline: int) -> Optional[float]:
    """Average of the first ``n_baseline`` in-band samples, or None."""
    baseline_values = [
        p for p in pace_values[:n_baseline]
        if p is not None and PACE_MIN_VALID <= p <= PACE_MAX_VALID
    ]
    if not baseline_values:
        return None
    return sum(baseline_values) / len(baseline_values)


def _median(values: list[float]) -> Optional[float]:
    """Median of a list, or None when empty."""
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def _stabilized_baseline_pace(pace_values: list[float]) -> Optional[float]:
    """The athlete's *settled cruising* pace — the honest thing to drop from.

    #82 point 1: the old baseline was the mean of the first 10% of samples, so a
    normal fast start pulled it too fast and every run after that looked like a
    collapse. Instead we drop the warmup (~first 10%) and take the **median** of
    the settled early band (roughly the first half after warmup). The median
    resists both the fast start and a late collapse tail, so the baseline reads
    the pace the athlete actually held once they found their rhythm.

    Args:
        pace_values: Pace stream (min/km), already the raw or GAP series.

    Returns:
        The stabilized baseline pace (min/km), or None when there is no usable
        settled window (e.g. a run too short to have one).
    """
    in_band = [
        p for p in pace_values
        if p is not None and PACE_MIN_VALID <= p <= PACE_MAX_VALID
    ]
    n = len(in_band)
    if n == 0:
        return None
    if n < 4:
        # Too short to carve a warmup out of — the median of the whole thing is
        # still steadier than the first sample.
        return _median(in_band)

    warmup_end = max(1, round(n * 0.10))
    settled_end = max(warmup_end + 1, round(n * 0.50))
    window = in_band[warmup_end:settled_end]
    if not window:
        window = in_band[warmup_end:]
    return _median(window)


def _cliff_severity(drop_pct: float) -> Severity:
    """Map a sustained pace-collapse magnitude to a severity bucket.

    A sustained collapse is already a serious event by the time it clears the
    15% baseline gate, so ~18%+ is treated as HIGH (a real bonk), 12-18% MEDIUM,
    below that LOW. Thresholds are v1 tuning targets (ADR 2026-06-02).
    """
    if drop_pct >= 18.0:
        return Severity.HIGH
    if drop_pct >= 12.0:
        return Severity.MEDIUM
    return Severity.LOW


def detect_pace_drop(
    time_seconds: list[float],
    pace_per_km: list[float],
    gap_pace: Optional[list[float]] = None,
    threshold: float = CLIFF_THRESHOLD_PCT,
) -> list[Moment]:
    """Detect the run's single hardest sustained pace collapse → CLIFF moment.

    When ``gap_pace`` is supplied the drop is measured on the grade-adjusted
    stream, so an uphill slowdown is absorbed and does NOT produce a false CLIFF.
    Baseline is the athlete's *settled cruising* pace (median of the post-warmup
    early band, :func:`_stabilized_baseline_pace`) — NOT the fast first 10%, which
    used to make an ordinary quick start read as a collapse (#82 point 1).

    The whole run is scanned (the old code returned on the *first* window it saw,
    which caught the warmup, not the bonk). Every sustained-drop window is
    collected and only the genuinely hardest one (largest %) is emitted.

    Corroboration (that a real CLIFF coincides with cardiac drift or a positive
    split) is applied one layer up in :func:`extract_run_signals`, which has the
    other signals in hand — this function stays a pure pace-shape detector.

    Args:
        time_seconds: Elapsed time per sample (s).
        pace_per_km: Raw pace stream (min/km).
        gap_pace: Optional grade-adjusted pace stream. When given, detection runs
                  on it instead of the raw pace.
        threshold: Minimum % over baseline to flag as a collapse.

    Returns:
        A list with at most one CLIFF ``Moment`` — the hardest sustained collapse
        on the run, or empty when nothing clears the baseline gate.
    """
    series = gap_pace if gap_pace is not None else pace_per_km
    if not series or not time_seconds or len(series) != len(time_seconds):
        return []

    n = len(series)
    baseline = _stabilized_baseline_pace(series)
    if baseline is None or baseline <= 0:
        return []

    scan_start = max(1, round(n * 0.10))  # skip the warmup we excluded from baseline

    # Collect every sustained-drop window across the whole run, then keep the
    # hardest. A window is a contiguous run of samples ≥ threshold over baseline.
    windows: list[tuple[int, int, float]] = []  # (start_idx, end_idx, max_drop)
    window_start: Optional[int] = None
    window_max_drop = 0.0

    for i in range(scan_start, n):
        current = series[i]
        in_band = (
            current is not None
            and PACE_MIN_VALID <= current <= PACE_MAX_VALID
        )
        drop = ((current - baseline) / baseline * 100) if in_band else 0.0

        if in_band and drop >= threshold:
            if window_start is None:
                window_start = i
                window_max_drop = drop
            else:
                window_max_drop = max(window_max_drop, drop)
        elif window_start is not None:
            windows.append((window_start, i - 1, window_max_drop))
            window_start = None
            window_max_drop = 0.0

    if window_start is not None:
        windows.append((window_start, n - 1, window_max_drop))

    if not windows:
        return []

    # The genuinely hardest moment — largest sustained drop wins.
    start_idx, end_idx, max_drop = max(windows, key=lambda w: w[2])
    return [
        Moment(
            type=MomentType.CLIFF,
            start_s=int(time_seconds[start_idx]),
            end_s=int(time_seconds[end_idx]),
            severity=_cliff_severity(max_drop),
            evidence={
                "pct_drop": round(max_drop, 1),
                "baseline_pace": round(baseline, 2),
            },
        )
    ]


def detect_pace_drop_summary(
    time_seconds: list[float],
    pace_per_km: list[float],
    threshold_percent: float = CLIFF_THRESHOLD_PCT,
) -> dict[str, Any]:
    """Legacy dict-returning pace-drop summary (moved from training_analyzer).

    Kept for the LLM call-sites (`training_analyzer`, `managed_agent_training`)
    that send ``{"critical_km": ..., "drop_percent": ...}`` to the prompt. The
    typed ``detect_pace_drop`` is the new primary contract; this is the legacy
    summary view over the same baseline logic.

    Args:
        time_seconds: Elapsed time data points in seconds.
        pace_per_km: Corresponding pace in min/km per data point.
        threshold_percent: Minimum drop (%) from baseline to flag as critical.

    Returns:
        Dict with keys ``critical_km`` (float | None) and ``drop_percent`` (float | None).
    """
    if not pace_per_km or not time_seconds or len(pace_per_km) != len(time_seconds):
        return {"critical_km": None, "drop_percent": None}

    n = len(pace_per_km)
    first_tenth = max(1, n // 10)
    baseline = _baseline_pace(pace_per_km, first_tenth)
    if baseline is None or baseline <= 0:
        return {"critical_km": None, "drop_percent": None}

    for i in range(first_tenth, n):
        current = pace_per_km[i]
        if (
            current is not None
            and PACE_MIN_VALID <= current <= PACE_MAX_VALID
        ):
            drop = (current - baseline) / baseline * 100
            if drop >= threshold_percent:
                km_estimate = time_seconds[i] / 60 / baseline if baseline > 0 else None
                return {
                    "critical_km": round(km_estimate, 1) if km_estimate else None,
                    "drop_percent": round(drop, 1),
                }

    return {"critical_km": None, "drop_percent": None}


# ---------------------------------------------------------------------------
# Decoupling (cardiac drift vs pace)
# ---------------------------------------------------------------------------


def detect_decoupling(
    heartrate: list[float],
    pace_per_km: list[float],
    time_seconds: list[float],
) -> Optional[Moment]:
    """Detect HR/pace efficiency drift between the two halves of the run.

    Efficiency for a half = mean(HR) / mean(speed), where speed = 1/pace.
    ``decoupling_pct = eff_2 / eff_1 - 1``. A positive value means the athlete
    needed more heartbeats per unit speed in the second half (cardiac drift).

    Args:
        heartrate: HR stream (bpm).
        pace_per_km: Pace stream (min/km).
        time_seconds: Elapsed time per sample (s).

    Returns:
        A DECOUPLING ``Moment`` when drift > 5%, else None. Returns None when HR
        or pace data is missing/misaligned.
    """
    n = len(pace_per_km)
    if n < 4 or len(heartrate) != n or len(time_seconds) != n:
        return None

    mid = n // 2

    def _efficiency(lo: int, hi: int) -> Optional[float]:
        hrs: list[float] = []
        speeds: list[float] = []
        for i in range(lo, hi):
            hr = heartrate[i]
            pace = pace_per_km[i]
            if (
                hr is not None and hr > 0
                and pace is not None and PACE_MIN_VALID <= pace <= PACE_MAX_VALID
            ):
                hrs.append(hr)
                speeds.append(1.0 / pace)
        if not hrs or not speeds:
            return None
        mean_hr = sum(hrs) / len(hrs)
        mean_speed = sum(speeds) / len(speeds)
        if mean_speed <= 0:
            return None
        return mean_hr / mean_speed

    eff_1 = _efficiency(0, mid)
    eff_2 = _efficiency(mid, n)
    if eff_1 is None or eff_2 is None or eff_1 <= 0:
        return None

    decoupling = eff_2 / eff_1 - 1.0
    if decoupling <= DECOUPLING_THRESHOLD:
        return None

    if decoupling > 0.12:
        severity = Severity.HIGH
    elif decoupling > 0.08:
        severity = Severity.MEDIUM
    else:
        severity = Severity.LOW

    return Moment(
        type=MomentType.DECOUPLING,
        start_s=int(time_seconds[mid]),
        end_s=int(time_seconds[n - 1]),
        severity=severity,
        evidence={"decoupling_pct": round(decoupling, 4)},
    )


# ---------------------------------------------------------------------------
# Positive split
# ---------------------------------------------------------------------------


def _split_ratio(pace_per_km: list[float]) -> Optional[float]:
    """avg(2nd-half pace) / avg(1st-half pace) over in-band samples, or None."""
    cleaned_with_idx = [
        (i, p) for i, p in enumerate(pace_per_km)
        if p is not None and PACE_MIN_VALID <= p <= PACE_MAX_VALID
    ]
    if len(cleaned_with_idx) < 2:
        return None
    mid = len(cleaned_with_idx) // 2
    first = [p for _, p in cleaned_with_idx[:mid]]
    second = [p for _, p in cleaned_with_idx[mid:]]
    if not first or not second:
        return None
    avg_1 = sum(first) / len(first)
    avg_2 = sum(second) / len(second)
    if avg_1 <= 0:
        return None
    return avg_2 / avg_1


def detect_positive_split(
    pace_per_km: list[float],
    time_seconds: list[float],
    threshold: float = POSITIVE_SPLIT_THRESHOLD,
) -> Optional[Moment]:
    """Flag when the second half is slower than the first by > threshold.

    Args:
        pace_per_km: Pace stream (min/km). Higher value = slower.
        time_seconds: Elapsed time per sample (s).
        threshold: Fractional slowdown to flag (default 0.05 = 5%).

    Returns:
        A POSITIVE_SPLIT ``Moment`` when ``split_ratio - 1 > threshold``, else None.
    """
    ratio = _split_ratio(pace_per_km)
    if ratio is None:
        return None
    excess = ratio - 1.0
    if excess <= threshold:
        return None

    if excess > 0.15:
        severity = Severity.HIGH
    elif excess > 0.10:
        severity = Severity.MEDIUM
    else:
        severity = Severity.LOW

    n = len(time_seconds)
    mid_s = int(time_seconds[n // 2]) if n else 0
    end_s = int(time_seconds[-1]) if n else 0
    return Moment(
        type=MomentType.POSITIVE_SPLIT,
        start_s=mid_s,
        end_s=end_s,
        severity=severity,
        evidence={"split_ratio": round(ratio, 3)},
    )


# ---------------------------------------------------------------------------
# Cadence decay
# ---------------------------------------------------------------------------


def _linear_slope(xs: list[float], ys: list[float]) -> Optional[float]:
    """Ordinary least-squares slope of ys over xs, or None if degenerate."""
    n = len(xs)
    if n < 2 or len(ys) != n:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    denom = sum((x - mean_x) ** 2 for x in xs)
    if denom == 0:
        return None
    numer = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    return numer / denom


def detect_cadence_decay(
    cadence: list[float],
    time_seconds: list[float],
) -> Optional[Moment]:
    """Detect a declining cadence trend (spm per 10 minutes).

    Fits a line to cadence over time; a slope below the threshold
    (``-1.5 spm / 10 min``) is flagged as CADENCE_DECAY.

    Args:
        cadence: Cadence stream (spm).
        time_seconds: Elapsed time per sample (s).

    Returns:
        A CADENCE_DECAY ``Moment`` when the trend is steeper than the threshold,
        else None. Also returns None when there is no usable cadence data.
    """
    n = len(cadence)
    if n < 3 or len(time_seconds) != n:
        return None

    xs: list[float] = []
    ys: list[float] = []
    for i in range(n):
        c = cadence[i]
        t = time_seconds[i]
        if c is not None and c > 0 and t is not None:
            xs.append(t)
            ys.append(c)
    if len(xs) < 3:
        return None

    slope_per_s = _linear_slope(xs, ys)
    if slope_per_s is None:
        return None

    # Convert spm-per-second to spm-per-10-minutes.
    slope_per_10min = slope_per_s * 600.0
    if slope_per_10min >= CADENCE_DECAY_THRESHOLD:
        return None

    magnitude = abs(slope_per_10min)
    if magnitude > 6.0:
        severity = Severity.HIGH
    elif magnitude > 3.0:
        severity = Severity.MEDIUM
    else:
        severity = Severity.LOW

    return Moment(
        type=MomentType.CADENCE_DECAY,
        start_s=int(xs[0]),
        end_s=int(xs[-1]),
        severity=severity,
        evidence={"cadence_slope_spm_per_10min": round(slope_per_10min, 2)},
    )


# ---------------------------------------------------------------------------
# Grade-adjustment informational moment
# ---------------------------------------------------------------------------


def detect_grade_adjustment(
    pace_per_km: list[float],
    gap_pace: list[float],
    time_seconds: list[float],
) -> Optional[Moment]:
    """Emit an informational GRADE_ADJUSTMENT moment when the GAP correction was
    material (mean |raw - GAP| / raw > 10%). This is evidence, not an alarm — it
    tells the downstream layer "the terrain meaningfully shaped the raw pace".

    Args:
        pace_per_km: Raw pace stream (min/km).
        gap_pace: Grade-adjusted pace stream (min/km).
        time_seconds: Elapsed time per sample (s).

    Returns:
        A GRADE_ADJUSTMENT ``Moment`` when the correction is material, else None.
    """
    n = len(pace_per_km)
    if n == 0 or len(gap_pace) != n or len(time_seconds) != n:
        return None

    deltas: list[float] = []
    for i in range(n):
        raw = pace_per_km[i]
        adj = gap_pace[i]
        if (
            raw is not None and adj is not None
            and PACE_MIN_VALID <= raw <= PACE_MAX_VALID
            and raw > 0
        ):
            deltas.append(abs(raw - adj) / raw)
    if not deltas:
        return None

    mean_delta = sum(deltas) / len(deltas)
    if mean_delta <= GRADE_ADJUSTMENT_MATERIAL_PCT:
        return None

    return Moment(
        type=MomentType.GRADE_ADJUSTMENT,
        start_s=int(time_seconds[0]),
        end_s=int(time_seconds[-1]),
        severity=Severity.LOW,
        evidence={"mean_gap_correction_pct": round(mean_delta * 100, 1)},
    )


# ---------------------------------------------------------------------------
# HR zones
# ---------------------------------------------------------------------------

# Semantic zone keys (2026-05-19 mapping) — NEVER "Z1"/"Z2" as raw labels.
_SEMANTIC_ZONE_KEYS = ("recovery", "endurance", "tempo", "threshold", "max")


def calculate_hr_zones(heartrate: list[float], max_hr: int) -> dict[str, float]:
    """Percentage of time in each HR zone, keyed by SEMANTIC names.

    Zone boundaries as % of ``max_hr`` (which is now a REQUIRED parameter — the
    legacy 190 default is gone):
      recovery:   < 60%
      endurance:  60–70%
      tempo:      70–80%
      threshold:  80–90%
      max:        > 90%

    Args:
        heartrate: HR data points (bpm).
        max_hr: Athlete's resolved max HR (caller supplies via ProfileCtx).

    Returns:
        Dict mapping semantic zone names to their % of total in-band samples.
    """
    if not heartrate or max_hr <= 0:
        return {k: 0.0 for k in _SEMANTIC_ZONE_KEYS}

    valid = [h for h in heartrate if h and h > 0]
    if not valid:
        return {k: 0.0 for k in _SEMANTIC_ZONE_KEYS}

    counts: dict[str, int] = {k: 0 for k in _SEMANTIC_ZONE_KEYS}
    for hr in valid:
        pct = hr / max_hr * 100
        if pct < 60:
            counts["recovery"] += 1
        elif pct < 70:
            counts["endurance"] += 1
        elif pct < 80:
            counts["tempo"] += 1
        elif pct < 90:
            counts["threshold"] += 1
        else:
            counts["max"] += 1

    total = len(valid)
    return {k: round(v / total * 100, 1) for k, v in counts.items()}


def calculate_hr_zones_legacy(
    heartrate: list[float],
    max_hr: int = 190,
) -> dict[str, float]:
    """Legacy ``zone_1..5`` HR zone distribution (moved from training_analyzer).

    Kept for the existing LLM call-sites that key on ``zone_1..zone_5``. The
    semantic-key ``calculate_hr_zones`` is the new primary contract.

    Args:
        heartrate: HR data points (bpm).
        max_hr: Athlete's max HR (legacy default 190).

    Returns:
        Dict mapping ``zone_1..zone_5`` to their % of total in-band samples.
    """
    if not heartrate:
        return {f"zone_{i}": 0.0 for i in range(1, 6)}

    valid = [h for h in heartrate if h and h > 0]
    if not valid:
        return {f"zone_{i}": 0.0 for i in range(1, 6)}

    zones: dict[str, int] = {f"zone_{i}": 0 for i in range(1, 6)}
    for hr in valid:
        pct = hr / max_hr * 100
        if pct < 60:
            zones["zone_1"] += 1
        elif pct < 70:
            zones["zone_2"] += 1
        elif pct < 80:
            zones["zone_3"] += 1
        elif pct < 90:
            zones["zone_4"] += 1
        else:
            zones["zone_5"] += 1

    total = len(valid)
    return {k: round(v / total * 100, 1) for k, v in zones.items()}


# ---------------------------------------------------------------------------
# Multi-event split (v1 simplified)
# ---------------------------------------------------------------------------

# A gap in time_seconds larger than this between consecutive samples is treated
# as a separation between distinct efforts (long stop / lap boundary).
_EVENT_GAP_S = 600  # 10 minutes


def split_events(
    time_seconds: list[float],
    pace_per_km: list[float],
) -> list[tuple[int, int]]:
    """Split the activity into (start_idx, end_idx_exclusive) effort windows.

    v1 (ADR §"Decyzje Grega"): a single event spanning the whole activity when
    there is no clear separation. We split only on large time gaps between
    consecutive samples (a long stop). Strava ``laps`` API detection is deferred
    to v2.

    Args:
        time_seconds: Elapsed time per sample (s).
        pace_per_km: Pace stream (min/km), length-aligned with time_seconds.

    Returns:
        List of (start, end-exclusive) index tuples. Empty input → empty list.
    """
    n = len(time_seconds)
    if n == 0:
        return []
    if len(pace_per_km) != n:
        return [(0, n)]

    events: list[tuple[int, int]] = []
    start = 0
    for i in range(1, n):
        prev_t, cur_t = time_seconds[i - 1], time_seconds[i]
        if prev_t is None or cur_t is None:
            continue
        if cur_t - prev_t > _EVENT_GAP_S:
            events.append((start, i))
            start = i
    events.append((start, n))
    return events


# ---------------------------------------------------------------------------
# Top-level orchestrator (pure)
# ---------------------------------------------------------------------------


def _slice_stream(stream: list, lo: int, hi: int) -> list:
    """Safe positional slice of a stream that may be shorter than the index."""
    if not stream:
        return []
    return stream[lo:hi]


def cumulative_distance_m(
    pace_per_km: list[float],
    time_seconds: list[float],
    distance_stream: Optional[list[float]] = None,
) -> list[float]:
    """Per-sample cumulative distance (m) along the run (#82 point 2).

    Prefers a real ``distance`` stream (Strava's GPS-integrated distance) when one
    is present and aligned. Otherwise it integrates speed over time from the pace
    stream — ``speed = 1 / pace`` — which recovers the same distance because the
    pace itself came from Strava's ``velocity_smooth``. Either way the result is a
    real place on the course, not the old ``time / 360`` guess at a flat 6:00/km.

    Args:
        pace_per_km: Pace stream (min/km).
        time_seconds: Elapsed time per sample (s), aligned with pace.
        distance_stream: Optional native cumulative-distance stream (m).

    Returns:
        Cumulative distance (m) per sample, same length as ``time_seconds``.
        Empty input → empty list.
    """
    n = len(time_seconds)
    if n == 0:
        return []

    # A usable native distance stream wins — it is the true GPS distance.
    if (
        distance_stream
        and len(distance_stream) == n
        and all(d is not None for d in distance_stream)
    ):
        return [float(d) for d in distance_stream]

    cum: list[float] = [0.0] * n
    if len(pace_per_km) != n:
        return cum

    running = 0.0
    for i in range(n):
        if i == 0:
            cum[i] = 0.0
            continue
        t_prev, t_cur = time_seconds[i - 1], time_seconds[i]
        pace = pace_per_km[i]
        if (
            t_prev is not None and t_cur is not None
            and pace is not None and PACE_MIN_VALID <= pace <= PACE_MAX_VALID
        ):
            dt_s = t_cur - t_prev
            if dt_s > 0:
                # speed (m/s) = 1000 m per (pace min) = 1000 / (pace * 60).
                speed_m_s = 1000.0 / (pace * 60.0)
                running += speed_m_s * dt_s
        cum[i] = round(running, 1)
    return cum


def _nearest_index(time_seconds: list[float], t: float) -> int:
    """Index of the sample whose elapsed time is closest to ``t`` (0 on empty)."""
    best_i = 0
    best_d = float("inf")
    for i, ts in enumerate(time_seconds):
        if ts is None:
            continue
        d = abs(ts - t)
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def _annotate_distance(
    moments: list[Moment],
    time_seconds: list[float],
    cum_dist: list[float],
) -> None:
    """Stamp each moment with the real distance/km at its start (in place)."""
    if not cum_dist or not time_seconds:
        return
    for m in moments:
        idx = _nearest_index(time_seconds, m.start_s)
        if 0 <= idx < len(cum_dist):
            dist_m = cum_dist[idx]
            m.distance_m = dist_m
            m.km = round(dist_m / 1000.0, 1)


def detect_strengths(
    split_ratio: Optional[float],
    decoupling_pct: Optional[float],
    cadence_trend: Optional[float],
    has_cadence: bool,
) -> list[Strength]:
    """Surface what went RIGHT so a good run never reads as pure failure (#82 pt 3).

    Guarantees at least one strength whenever the pacing signal is available and
    the run was not itself a positive split — an even or negatively-split run,
    steady heart, and held cadence are exactly the things worth repeating.

    Args:
        split_ratio: 2nd/1st half avg pace (<1 = faster 2nd half).
        decoupling_pct: HR/pace drift as a fraction (e.g. 0.02 = 2%).
        cadence_trend: Whole-run cadence slope (spm per 10 min); ~0 = held.
        has_cadence: Whether the run actually carried cadence data.

    Returns:
        A list of ``Strength`` (possibly empty when signals are genuinely poor).
    """
    strengths: list[Strength] = []

    # Pacing: a faster or dead-even second half is the headline strength.
    if split_ratio is not None:
        if split_ratio < 0.97:
            gain = round((1.0 - split_ratio) * 100, 1)
            sev = Severity.HIGH if split_ratio < 0.94 else Severity.MEDIUM
            strengths.append(
                Strength(
                    type=StrengthType.NEGATIVE_SPLIT,
                    severity=sev,
                    evidence={"split_ratio": round(split_ratio, 3), "faster_pct": gain},
                )
            )
        elif split_ratio <= 1.03:
            strengths.append(
                Strength(
                    type=StrengthType.EVEN_PACING,
                    severity=Severity.MEDIUM,
                    evidence={"split_ratio": round(split_ratio, 3)},
                )
            )

    # Cardiac drift near zero → well fuelled + hydrated to the end.
    if decoupling_pct is not None and decoupling_pct < 0.03:
        strengths.append(
            Strength(
                type=StrengthType.CARDIAC_STEADY,
                severity=Severity.MEDIUM,
                evidence={"decoupling_pct": round(decoupling_pct, 4)},
            )
        )

    # Cadence held (only claim it when we actually measured cadence).
    if has_cadence and cadence_trend is not None and cadence_trend >= -1.0:
        strengths.append(
            Strength(
                type=StrengthType.CADENCE_STABLE,
                severity=Severity.LOW,
                evidence={"cadence_slope_spm_per_10min": round(cadence_trend, 2)},
            )
        )

    return strengths


def extract_run_signals(streams: dict, profile_ctx: ProfileCtx) -> RunSignals:
    """Extract typed run signals from raw streams (pure, no DB/LLM).

    Pipeline (ADR §"Public API"):
        sanitize → split_events → per event {GAP, detect_pace_drop(gap),
        decoupling, positive_split, cadence_decay, grade_adjustment}
        → semantic HR zones(max_hr) → aggregate into RunSignals.

    Args:
        streams: Activity streams, typically ``activities.fit_data["streams"]``
                 with keys heartrate / pace_per_km / altitude / cadence /
                 time_seconds.
        profile_ctx: Resolved athlete context (carries ``max_hr`` + source).

    Returns:
        A populated ``RunSignals``. ``confidence`` is LOW when
        ``max_hr_source == "default"`` or the activity is shorter than 10 min.
    """
    time_seconds: list[float] = list(streams.get("time_seconds") or [])
    pace_raw: list[float] = list(streams.get("pace_per_km") or [])
    altitude: list[float] = list(streams.get("altitude") or [])
    cadence: list[float] = list(streams.get("cadence") or [])
    heartrate: list[float] = list(streams.get("heartrate") or [])
    distance_stream: list[float] = list(
        streams.get("distance_m") or streams.get("distance") or []
    )

    duration_s = int(max(time_seconds)) if time_seconds else 0

    # Whole-activity grade-adjusted pace (used downstream + per-event detection).
    gap_pace = grade_adjusted_pace(pace_raw, altitude, time_seconds)

    moments: list[Moment] = []
    events = split_events(time_seconds, pace_raw)

    for lo, hi in events:
        t_ev = _slice_stream(time_seconds, lo, hi)
        pace_ev = _slice_stream(pace_raw, lo, hi)
        gap_ev = _slice_stream(gap_pace, lo, hi)
        cad_ev = _slice_stream(cadence, lo, hi)
        hr_ev = _slice_stream(heartrate, lo, hi)

        if not t_ev or not pace_ev:
            continue

        # CLIFF on the GAP stream — uphill slowdown absorbed, not a false bonk.
        cliffs = detect_pace_drop(t_ev, pace_ev, gap_pace=gap_ev)

        decoupling = detect_decoupling(hr_ev, pace_ev, t_ev)
        split = detect_positive_split(pace_ev, t_ev)
        cad_decay = detect_cadence_decay(cad_ev, t_ev)
        grade = detect_grade_adjustment(pace_ev, gap_ev, t_ev)

        # Corroboration gate (#82 point 1): a pace drop is only a real CLIFF when
        # a second-half physiological signal backs it up — cardiac drift OR a
        # positive split. A lone pace wobble (GPS noise, a single slow km, an
        # unflagged hill) is NOT a bonk and must not headline the run as one.
        corroborated = decoupling is not None or split is not None
        if corroborated:
            moments.extend(cliffs)

        for m in (decoupling, split, cad_decay, grade):
            if m is not None:
                moments.append(m)

    # Aggregate metrics over the whole activity.
    hr_zones = calculate_hr_zones(heartrate, profile_ctx.max_hr)
    split_ratio = _split_ratio(pace_raw)

    decoupling_overall = detect_decoupling(heartrate, pace_raw, time_seconds)
    decoupling_pct = (
        decoupling_overall.evidence.get("decoupling_pct")
        if decoupling_overall is not None
        else None
    )

    cadence_overall = _cadence_trend(cadence, time_seconds)

    # Stamp every moment with the real distance/km it happened at (#82 point 2).
    cum_dist = cumulative_distance_m(pace_raw, time_seconds, distance_stream)
    _annotate_distance(moments, time_seconds, cum_dist)

    # What went well — always at least one when the pacing signal is good (pt 3).
    has_cadence = any(c is not None and c > 0 for c in cadence)
    strengths = detect_strengths(
        split_ratio=round(split_ratio, 3) if split_ratio is not None else None,
        decoupling_pct=decoupling_pct,
        cadence_trend=cadence_overall,
        has_cadence=has_cadence,
    )

    confidence = Severity.MEDIUM
    if profile_ctx.max_hr_source == "default" or duration_s < SHORT_STREAM_DURATION_S:
        confidence = Severity.LOW

    return RunSignals(
        moments=moments,
        strengths=strengths,
        gap_pace_per_km=gap_pace,
        hr_zones=hr_zones,
        split_ratio=round(split_ratio, 3) if split_ratio is not None else None,
        decoupling_pct=decoupling_pct,
        cadence_trend=cadence_overall,
        duration_s=duration_s,
        confidence=confidence,
        schema_version=1,
    )


# ---------------------------------------------------------------------------
# Run-dot verdict (v11 #88 F2c, "NOWE-S") — backend port of the mobile
# `runDot()` in mobile/src/screens/v11/lib/verdict.ts so the activities LIST
# can carry the timeline-dot verdict in one batch instead of the client
# fetching run-signals per row.
# ---------------------------------------------------------------------------

#: One-word severity read of a run for the timeline dot:
#: ``attention`` (a medium/high moment) · ``clean`` (even run) ·
#: ``insufficient`` (not enough data for an honest call).
RunDot = Literal["attention", "clean", "insufficient"]

_SEVERITY_RANK: dict[Severity, int] = {
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


def lead_moment(moments: list[Moment]) -> Optional[Moment]:
    """The single moment that defines the run's verdict.

    Highest severity wins; ties break on the earliest ``start_s`` — identical
    ordering to the mobile ``leadMoment()`` so both surfaces agree on the dot.
    """
    if not moments:
        return None
    return sorted(
        moments,
        key=lambda m: (-_SEVERITY_RANK.get(m.severity, 0), m.start_s),
    )[0]


def run_dot(signals: Optional[RunSignals]) -> RunDot:
    """One-word severity read of a run (port of mobile ``runDot()``).

    ``insufficient`` when there are no signals, or the extractor confidence is
    low with zero detected moments; ``attention`` when the lead moment is
    medium/high severity; ``clean`` otherwise.
    """
    if signals is None:
        return "insufficient"
    if signals.confidence == Severity.LOW and not signals.moments:
        return "insufficient"
    lead = lead_moment(signals.moments)
    if lead is not None and lead.severity in (Severity.HIGH, Severity.MEDIUM):
        return "attention"
    return "clean"


def run_dot_from_stored(raw: Any) -> RunDot:
    """Compute the run dot from a stored ``activities.run_signals`` JSON value.

    Defensive at the storage boundary: an absent or unparseable payload (a
    shape predating the current contract) yields ``insufficient`` rather than
    raising — the honest "not enough data" dot.
    """
    if not isinstance(raw, dict):
        return "insufficient"
    try:
        signals = RunSignals.model_validate(raw)
    except Exception:
        return "insufficient"
    return run_dot(signals)


def _cadence_trend(cadence: list[float], time_seconds: list[float]) -> Optional[float]:
    """Whole-activity cadence slope (spm per 10 min) for the RunSignals metric."""
    n = len(cadence)
    if n < 3 or len(time_seconds) != n:
        return None
    xs: list[float] = []
    ys: list[float] = []
    for i in range(n):
        c = cadence[i]
        t = time_seconds[i]
        if c is not None and c > 0 and t is not None:
            xs.append(t)
            ys.append(c)
    if len(xs) < 3:
        return None
    slope_per_s = _linear_slope(xs, ys)
    if slope_per_s is None:
        return None
    return round(slope_per_s * 600.0, 3)
