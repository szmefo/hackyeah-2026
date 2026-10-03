"""Deterministic FIT fixtures for the Garmin pilot tests (in memory, GPS-free).

Built with ``garmin_fit_sdk.Encoder`` so every fixture is a GENUINE FIT file
(header CRC, file CRC, real message definitions), not a hand-crafted byte blob.
"""
from __future__ import annotations

import io
import zipfile
from datetime import datetime, timezone

from garmin_fit_sdk import Profile
from garmin_fit_sdk.encoder import Encoder
from garmin_fit_sdk.util import convert_datetime_to_timestamp

START = datetime(2026, 9, 5, 6, 30, 0, tzinfo=timezone.utc)
FIT_START = convert_datetime_to_timestamp(START)

MESG_NUM = Profile["mesg_num"]


def _fit_start_ts() -> int:
    return int(FIT_START)


def build_run_fit(
    *,
    seconds: int = 120,
    with_gps: bool = False,
    hr_gap: tuple[int, int] | None = None,
    pause: tuple[int, int] | None = None,
    manufacturer: str = "garmin",
    product_name: str | None = "Forerunner 965",
    sport: str = "running",
    sub_sport: str = "generic",
    with_device_info: bool = True,
    with_serial: bool = True,
    extra_sessions: list[str] | None = None,
    local_offset_s: int | None = 7200,
    start: datetime = START,
) -> bytes:
    """Encode a 1 Hz run with optional HR gap, timer pause and device metadata.

    Args:
        seconds: Number of 1 Hz record messages.
        hr_gap: ``(start_s, end_s)`` half-open window whose records carry NO
            heart_rate field at all (sensor dropout).
        pause: ``(stop_s, start_s)`` timer stop/start events.
        manufacturer: file_id manufacturer (``"garmin"`` or e.g. ``"development"``).
        product_name: product name string or None.
        sport / sub_sport: session sport labels.
        with_device_info: whether to emit a device_info message.
        with_serial: whether the file_id carries a serial number.
        extra_sessions: extra session sports to append (multisport fixture).
        local_offset_s: activity local_timestamp offset; None omits it.
        start: UTC start of the recording (file_id.time_created + session.start_time).
    """
    START = start  # noqa: N806 — shadow the module default for this build
    enc = Encoder()
    file_id = {
        "mesg_num": MESG_NUM["FILE_ID"],
        "type": "activity",
        "manufacturer": manufacturer,
        "time_created": START,
    }
    if product_name:
        file_id["product_name"] = product_name
    if with_serial:
        file_id["serial_number"] = 3412345678
    enc.write_mesg(file_id)

    if with_device_info:
        dev = {
            "mesg_num": MESG_NUM["DEVICE_INFO"],
            "timestamp": START,
            "device_index": "creator",
            "manufacturer": manufacturer,
            "software_version": 21.5,
        }
        if product_name:
            dev["product_name"] = product_name
        if with_serial:
            dev["serial_number"] = 3412345678
        enc.write_mesg(dev)

    enc.write_mesg({
        "mesg_num": MESG_NUM["EVENT"],
        "timestamp": START,
        "event": "timer",
        "event_type": "start",
    })

    from datetime import timedelta

    for s in range(seconds):
        rec = {
            "mesg_num": MESG_NUM["RECORD"],
            "timestamp": START + timedelta(seconds=s),
            "distance": float(s * 3.0),
            "enhanced_speed": 3.0 + (0.5 if s % 30 == 0 else 0.0),
            "enhanced_altitude": 300.0 + s * 0.1,
            "cadence": 85,
        }
        if with_gps:
            rec["position_lat"] = round((54.0 + s * 0.00001) * 2**31 / 180)
            rec["position_long"] = round((19.0 + s * 0.00001) * 2**31 / 180)
        in_gap = hr_gap is not None and hr_gap[0] <= s < hr_gap[1]
        if not in_gap:
            rec["heart_rate"] = 140 + (s % 10)
        if pause is not None and pause[0] < s <= pause[1]:
            # Watch paused: no records during the pause window.
            continue
        enc.write_mesg(rec)
        if pause is not None and s == pause[0]:
            enc.write_mesg({
                "mesg_num": MESG_NUM["EVENT"],
                "timestamp": START + timedelta(seconds=pause[0]),
                "event": "timer",
                "event_type": "stop_all",
            })
            enc.write_mesg({
                "mesg_num": MESG_NUM["EVENT"],
                "timestamp": START + timedelta(seconds=pause[1]),
                "event": "timer",
                "event_type": "start",
            })

    pause_len = (pause[1] - pause[0]) if pause else 0
    session = {
        "mesg_num": MESG_NUM["SESSION"],
        "timestamp": START + timedelta(seconds=seconds),
        "start_time": START,
        "sport": sport,
        "sub_sport": sub_sport,
        "total_elapsed_time": float(seconds),
        "total_timer_time": float(seconds - pause_len),
        "total_distance": float(seconds * 3.0),
        "total_ascent": int(seconds * 0.1),
    }
    enc.write_mesg(session)
    for extra in extra_sessions or []:
        enc.write_mesg({**session, "sport": extra})

    activity = {
        "mesg_num": MESG_NUM["ACTIVITY"],
        "timestamp": START + timedelta(seconds=seconds),
        "num_sessions": 1 + len(extra_sessions or []),
        "type": "manual",
        "event": "activity",
        "event_type": "stop",
        "total_timer_time": float(seconds - pause_len),
    }
    if local_offset_s is not None:
        activity["local_timestamp"] = START + timedelta(seconds=seconds + local_offset_s)
    enc.write_mesg(activity)
    return enc.close()


def zip_of(entries: dict[str, bytes], *, compression: int = zipfile.ZIP_DEFLATED) -> bytes:
    """Build an in-memory ZIP archive from ``{name: bytes}``."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=compression) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()
