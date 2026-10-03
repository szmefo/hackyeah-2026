"""Parser v2 guards (ADR 2026-09-12): aligned samples, pauses, sport, evidence.

The alignment test is the FAIL→PASS guard for this card: on the v1 parser a
record without ``heart_rate`` was simply skipped in the HR list, so every
later HR reading shifted one index earlier relative to pace/time. The
assertion below reads HR *by position* — exactly how ``detect_decoupling`` and
moment slicing read it — and demands that the sample at second 50 (inside the
gap) is ``None`` and the sample at second 60 (after the gap) is the real 140.
"""
from __future__ import annotations

import pytest

from app.services.fit_adapter import adapt_fit_activity_to_streams
from app.services.fit_parser import FitParseError, parse_fit_activity, parse_fit_bytes
from tests.fit_fixtures import build_run_fit


@pytest.fixture(scope="module")
def parsed_gap() -> dict:
    return parse_fit_activity(build_run_fit(seconds=120, hr_gap=(40, 60)))


def test_missing_hr_stays_null_at_the_right_second(parsed_gap):
    samples = parsed_gap["samples"]
    n = len(samples["time_seconds"])
    assert n == 120
    assert all(len(samples[k]) == n for k in ("heartrate", "velocity_ms", "altitude", "cadence"))
    assert samples["time_seconds"][60] == 60
    assert samples["heartrate"][50] is None           # inside the dropout
    assert samples["heartrate"][60] == 140 + (60 % 10)  # first reading after it
    assert samples["heartrate"][39] == 140 + (39 % 10)
    # A missing reading is never a fabricated zero.
    assert 0 not in samples["heartrate"]


def test_adapter_keeps_hr_aligned_with_pace_and_time(parsed_gap):
    streams = adapt_fit_activity_to_streams(parsed_gap)
    assert len(streams["heartrate"]) == len(streams["pace_per_km"]) == len(streams["time_seconds"])
    assert streams["heartrate"][50] is None
    assert streams["heartrate"][60] == 140
    assert streams["time_seconds"][60] == 60
    assert streams["pace_per_km"][60] > 0


def test_v1_compact_streams_are_still_emitted_for_old_readers(parsed_gap):
    assert parsed_gap["streams"]["heartrate"]["original_size"] == 100
    assert parsed_gap["summary_stats"]["has_heartrate"] is True


def test_pause_is_reported_and_elapsed_exceeds_moving():
    parsed = parse_fit_activity(build_run_fit(seconds=300, pause=(100, 160)))
    assert parsed["pauses"] == [{"start_s": 100, "duration_s": 60}]
    assert parsed["elapsed_time"] == 300
    assert parsed["moving_time"] == 240
    # Time axis is real timestamps: the record after the pause sits at 161 s.
    t = parsed["samples"]["time_seconds"]
    assert 161 in t and 130 not in t


def test_sport_labels_and_timezone():
    trail = parse_fit_activity(build_run_fit(seconds=10, sport="running", sub_sport="trail"))
    assert trail["type"] == "TrailRun" and trail["is_run"] is True
    tread = parse_fit_activity(build_run_fit(seconds=10, sub_sport="treadmill"))
    assert tread["type"] == "Treadmill"
    ride = parse_fit_activity(build_run_fit(seconds=10, sport="cycling"))
    assert ride["is_run"] is False
    assert trail["local_timezone_offset_s"] == 7200
    assert trail["start_time_utc"] == "2026-09-05T06:30:00+00:00"


def test_multisport_is_refused_not_glued():
    with pytest.raises(FitParseError) as exc:
        parse_fit_activity(build_run_fit(seconds=10, extra_sessions=["cycling"]))
    assert exc.value.code == "multisport_unsupported"
    with pytest.raises(FitParseError):
        parse_fit_activity(build_run_fit(seconds=10, sport="multisport"))


def test_http_wrapper_maps_typed_error_to_422_with_code():
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        parse_fit_bytes(build_run_fit(seconds=10, extra_sessions=["cycling"]))
    assert exc.value.status_code == 422
    assert exc.value.headers["X-FIT-Error-Code"] == "multisport_unsupported"


def test_device_summary_has_no_serial_and_no_gps():
    parsed = parse_fit_activity(build_run_fit(seconds=5))
    dev = parsed["device"]
    assert dev["manufacturer"] == "garmin"
    assert dev["product"] == "Forerunner 965"
    assert dev["file_type"] == "activity"
    assert "serial" not in " ".join(dev.keys())
    flat = str(parsed)
    assert "serial_number" not in flat
    assert "position_lat" not in flat and "position_long" not in flat
