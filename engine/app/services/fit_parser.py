"""FIT file parser service — in-memory only, no disk writes.

Uses garmin-fit-sdk for decoding. Produces a unified JSON matching the
Strava activity streams output schema (heartrate, velocity_smooth, altitude,
cadence) PLUS — since parser version 2 (Garmin pilot, ADR 2026-09-12) — an
index-aligned ``samples`` block on one shared time axis:

    samples = {
        "time_seconds": [0, 1, 2, ...],          # from record timestamps
        "heartrate":    [142, None, 143, ...],   # None = sensor had no reading
        "velocity_ms":  [...], "altitude": [...], "cadence": [...],
        "distance_m":   [...],
    }

Why the aligned block exists: the v1 streams compact every channel
independently (``if hr is not None: hr_data.append(...)``), so one missing HR
sample silently shifts every later HR reading one index earlier. Downstream
consumers (decoupling, moment slicing) index HR by position against pace/time
and would read the wrong heartbeat for the right second. The v1 ``streams``
stay for backward compatibility; :mod:`app.services.fit_adapter` prefers
``samples`` whenever they are present.

GPS is excluded by default; the Garmin worker may opt in after GPS consent.
Device serial numbers are never returned (a manufacturer/product/file-type
summary is enough as limited source evidence).
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

PARSER_VERSION = 2

# FIT epoch: seconds since 1989-12-31T00:00:00Z.
_FIT_EPOCH = datetime(1989, 12, 31, tzinfo=timezone.utc)

# User-facing copy for a decoder that choked on the upload (#125). The decoder
# error list carries library internals (message/field names, byte offsets) and
# has no meaning for an athlete — it goes to the log, not to the screen.
_FIT_PARSE_FAILED_PL = (
    "Nie udało się odczytać tego pliku FIT — może być uszkodzony lub "
    "niekompletny. Wyeksportuj go ponownie z zegarka i spróbuj jeszcze raz."
)
_FIT_MULTISPORT_PL = (
    "Ten plik zawiera aktywność wielodyscyplinową (np. triathlon). Na razie "
    "analizujemy pojedyncze biegi — wyeksportuj sam odcinek biegowy."
)

# Sports we label as a run. Everything else keeps the raw sport name and is
# reported as ``is_run=False`` so the caller decides (sync imports only runs).
_RUN_SPORTS = {"running", "trail_running", "treadmill", "track_running"}
_RUN_SUB_SPORT_LABELS = {
    "trail": "TrailRun",
    "treadmill": "Treadmill",
    "track": "Run",
    "road": "Run",
    "street": "Run",
    "indoor_running": "Treadmill",
}


class FitParseError(ValueError):
    """Typed parser failure. ``code`` is machine-readable and secret-free."""

    def __init__(self, code: str, detail_pl: str) -> None:
        super().__init__(code)
        self.code = code
        self.detail_pl = detail_pl


def parse_fit_bytes(content: bytes) -> dict[str, Any]:
    """Parse raw FIT file bytes and return a unified activity JSON (HTTP contract).

    Thin wrapper over :func:`parse_fit_activity` that keeps the historical
    ``HTTPException`` contract of the upload endpoint.

    Args:
        content: Raw bytes of a .fit file.

    Returns:
        Unified activity dict with source, streams, samples and summary_stats.

    Raises:
        HTTPException 422 if the bytes are not a valid / supported FIT file.
        HTTPException 500 if the decoder library is missing.
    """
    try:
        return parse_fit_activity(content)
    except FitParseError as exc:
        if exc.code == "decoder_unavailable":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FIT parsing library not available",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.detail_pl,
            headers={"X-FIT-Error-Code": exc.code},
        ) from exc


def parse_fit_activity(content: bytes, *, include_gps: bool = False, include_details: bool = False) -> dict[str, Any]:
    """Parse raw FIT bytes into the unified activity JSON (typed errors).

    The file is processed entirely in RAM — no data is written to disk.

    Args:
        content: Raw bytes of a .fit file.

    Returns:
        Unified activity dict (see module docstring).

    Raises:
        FitParseError: ``not_fit`` / ``decode_failed`` / ``multisport_unsupported``
            / ``decoder_unavailable``.
    """
    try:
        from garmin_fit_sdk import Decoder, Stream
    except ImportError as exc:
        raise FitParseError("decoder_unavailable", _FIT_PARSE_FAILED_PL) from exc

    stream = Stream.from_bytes_io(BytesIO(content))
    decoder = Decoder(stream)

    if not decoder.is_fit():
        raise FitParseError("not_fit", "Uploaded file is not a valid FIT file")

    messages, errors = decoder.read(
        convert_datetimes_to_dates=False,
        convert_types_to_strings=True,
    )

    if errors:
        # #125: the raw decoder errors used to ride the 422 detail straight to
        # the client. Full list stays in the server log for debugging.
        logger.error("FIT decode reported %d error(s): %s", len(errors), errors[:3])
        raise FitParseError("decode_failed", _FIT_PARSE_FAILED_PL)

    result = _extract_activity(messages)
    if include_details:
        from app.services.garmin_details import extract_details
        result["details"] = extract_details(messages)
    if include_gps:
        from app.services.garmin_route import extract_route
        result["gps_route"] = extract_route(messages.get("record_mesgs", []))
    return result


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


def _extract_activity(messages: dict[str, Any]) -> dict[str, Any]:
    """Extract unified activity JSON from decoded FIT messages.

    Args:
        messages: Dict of message type → list of records from garmin-fit-sdk.

    Returns:
        Unified activity dict.

    Raises:
        FitParseError: ``multisport_unsupported`` when the file carries more
            than one session with different sports or a multisport session.
    """
    session_msgs = messages.get("session_mesgs", [])
    session = session_msgs[0] if session_msgs else {}
    _reject_multisport(session_msgs)

    records = messages.get("record_mesgs", [])
    samples = _aligned_samples(records)

    # --- v1 compact streams (backward compatible) ---
    hr_data = [v for v in samples["heartrate"] if v is not None]
    vel_data = [v for v in samples["velocity_ms"] if v is not None]
    alt_data = [v for v in samples["altitude"] if v is not None]
    cad_data = [v for v in samples["cadence"] if v is not None]

    distance = _float_or_none(session.get("total_distance"))
    timer_time = _int_or_none(session.get("total_timer_time"))
    moving_time = _int_or_none(session.get("total_moving_time")) or timer_time
    elapsed_time = _int_or_none(session.get("total_elapsed_time"))
    elevation_gain = _float_or_none(session.get("total_ascent"))
    sport_raw = str(session.get("sport", "unknown") or "unknown")
    sub_sport_raw = str(session.get("sub_sport") or "")
    sport_label, is_run = _sport_label(sport_raw, sub_sport_raw)

    start_raw = session.get("start_time")
    start_time = str(start_raw) if start_raw else None
    start_time_utc = _fit_timestamp_to_iso(start_raw)
    if start_time_utc is None and samples["_first_timestamp"] is not None:
        start_time_utc = _fit_timestamp_to_iso(samples["_first_timestamp"])
    tz_offset = _local_timezone_offset_s(messages.get("activity_mesgs", []))

    pauses = _timer_pauses(messages.get("event_mesgs", []), samples["_first_timestamp"])
    if elapsed_time is not None and moving_time is not None and elapsed_time < moving_time:
        # Some devices store elapsed < timer (rounding); never report a negative pause.
        elapsed_time = moving_time

    # Summary stats
    avg_hr = int(round(sum(hr_data) / len(hr_data))) if hr_data else None
    max_hr = max(hr_data) if hr_data else None
    avg_vel = sum(vel_data) / len(vel_data) if vel_data else None
    avg_pace_kmh = round(avg_vel * 3.6, 2) if avg_vel is not None else None
    avg_cad = int(round(sum(cad_data) / len(cad_data))) if cad_data else None

    def _stream_obj(data: list) -> dict[str, Any] | None:
        if not data:
            return None
        return {"data": data, "original_size": len(data)}

    return {
        "source": "fit_upload",
        "activity_id": f"fit-{uuid.uuid4()}",
        "name": "Uploaded Activity",
        "type": sport_label,
        "sport": sport_raw,
        "sub_sport": sub_sport_raw or None,
        "is_run": is_run,
        "distance": distance,
        "moving_time": moving_time,
        "elapsed_time": elapsed_time,
        "total_elevation_gain": elevation_gain,
        "start_date": start_time,
        "start_time_utc": start_time_utc,
        "local_timezone_offset_s": tz_offset,
        "pauses": pauses,
        "parser_version": PARSER_VERSION,
        "streams": {
            "heartrate": _stream_obj(hr_data),
            "velocity_smooth": _stream_obj(vel_data),
            "altitude": _stream_obj(alt_data),
            "cadence": _stream_obj(cad_data),
        },
        "samples": {
            "time_seconds": samples["time_seconds"],
            "time_axis": samples["time_axis"],
            "heartrate": samples["heartrate"],
            "velocity_ms": samples["velocity_ms"],
            "altitude": samples["altitude"],
            "cadence": samples["cadence"],
            "distance_m": samples["distance_m"],
        },
        "summary_stats": {
            "avg_hr": avg_hr,
            "max_hr": max_hr,
            "avg_pace_kmh": avg_pace_kmh,
            "avg_cadence": avg_cad,
            "temperature_est": None,
            "has_heartrate": bool(hr_data),
            "sample_count": len(samples["time_seconds"]),
        },
        "device": _device_summary(messages),
    }


def _aligned_samples(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Build one shared time axis and one value (or ``None``) per channel per record.

    ``enhanced_speed`` / ``enhanced_altitude`` win over the 16-bit ``speed`` /
    ``altitude`` when present (they carry the un-clamped value); the legacy
    field is the fallback. Records without a timestamp fall back to their
    ordinal position so the axis stays monotonic.
    """
    time_seconds: list[int] = []
    hr: list[int | None] = []
    vel: list[float | None] = []
    alt: list[float | None] = []
    cad: list[int | None] = []
    dist: list[float | None] = []
    first_ts: int | None = None
    last_t = -1

    for idx, rec in enumerate(records):
        ts = _int_or_none(rec.get("timestamp"))
        if ts is not None and first_ts is None:
            first_ts = ts
        if ts is not None and first_ts is not None:
            t = ts - first_ts
        else:
            t = last_t + 1 if last_t >= 0 else idx
        if t <= last_t:
            t = last_t + 1  # keep the axis strictly monotonic on duplicate stamps
        last_t = t
        time_seconds.append(t)

        hr.append(_int_or_none(rec.get("heart_rate")))
        speed = rec.get("enhanced_speed")
        if speed is None:
            speed = rec.get("speed")
        vel.append(_float_or_none(speed))
        altitude = rec.get("enhanced_altitude")
        if altitude is None:
            altitude = rec.get("altitude")
        alt.append(_float_or_none(altitude))
        cad.append(_int_or_none(rec.get("cadence")))
        dist.append(_float_or_none(rec.get("distance")))
        # GPS intentionally ignored:
        # rec.get("position_lat") and rec.get("position_long") are NOT processed

    return {
        "time_seconds": time_seconds,
        # "timestamp" = real per-record stamps; "ordinal" = records carried no
        # timestamps, so the axis is just the sample index (adapter spreads the
        # session's elapsed time over it, as v1 did).
        "time_axis": "timestamp" if first_ts is not None else "ordinal",
        "heartrate": hr,
        "velocity_ms": vel,
        "altitude": alt,
        "cadence": cad,
        "distance_m": dist,
        "_first_timestamp": first_ts,
    }


