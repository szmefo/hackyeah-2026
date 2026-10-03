"""Independent end-to-end FIT/CGM evidence tests, using new synthetic FITs."""
from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from app.services.analysis import AnalysisError, analyze_upload
from app.services.fit_parser import FitParseError
from app.services.glucose import GlucoseParseError

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("hackyeah_fit_demo", ROOT / "scripts" / "build_fit_demo.py")
_generator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_generator)
build_fit = _generator.build_fit
HEADER = "Timestamp (YYYY-MM-DDThh:mm:ss),Event Type,Glucose Value (mg/dL)\n"


def story(*, uphill=False, missing_hr=False, timestamps=True):
    samples = []
    for minute in range(61):
        samples.append({
            "minute": minute, "pace": 5 if minute < 28 else 7,
            "hr": None if missing_hr and 25 <= minute <= 35 else 140,
            "altitude": 200 + (max(0, min(minute - 25, 10)) * 5 if uphill else 0),
            "distanceKm": minute * 0.17,
        })
    return {"start": "2026-10-03T08:30:00+02:00", "durationMinutes": 60,
            "distanceKm": 10.2, "samples": samples}


def glucose_csv(*, low=False, gap=False, flags=False):
    start = datetime(2026, 10, 3, 8, 30)
    rows = []
    for minute in range(0, 61, 5):
        if gap and 20 <= minute <= 40:
            continue
        value = 65 if low and minute == 30 else 68 if low and minute == 35 else 130
        if flags and minute == 30:
            value = "Low"
        rows.append(f"{(start + timedelta(minutes=minute)).isoformat()},EGV,{value}")
    return (HEADER + "\n".join(rows) + "\n").encode()


def analyze(**options):
    run = story(uphill=options.get("uphill", False), missing_hr=options.get("missing_hr", False))
    return analyze_upload(build_fit(run), glucose_csv(low=options.get("low", False),
                          gap=options.get("gap", False), flags=options.get("flags", False)), synthetic=True)


def moment_near(run, minute=30):
    return min(run["moments"], key=lambda moment: abs(moment["minute"] - minute))


def test_public_pair_has_real_timing_and_expected_synthetic_facts():
    fixture = (ROOT / "public" / "demo-run.fit").read_bytes()
    result = analyze_upload(fixture, (ROOT / "public" / "demo-glucose.csv").read_bytes(), synthetic=True)
    assert result["schemaVersion"] == 1 and result["synthetic"] is True
    assert result["start"] == "2026-10-03T08:30:00+02:00"
    assert result["durationMinutes"] == 94
    assert result["distanceKm"] == pytest.approx(16.7)
    assert result["facts"]["minGlucose"] == 65
    assert result["facts"]["below70Count"] == 2
    assert result["facts"]["below54Count"] == 0
    assert result["facts"]["readingCount"] == 16
    assert result["facts"]["coveredMinutes"] == 69
    assert result["facts"]["coveragePct"] == 73
    for key, value in {"kind": "synthetic", "engineUsed": True, "clinicalValidation": False}.items():
        assert result["provenance"][key] == value
    assert len(result["samples"]) >= 90
    assert result["factRegistry"]
    for moment in result["moments"]:
        for factor in moment["factors"]:
            assert factor["factId"] in result["factRegistry"]


def test_a_flat_low_has_low_readings_without_uphill_claim():
    run = analyze(low=True)
    selected = moment_near(run)
    assert selected["minGlucose"] == 65
    assert selected["altitudeChange"] == 0
    assert run["facts"]["below70Count"] == 2


def test_b_uphill_normal_does_not_invent_low_glucose():
    run = analyze(uphill=True)
    assert run["facts"]["below70Count"] == 0
    selected = moment_near(run)
    assert selected["minGlucose"] == 130
    assert selected["altitudeChange"] > 0


def test_c_uphill_and_low_do_not_separate_cooccurring_causes():
    selected = moment_near(analyze(uphill=True, low=True))
    assert selected["minGlucose"] == 65
    assert selected["altitudeChange"] > 0
    assert selected["separable"] is False
    assert len(selected["factors"]) >= 2


