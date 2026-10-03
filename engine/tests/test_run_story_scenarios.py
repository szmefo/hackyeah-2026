"""Each committed synthetic scenario must tell its intended, distinct story."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.services.analysis import analyze_upload

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ROOT / "demos" / "synthetic-scenarios"
CAUSAL = re.compile(r"spowodował|z powodu|przez niski|wywołał|przyczyną był", re.IGNORECASE)
JARGON = re.compile(r"\bZ[1-5]\b|%\s*HR|HRmax|decoupling|kadencj[a-z]* spad|split", re.IGNORECASE)


def scenario(name: str) -> dict:
    folder = SCENARIOS / name
    return analyze_upload((folder / "bieg.fit").read_bytes(), (folder / "glukoza.csv").read_bytes(), "Europe/Warsaw")


def builtin() -> dict:
    return analyze_upload((ROOT / "public" / "demo-run.fit").read_bytes(),
                          (ROOT / "public" / "demo-glucose.csv").read_bytes(), "Europe/Warsaw", synthetic=True)


def factor_ids(moment: dict) -> set[str]:
    return {factor["id"] for factor in moment["factors"]}


ALL_RUNS = [pytest.param(lambda name=name: scenario(name), id=name)
            for name in ("01-niski-cukier-na-plaskim", "02-podbieg-cukier-w-normie",
                         "03-podbieg-i-niski-cukier", "04-luka-w-danych")] + [pytest.param(builtin, id="builtin")]


@pytest.mark.parametrize("load", ALL_RUNS)
def test_every_run_has_distinct_contract_compatible_moments(load):
    run = load()
    moments = run["moments"]
    assert moments, "at least one meaningful moment"
    assert [moment["id"] for moment in moments] == [f"moment-{index}" for index in range(1, len(moments) + 1)]
    assert [moment["minute"] for moment in moments] == sorted(moment["minute"] for moment in moments)
    # No two moments read the same: titles and narratives are unique.
    assert len({moment["title"] for moment in moments}) == len(moments)
    assert len({moment["narrative"] for moment in moments}) == len(moments)
    for moment in moments:
        assert isinstance(moment["separable"], bool)
        assert moment["windowEnd"] - moment["windowStart"] <= 20
        assert len(factor_ids(moment)) == len(moment["factors"]), "factor ids unique within a moment"
        for factor in moment["factors"]:
            assert factor["factId"] in run["factRegistry"]
            assert factor["factId"].startswith(moment["id"] + ".") or factor["factId"].startswith("run.")
        assert run["factRegistry"][f"{moment['id']}.glucose.minimum"]["value"] == moment["minGlucose"]
        assert run["factRegistry"][f"{moment['id']}.glucose.count"]["value"] == moment["readingCount"]
        assert not CAUSAL.search(moment["narrative"] + moment["title"])
        if not moment["separable"]:
            assert "rozdziel" in " ".join(moment["unknowns"])
    # Fact registry contains no orphaned moment ids.
    ids = {moment["id"] for moment in moments}
    assert {key.split(".")[0] for key in run["factRegistry"] if key.startswith("moment-")} == ids
    for sentence in run["strengths"]:
        assert not JARGON.search(sentence)


def test_01_low_glucose_on_flat_has_no_hill_factor():
    run = scenario("01-niski-cukier-na-plaskim")
    moment = min(run["moments"], key=lambda item: item["minGlucose"] if item["minGlucose"] is not None else 999)
    assert 44 <= moment["minute"] <= 56
    assert moment["minGlucose"] == run["facts"]["minGlucose"] < 70
    assert "low_glucose_nearby" in factor_ids(moment)
    assert all("uphill" not in factor_ids(item) for item in run["moments"])
    assert moment["separable"] is True
    assert "podbieg" in moment["narrative"].lower() and "nie było" in moment["narrative"].lower()


def test_02_hill_with_glucose_in_range_is_terrain_not_glucose():
    run = scenario("02-podbieg-cukier-w-normie")
    assert run["facts"]["below70Count"] == 0
    hill = next(moment for moment in run["moments"] if "uphill" in factor_ids(moment))
    assert 76 <= hill["minute"] <= 88
    assert not factor_ids(hill) & {"low_glucose_nearby", "below_range", "high_glucose_nearby", "no_glucose_data"}
    assert all(not factor_ids(item) & {"low_glucose_nearby", "below_range"} for item in run["moments"])
    assert hill["minGlucose"] >= 70
    assert run["factRegistry"][f"{hill['id']}.glucose.maximum"]["value"] <= 180
    assert hill["separable"] is True
    text = hill["narrative"]
    assert "teren się wznosił" in text and "w zakresie 70–180 mg/dL" in text
    assert "podbieg, nie spadek glukozy" in text and "nie dowód przyczyny" in text


def test_03_hill_and_low_together_are_not_separable():
    run = scenario("03-podbieg-i-niski-cukier")
    together = [moment for moment in run["moments"] if {"uphill", "low_glucose_nearby"} <= factor_ids(moment)]
    assert len(together) == 1, "one co-occurrence moment, not two copies of it"
    moment = together[0]
    assert 78 <= moment["minute"] <= 88
    assert moment["minGlucose"] == run["facts"]["minGlucose"] < 70
    assert moment["separable"] is False
    assert "nie pozwalają rozdzielić" in moment["narrative"]


def test_04_gap_is_unknown_and_never_separable():
    run = scenario("04-luka-w-danych")
    gap_moments = [moment for moment in run["moments"] if "no_glucose_data" in factor_ids(moment)]
    assert len(gap_moments) == 1
    moment = gap_moments[0]
    assert moment["readingCount"] == 0 and moment["minGlucose"] is None
    assert moment["separable"] is False
    assert moment["label"] == "Luka w danych"
    assert "Nie wiemy" in moment["narrative"]
    assert "pozwalają rozdzielić" not in moment["narrative"]
    assert any(gap["start"] <= moment["minute"] <= gap["end"] for gap in run["gaps"])
    assert not any("70 mg/dL" in sentence for sentence in run["strengths"]), "CGM did not cover this run"


def test_builtin_demo_has_gap_and_single_co_occurrence_moment():
    run = builtin()
    labels = [moment["label"] for moment in run["moments"]]
    assert labels.count("Dwa sygnały") == 1
    gap = next(moment for moment in run["moments"] if moment["readingCount"] == 0)
    assert gap["separable"] is False
    together = next(moment for moment in run["moments"] if {"uphill", "low_glucose_nearby"} <= factor_ids(moment))
    assert together["separable"] is False and together["minGlucose"] == 65


def test_data_gap_moment_is_never_separable_even_on_flat_ground():
    from tests.test_analysis import analyze

    run = analyze(gap=True)
    for moment in run["moments"]:
        if moment["readingCount"] == 0:
            assert moment["separable"] is False
            assert moment["label"] == "Luka w danych"


def test_strengths_are_genuine_or_empty():
    # 02-04 have no detector strengths; only 02 had full CGM without lows.
    assert scenario("03-podbieg-i-niski-cukier")["strengths"] == []
    assert scenario("04-luka-w-danych")["strengths"] == []
    assert scenario("02-podbieg-cukier-w-normie")["strengths"] == [
        "Odczyty sensora objęły cały bieg i żaden z nich nie był niższy niż 70 mg/dL."]
    flat = scenario("01-niski-cukier-na-plaskim")["strengths"]
    assert flat == ["Obie połowy biegu miały bardzo podobne tempo: równy, kontrolowany wysiłek od startu do mety."]
    for run in (scenario("01-niski-cukier-na-plaskim"), builtin()):
        assert all("Połączono czas" not in sentence for sentence in run["strengths"])