def _reject_multisport(session_msgs: list[dict[str, Any]]) -> None:
    """Refuse multisport files instead of gluing legs into one fake run."""
    sports = {str(s.get("sport") or "") for s in session_msgs}
    if "multisport" in sports or "transition" in sports or len(sports) > 1:
        raise FitParseError("multisport_unsupported", _FIT_MULTISPORT_PL)


def _sport_label(sport: str, sub_sport: str) -> tuple[str, bool]:
    """Map FIT sport/sub_sport to a display label + ``is_run`` flag."""
    if sport in _RUN_SPORTS:
        return _RUN_SUB_SPORT_LABELS.get(sub_sport, "TrailRun" if sport == "trail_running" else "Run"), True
    return sport.capitalize(), False


def _timer_pauses(events: list[dict[str, Any]], first_ts: int | None) -> list[dict[str, int]]:
    """Derive pauses (timer stop → next start) from FIT event messages."""
    if first_ts is None:
        return []
    pauses: list[dict[str, int]] = []
    stopped_at: int | None = None
    for ev in events:
        if str(ev.get("event")) != "timer":
            continue
        ts = _int_or_none(ev.get("timestamp"))
        if ts is None:
            continue
        et = str(ev.get("event_type") or "")
        if et.startswith("stop"):
            stopped_at = ts if stopped_at is None else stopped_at
        elif et == "start" and stopped_at is not None:
            duration = ts - stopped_at
            if duration > 0:
                pauses.append({"start_s": stopped_at - first_ts, "duration_s": duration})
            stopped_at = None
    return pauses


