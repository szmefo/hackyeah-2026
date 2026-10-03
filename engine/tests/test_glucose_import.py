"""Independent import guards: preserve units, timezone, flags and unknowns."""
from datetime import datetime, timezone

import pytest

from app.services.glucose import GlucoseParseError, parse_glucose_csv

HEADER = "Timestamp (YYYY-MM-DDThh:mm:ss),Event Type,Glucose Value (mg/dL)\n"


def csv_bytes(*rows: str) -> bytes:
    return (HEADER + "\n".join(rows) + "\n").encode()


def test_local_timestamp_uses_selected_timezone_and_only_egv():
    readings = parse_glucose_csv(csv_bytes(
        "2026-10-03T08:30:00,EGV,137",
        "2026-10-03T08:31:00,Carbs,40",
        "2026-10-03T08:32:00,Insulin,4",
    ))
    assert len(readings) == 1
    assert readings[0].timestamp == datetime(2026, 10, 3, 6, 30, tzinfo=timezone.utc)
    assert readings[0].value == 137


def test_offset_timestamps_do_not_receive_another_timezone_shift():
    readings = parse_glucose_csv(csv_bytes("2026-10-03T06:30:00Z,EGV,137"))
    assert readings[0].timestamp.hour == 6


def test_utf8_bom_and_out_of_order_rows_are_supported():
    readings = parse_glucose_csv(b"\xef\xbb\xbf" + csv_bytes(
        "2026-10-03T08:35:00,EGV,143", "2026-10-03T08:30:00,EGV,137"))
    assert [reading.value for reading in readings] == [137, 143]


def test_identical_duplicates_collapse():
    readings = parse_glucose_csv(csv_bytes(*["2026-10-03T08:30:00,EGV,137"] * 2))
    assert len(readings) == 1


def test_conflicting_duplicates_are_rejected():
    with pytest.raises(GlucoseParseError):
        parse_glucose_csv(csv_bytes("2026-10-03T08:30:00,EGV,137", "2026-10-03T08:30:00,EGV,65"))


def test_low_high_are_flags_without_invented_threshold_numbers():
    readings = parse_glucose_csv(csv_bytes(
        "2026-10-03T08:30:00,EGV,Low", "2026-10-03T08:35:00,EGV,High"))
    assert [reading.value for reading in readings] == [None, None]
    assert [reading.flag for reading in readings] == ["below_range", "above_range"]


@pytest.mark.parametrize("stamp", ["2026-10-25T02:30:00", "2026-03-29T02:30:00"])
def test_dst_ambiguous_and_nonexistent_local_times_are_rejected(stamp):
    with pytest.raises(GlucoseParseError):
        parse_glucose_csv(csv_bytes(f"{stamp},EGV,137"))


def test_explicit_offset_resolves_dst_ambiguity():
    readings = parse_glucose_csv(csv_bytes("2026-10-25T02:30:00+02:00,EGV,137"))
    assert readings[0].timestamp.hour == 0


@pytest.mark.parametrize("payload", [
    b"", b"random,columns\n1,2", b"\xff\xfe\x00broken",
    csv_bytes("not-a-date,EGV,137"), csv_bytes("2026-10-03,EGV,137"),
    csv_bytes("2026-10-03T08:30:00,EGV,nonsense"),
    csv_bytes("2026-10-03T08:30:00,Carbs,20"),
    b"Timestamp (YYYY-MM-DDThh:mm:ss),Event Type,Glucose Value\n2026-10-03T08:30:00,EGV,7.2",
])
def test_malformed_or_non_supported_data_rejected_with_typed_error(payload):
    with pytest.raises(GlucoseParseError) as error:
        parse_glucose_csv(payload)
    assert error.value.code and error.value.detail_pl


def test_unknown_timezone_is_actionable_typed_error():
    with pytest.raises(GlucoseParseError):
        parse_glucose_csv(csv_bytes("2026-10-03T08:30:00,EGV,137"), "Not/AZone")


def test_declared_mmol_is_normalized_to_mg_without_threshold_unit_confusion():
    payload = b"Timestamp (YYYY-MM-DDThh:mm:ss),Event Type,Glucose Value (mmol/L)\n2026-10-03T08:30:00,EGV,7.2"
    reading = parse_glucose_csv(payload)[0]
    assert reading.value == pytest.approx(129.731, abs=0.01)
    assert reading.source_unit == "mmol/L"
