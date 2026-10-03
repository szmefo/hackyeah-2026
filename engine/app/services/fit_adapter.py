"""Adapter: parsed FIT activity JSON → canonical analyzer stream shape (#171).

The FIT parser (:func:`app.services.fit_parser.parse_fit_bytes`) emits streams as
``{"data": [...], "original_size": N}`` objects and stores speed under
``velocity_smooth`` in **m/s**. The training analyzer
(:func:`app.services.training_analyzer.format_streams_for_prompt` and the
downstream ``detect_pace_drop`` / ``extract_run_signals``) reads **flat lists**
keyed ``heartrate`` / ``pace_per_km`` (**min/km**) / ``altitude`` / ``cadence`` /
``time_seconds``.

Without this adapter an uploaded ``.FIT`` run reaches the model with an empty
Pace section (key mismatch) — or not at all (object-vs-list mismatch). This is
the single point where a ``.FIT`` activity is reshaped into the *same* streams a
Strava activity produces (``strava_client.get_activity_streams``), so both feed
one identical prompt path — no separate ``.FIT`` branch in the prompts.
"""
from __future__ import annotations

from typing import Any


def _velocity_ms_to_pace_min_per_km(velocity_ms: float | None) -> float:
    """Convert velocity (m/s) to running pace (min/km).

    Mirrors ``strava_client._velocity_to_pace`` exactly so the ``.FIT`` path and
    the Strava path convert speed identically. A zero / ``None`` / negative speed
    (GPS pause, stopped sample) maps to ``0.0`` — ``format_streams_for_prompt``
    filters non-positive pace samples out of its stats, same as for Strava.

    Args:
        velocity_ms: Instantaneous speed in metres per second.

    Returns:
        Pace in minutes per kilometre, or ``0.0`` when speed is non-positive.
    """
    if not velocity_ms or velocity_ms <= 0:
        return 0.0
    return 1000.0 / 60.0 / velocity_ms


def _flat_stream(stream: Any) -> list[float]:
    """Flatten one parser stream entry to a plain list of samples.

    Accepts the parser's ``{"data": [...], "original_size": N}`` object, a bare
    list (already-flat / canonical input — idempotent), or ``None`` (missing
    stream → empty list).

    Args:
        stream: A parser stream value.

    Returns:
        The sample list, or ``[]`` when the stream is absent/empty.
    """
    if stream is None:
        return []
    if isinstance(stream, dict):
        data = stream.get("data")
        return list(data) if data else []
    if isinstance(stream, list):
        return list(stream)
    return []


def _reconstruct_time_axis(activity_json: dict[str, Any], sample_count: int) -> list[int]:
    """Best-effort per-sample time axis (seconds) for a ``.FIT`` activity.

    The parser drops per-record timestamps, but the session summary keeps the
    real ``elapsed_time`` / ``moving_time``. FIT records are sampled at ~1 Hz and
    evenly spaced, so we distribute the real elapsed span evenly across the
    samples: ``time[i] = round(i * elapsed / (n - 1))``. This feeds the optional
    Duration line and ``detect_pace_drop`` (which pairs time with pace); it is
    never required for the analysis — the load-bearing streams are HR + pace.

    Args:
        activity_json: The parser's unified activity dict.
        sample_count: Number of samples to build a time axis for (pace length).

    Returns:
        Monotonic seconds list of length ``sample_count`` (empty for < 2 samples).
    """
    if sample_count < 2:
        return []
    elapsed = activity_json.get("elapsed_time") or activity_json.get("moving_time")
    if not elapsed or elapsed <= 0:
        # No summary timing — fall back to a 1 Hz assumption (FIT default).
        return list(range(sample_count))
    step = float(elapsed) / (sample_count - 1)
    return [round(i * step) for i in range(sample_count)]