def test_d_gap_has_unknown_minimum_and_no_glucose_line_bridge():
    run = analyze(gap=True)
    selected = moment_near(run)
    assert selected["readingCount"] == 0
    assert selected["minGlucose"] is None
    assert selected["unknowns"]
    for segment in run["glucoseSegments"]:
        assert all(right["minute"] - left["minute"] <= 15 for left, right in zip(segment, segment[1:]))
        assert not (segment[0]["minute"] < 30 < segment[-1]["minute"])


def test_missing_hr_is_null_at_same_timestamp():
    run = analyze(missing_hr=True)
    samples = {point["minute"]: point for point in run["samples"]}
    assert samples[30]["hr"] is None
    assert samples[36]["hr"] == 140
    assert all(point["hr"] != 0 for point in run["samples"])


def test_low_flag_is_not_counted_as_numeric_40_and_breaks_chart():
    run = analyze(flags=True)
    assert run["facts"]["below70Count"] == 0
    assert run["facts"]["minGlucose"] == 130
    assert {item["flag"] for item in run["glucoseFlags"]} == {"below_range"}
    for segment in run["glucoseSegments"]:
        assert not (segment[0]["minute"] < 30 < segment[-1]["minute"])


@pytest.mark.parametrize("sport", ["cycling", "swimming"])
def test_non_running_fit_is_rejected(sport):
    with pytest.raises(AnalysisError):
        analyze_upload(build_fit(story(), sport=sport), glucose_csv())


def test_missing_actual_record_timing_is_not_fabricated_for_alignment():
    with pytest.raises(AnalysisError):
        analyze_upload(build_fit(story(), timestamps=False), glucose_csv())


def test_corrupt_fit_returns_typed_failure():
    with pytest.raises((AnalysisError, FitParseError)):
        analyze_upload(b"not a real FIT", glucose_csv())


def test_patient_source_is_not_labelled_as_synthetic_without_explicit_choice():
    run = analyze_upload(build_fit(story()), glucose_csv())
    assert run["synthetic"] is False
    assert run["provenance"]["kind"] == "uploaded"


def test_no_gps_device_serial_or_raw_upload_in_result():
    result = json.dumps(analyze(), ensure_ascii=False)
    assert "position_lat" not in result and "position_long" not in result
    assert "serial_number" not in result and "raw_fit" not in result


def test_csv_wholly_outside_run_has_actionable_failure():
    payload = (HEADER + "2025-01-01T08:30:00,EGV,130\n").encode()
    with pytest.raises((AnalysisError, GlucoseParseError)):
        analyze_upload(build_fit(story()), payload)


def test_session_start_and_delayed_first_record_are_not_shifted():
    activity = story()
    activity["samples"] = activity["samples"][10:]
    run = analyze_upload(build_fit(activity), glucose_csv())
    assert run["samples"][0]["minute"] == 10
    assert run["start"] == "2026-10-03T08:30:00+02:00"
    assert run["glucose"][0]["minute"] == 0


def test_partly_missing_record_timestamps_are_not_assumed_ordinal():
    with pytest.raises(AnalysisError):
        analyze_upload(build_fit(story(), omit_timestamp_minutes={30}), glucose_csv())


def test_missing_altitude_stays_unknown_without_fake_flat_terrain():
    activity = story()
    for point in activity["samples"]:
        point["altitude"] = None
    run = analyze_upload(build_fit(activity), glucose_csv())
    assert all(point["altitude"] is None for point in run["samples"])
    assert all(moment["altitudeChange"] is None for moment in run["moments"])
    assert all(moment["altitudeAscent"] is None for moment in run["moments"])


def test_leading_and_trailing_unobserved_glucose_are_visible_gaps():
    start = datetime(2026, 10, 3, 8, 30)
    rows = [f"{(start + timedelta(minutes=minute)).isoformat()},EGV,130" for minute in range(10, 51, 5)]
    run = analyze_upload(build_fit(story()), (HEADER + "\n".join(rows)).encode())
    assert run["facts"]["coveredMinutes"] == 40
    assert any(gap["start"] == 0 and gap["end"] == 10 for gap in run["gaps"])
    assert any(gap["start"] == 50 and gap["end"] == 60 for gap in run["gaps"])


def test_public_fit_fixture_rebuild_is_byte_identical():
    source = json.loads((ROOT / "data" / "demo-run.json").read_text(encoding="utf-8"))
    assert build_fit(source) == (ROOT / "public" / "demo-run.fit").read_bytes()


