"""A CSV from another day must fail with an error that names both time ranges."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.analysis import AnalysisError, analyze_upload

ROOT = Path(__file__).resolve().parents[2]


def test_csv_from_another_day_names_run_and_csv_ranges():
    fit = (ROOT / "public" / "demo-run.fit").read_bytes()
    csv = (ROOT / "public" / "demo-glucose.csv").read_bytes().replace(b"2026-10-03T", b"2026-10-01T")
    with pytest.raises(AnalysisError) as caught:
        analyze_upload(fit, csv, "Europe/Warsaw")
    assert caught.value.code == "no_glucose_overlap"
    message = caught.value.detail_pl
    assert "Bieg: 03.10.2026" in message
    assert "Odczyty w CSV: 01.10.2026" in message
    assert "(Europe/Warsaw)" in message
    assert "strefę czasową" in message