def adapt_fit_activity_to_streams(activity_json: dict[str, Any]) -> dict[str, list]:
    """Reshape a parsed ``.FIT`` activity into the canonical analyzer streams.

    Output matches ``strava_client.get_activity_streams``'s ``["streams"]`` shape
    exactly: flat lists keyed ``heartrate`` / ``pace_per_km`` (min/km) /
    ``altitude`` / ``cadence`` / ``time_seconds``. Feeding this into
    ``format_streams_for_prompt`` yields non-empty Heart rate + Pace sections
    whenever the file carried HR and speed.

    Args:
        activity_json: Output of :func:`app.services.fit_parser.parse_fit_bytes`.

    Returns:
        Canonical streams dict ready for
        :meth:`app.services.training_analyzer.TrainingOrchestrator.run`.
    """
    samples = activity_json.get("samples")
    if isinstance(samples, dict) and samples.get("time_seconds"):
        return _adapt_aligned_samples(samples, activity_json)

    streams = activity_json.get("streams") or {}

    heartrate = [int(v) for v in _flat_stream(streams.get("heartrate")) if v is not None]
    velocity = _flat_stream(streams.get("velocity_smooth"))
    pace_per_km = [_velocity_ms_to_pace_min_per_km(v) for v in velocity]
    altitude = [float(v) for v in _flat_stream(streams.get("altitude")) if v is not None]
    cadence = [int(v) for v in _flat_stream(streams.get("cadence")) if v is not None]

    axis_len = len(pace_per_km) or len(heartrate)
    time_seconds = _reconstruct_time_axis(activity_json, axis_len)

    return {
        "heartrate": heartrate,
        "pace_per_km": pace_per_km,
        "altitude": altitude,
        "cadence": cadence,
        "time_seconds": time_seconds,
    }


def _adapt_aligned_samples(samples: dict[str, Any], activity_json: dict[str, Any]) -> dict[str, list]:
    """Reshape parser-v2 aligned samples (ADR 2026-09-12) into canonical streams.

    Every output list has the SAME length as ``time_seconds`` and a missing
    reading stays ``None`` — the consumers (``format_streams_for_prompt``,
    ``detect_decoupling``, moment slicing) already skip ``None`` and read HR by
    position, which is exactly what the v1 compaction broke.

    Args:
        samples: The parser's ``samples`` block.
        activity_json: The whole parsed activity (for the elapsed-time fallback
            when records carried no timestamps — ``time_axis == "ordinal"``).

    Returns:
        Canonical streams dict with index-aligned lists.
    """
    n = len(samples.get("time_seconds") or [])
    if samples.get("time_axis") == "ordinal":
        time_seconds = _reconstruct_time_axis(activity_json, n) or list(range(n))
    else:
        time_seconds = [int(t) for t in samples["time_seconds"]]

    def _aligned(key: str) -> list:
        values = list(samples.get(key) or [])
        values = values[:n] + [None] * max(0, n - len(values))
        return values

    heartrate = [int(v) if v is not None else None for v in _aligned("heartrate")]
    pace_per_km = [
        _velocity_ms_to_pace_min_per_km(v) if v is not None else 0.0
        for v in _aligned("velocity_ms")
    ]
    altitude = [float(v) if v is not None else None for v in _aligned("altitude")]
    cadence = [int(v) if v is not None else None for v in _aligned("cadence")]
    distance_m = [float(v) if v is not None else None for v in _aligned("distance_m")]
    out: dict[str, list] = {
        "heartrate": heartrate,
        "pace_per_km": pace_per_km,
        "altitude": altitude,
        "cadence": cadence,
        "time_seconds": time_seconds,
    }
    if any(d is not None for d in distance_m):
        # Native cumulative distance (m) — run_signal_extractor prefers it over
        # the pace-integrated estimate when every sample carries it.
        out["distance_m"] = distance_m
    return out


def fit_streams_have_signal(streams: dict[str, list]) -> bool:
    """Whether adapted ``.FIT`` streams carry anything the analyzer can read.

    True when at least one HR sample or one positive pace sample is present —
    the same "usable stream data" bar the ``/training/analyze`` endpoint enforces
    for Strava activities (400 branch). A header-only / dataless ``.FIT`` (e.g. an
    indoor entry with no HR strap and no GPS) yields False so the caller can
    return an honest Polish message instead of an empty analysis.

    Args:
        streams: Output of :func:`adapt_fit_activity_to_streams`.

    Returns:
        ``True`` when HR or positive pace samples exist, else ``False``.
    """
    if any(streams.get("heartrate") or []):
        return True
    return any(p for p in (streams.get("pace_per_km") or []) if p and p > 0)