def _local_timezone_offset_s(activity_msgs: list[dict[str, Any]]) -> int | None:
    """Local UTC offset in seconds from the activity message, when both stamps exist."""
    if not activity_msgs:
        return None
    act = activity_msgs[0]
    ts = _int_or_none(act.get("timestamp"))
    local = _int_or_none(act.get("local_timestamp"))
    if ts is None or local is None:
        return None
    return local - ts


def _device_summary(messages: dict[str, Any]) -> dict[str, Any]:
    """Limited, serial-free source evidence from file_id / device_info."""
    file_id = (messages.get("file_id_mesgs") or [{}])[0]
    devices = messages.get("device_info_mesgs") or []
    primary = next(
        (d for d in devices if str(d.get("device_index") or "") in ("creator", "0")), None
    ) or (devices[0] if devices else {})
    manufacturer = file_id.get("manufacturer") or primary.get("manufacturer")
    product = file_id.get("product_name") or primary.get("product_name") \
        or file_id.get("garmin_product") or primary.get("garmin_product") \
        or file_id.get("product") or primary.get("product")
    return {
        "file_type": _str_or_none(file_id.get("type")),
        "manufacturer": _str_or_none(manufacturer),
        "product": _str_or_none(product),
        "time_created_utc": _fit_timestamp_to_iso(file_id.get("time_created")),
        "software_version": _str_or_none(primary.get("software_version")),
        # serial_number deliberately omitted (CLAUDE.md §.FIT File Data Model).
    }


def _fit_timestamp_to_iso(raw: Any) -> str | None:
    """Convert a FIT-epoch seconds value to an ISO-8601 UTC string."""
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw.astimezone(timezone.utc).isoformat()
    secs = _int_or_none(raw)
    if secs is None:
        return None
    try:
        return (_FIT_EPOCH + timedelta(seconds=secs)).isoformat()
    except OverflowError:
        return None


def _str_or_none(val: Any) -> str | None:
    return None if val is None else str(val)[:120]


def _float_or_none(val: Any) -> float | None:
    """Convert value to float or return None."""
    try:
        return float(val) if val is not None else None
    except (TypeError, ValueError):
        return None


def _int_or_none(val: Any) -> int | None:
    """Convert value to int or return None."""
    try:
        return int(val) if val is not None else None
    except (TypeError, ValueError):
        return None