def test_watch_recording_gap_is_rendered_as_missing_channels():
    activity = story()
    activity["samples"] = [point for point in activity["samples"] if not 25 <= point["minute"] <= 35]
    run = analyze_upload(build_fit(activity), glucose_csv())
    middle = [point for point in run["samples"] if 25 <= point["minute"] <= 35]
    assert middle and all(point["pace"] is None and point["hr"] is None for point in middle)
    selected = moment_near(run)
    if 25 <= selected["minute"] <= 35:
        assert selected["pace"] is None and selected["hr"] is None


def test_only_range_flags_never_produce_numeric_minimum_or_count():
    rows = [f"2026-10-03T08:{minute:02}:00,EGV,Low" for minute in (30, 35, 40, 45, 50, 55)]
    run = analyze_upload(build_fit(story()), (HEADER + "\n".join(rows)).encode())
    assert run["facts"]["readingCount"] == 0 and run["facts"]["minGlucose"] is None
    assert run["facts"]["coveragePct"] == 0
    assert run["glucose"] == [] and run["glucoseSegments"] == []
    assert run["facts"]["belowRangeCount"] == 6


def test_model_pattern_facts_come_from_measured_window_and_baseline():
    payload = (HEADER + "2026-10-03T08:55:00,EGV,130\n"
               "2026-10-03T09:00:00,EGV,65\n2026-10-03T09:05:00,EGV,90\n").encode()
    run = analyze_upload(build_fit(story()), payload)
    selected = moment_near(run)
    prefix = selected["id"]
    registry = run["factRegistry"]
    assert registry[f"{prefix}.glucose.first"]["value"] == 130
    assert registry[f"{prefix}.glucose.last"]["value"] == 90
    assert registry[f"{prefix}.glucose.delta"]["value"] == -40
    assert registry[f"{prefix}.pace.firstHalf.average"]["value"] == pytest.approx(5.4, abs=0.01)
    assert registry[f"{prefix}.pace.secondHalf.average"]["value"] == pytest.approx(7, abs=0.01)
    assert registry[f"{prefix}.pace.baseline.average"]["value"] == pytest.approx(5.8, abs=0.01)
    assert registry[f"{prefix}.pace.changeVsBaseline"]["value"] == pytest.approx(1.2, abs=0.01)


def test_one_glucose_point_does_not_fabricate_trend_or_coverage():
    payload = (HEADER + "2026-10-03T09:00:00,EGV,65\n").encode()
    run = analyze_upload(build_fit(story()), payload)
    selected = moment_near(run)
    assert selected["readingCount"] == 1
    assert run["factRegistry"][f"{selected['id']}.glucose.delta"]["value"] is None
    assert run["facts"]["coveragePct"] == 0


def test_uphill_returning_to_same_height_is_not_hidden_by_zero_net_change():
    activity = story()
    heights = {25: 200, 26: 210, 27: 220, 28: 234, 29: 225, 30: 215, 31: 205, 32: 200}
    for point in activity["samples"]:
        point["altitude"] = heights.get(point["minute"], 200)
    run = analyze_upload(build_fit(activity), glucose_csv(low=True))
    selected = moment_near(run)
    assert selected["altitudeChange"] == 0
    assert selected["altitudeAscent"] == 34
    assert selected["separable"] is False
    factor = next(item for item in selected["factors"] if item["id"] == "uphill")
    assert factor["factId"] == f"{selected['id']}.altitude.ascent"
    assert run["factRegistry"][factor["factId"]]["value"] == 34


@pytest.mark.parametrize("gap_kind", ["altitude", "records"])
def test_ascent_does_not_join_a_jump_across_missing_measurements(gap_kind):
    activity = story()
    for point in activity["samples"]:
        point["altitude"] = 200 if point["minute"] <= 25 else 230
        if gap_kind == "altitude" and 26 <= point["minute"] <= 29:
            point["altitude"] = None
    if gap_kind == "records":
        activity["samples"] = [point for point in activity["samples"] if not 26 <= point["minute"] <= 29]
    run = analyze_upload(build_fit(activity), glucose_csv(low=True))
    selected = moment_near(run)
    assert selected["altitudeChange"] == 30
    assert selected["altitudeAscent"] == 0
    assert run["factRegistry"][f"{selected['id']}.altitude.partial"]["value"] == "yes"
    assert not any(factor["id"] == "uphill" for factor in selected["factors"])
    assert selected["separable"] is False
