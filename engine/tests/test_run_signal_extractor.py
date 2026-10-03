"""Snapshot tests for the pure run-signal extractor (#A, ADR 2026-06-02).

Imports ONLY ``app.services.run_signal_extractor`` — the module is pure (zero DB,
zero Anthropic), so this test file deliberately does NOT touch ``app.models`` or
``app.main``. That keeps it runnable in parallel with the UUID auth migration.

Fixture style mirrors ``test_training_analyzer.py`` SAMPLE_STREAMS: each profile
is a dict of positionally-aligned streams (``time_seconds``, ``pace_per_km``,
``altitude``, ``cadence``, ``heartrate``).

The critical Greg gate is ``test_mountain_uphill_absorbed_by_gap``: an uphill
slowdown must be absorbed by grade-adjusted pace and must NOT surface as a
false-positive CLIFF.
"""

from __future__ import annotations

import pytest

from app.services.run_signal_extractor import (
    MomentType,
    ProfileCtx,
    Severity,
    StrengthType,
    cumulative_distance_m,
    detect_pace_drop,
    extract_run_signals,
    grade_adjusted_pace,
)

# ---------------------------------------------------------------------------
# Profile context fixtures
# ---------------------------------------------------------------------------

# Age-formula resolution → medium confidence (data is present).
PROFILE_CTX = ProfileCtx(max_hr=190, max_hr_source="age_formula", age=30)
# Fallback resolution → low confidence (no max HR, no age).
PROFILE_CTX_DEFAULT = ProfileCtx(max_hr=190, max_hr_source="default")


# ---------------------------------------------------------------------------
# Stream fixtures (12 samples, one every 600 s = 10 min)
# ---------------------------------------------------------------------------

_TIME = [i * 600.0 for i in range(12)]

# 1. FLAT_CLEAN — even pace, flat altitude, stable HR + cadence.
FLAT_CLEAN = {
    "time_seconds": _TIME,
    "pace_per_km": [5.0, 5.02, 4.99, 5.01, 5.0, 5.0, 5.01, 4.99, 5.0, 5.02, 5.0, 5.01],
    "altitude": [100, 101, 100, 99, 100, 101, 100, 100, 101, 99, 100, 100],
    "cadence": [172, 172, 171, 172, 173, 172, 172, 171, 172, 172, 173, 172],
    "heartrate": [150, 151, 150, 150, 151, 150, 150, 151, 150, 150, 151, 150],
}

# 2. MOUNTAIN_UPHILL — an out-and-back: flat cruise, a sustained climb, then the
#    descent home. Raw pace on the climb drops ~28% vs the settled baseline (looks
#    like a bonk), but the climb is pure terrain — GAP flattens it back below
#    baseline so no CLIFF fires. HR + cadence steady throughout. Built for the
#    stabilized-baseline logic (#82): the first-half flat cruise IS the baseline,
#    the climb sits mid-run, the descent balances the split so no false fade.
MOUNTAIN_UPHILL = {
    "time_seconds": _TIME,
    "pace_per_km": [5.0, 5.0, 5.0, 5.0, 6.4, 6.4, 6.4, 6.4, 4.2, 4.2, 4.2, 4.2],
    "altitude": [100, 100, 100, 100, 280, 460, 640, 820, 640, 460, 280, 100],
    "cadence": [172, 172, 171, 172, 172, 172, 171, 172, 172, 172, 171, 172],
    "heartrate": [155, 156, 155, 155, 156, 155, 155, 156, 155, 155, 156, 155],
}

# 3. BONK — flat altitude, first half even, then a sustained ~22% pace collapse.
BONK = {
    "time_seconds": _TIME,
    "pace_per_km": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.9, 5.95, 6.0, 6.0, 6.05, 6.1],
    "altitude": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    "cadence": [172, 172, 172, 172, 172, 172, 170, 170, 169, 169, 168, 168],
    "heartrate": [150, 150, 150, 150, 150, 150, 151, 151, 150, 150, 151, 150],
}

# 4. DECOUPLE — constant pace + flat altitude, but HR drifts up in the 2nd half.
DECOUPLE = {
    "time_seconds": _TIME,
    "pace_per_km": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    "altitude": [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
    "cadence": [172, 172, 172, 172, 172, 172, 172, 172, 172, 172, 172, 172],
    "heartrate": [150, 150, 150, 150, 150, 150, 165, 166, 167, 168, 169, 170],
}


def _types(signals) -> list[MomentType]:
    return [m.type for m in signals.moments]


# ---------------------------------------------------------------------------
# 1. FLAT_CLEAN
# ---------------------------------------------------------------------------


def test_flat_clean_has_no_moments():
    """An even, flat, stable run produces zero moments."""
    signals = extract_run_signals(FLAT_CLEAN, PROFILE_CTX)
    assert signals.moments == []


def test_flat_clean_split_ratio_near_one():
    """FLAT_CLEAN second half ≈ first half → split_ratio ~1.0."""
    signals = extract_run_signals(FLAT_CLEAN, PROFILE_CTX)
    assert signals.split_ratio == pytest.approx(1.0, abs=0.03)


# ---------------------------------------------------------------------------
# 2. MOUNTAIN_UPHILL — the critical Greg gate
# ---------------------------------------------------------------------------


def test_mountain_uphill_absorbed_by_gap():
    """CRITICAL: an uphill slowdown must NOT surface as a false-positive CLIFF.

    GAP must absorb the climb. Control: raw ``detect_pace_drop`` (no GAP) DOES
    flag a CLIFF on the same fixture, proving the slowdown is real — but
    ``extract_run_signals`` (which runs detection on GAP) does NOT classify it
    as a bonk.
    """
    signals = extract_run_signals(MOUNTAIN_UPHILL, PROFILE_CTX)
    assert MomentType.CLIFF not in _types(signals)

    # Control: WITHOUT grade adjustment the same pace stream looks like a CLIFF...
    raw_moments = detect_pace_drop(
        MOUNTAIN_UPHILL["time_seconds"], MOUNTAIN_UPHILL["pace_per_km"]
    )
    assert any(m.type == MomentType.CLIFF for m in raw_moments), (
        "fixture sanity: raw pace must drop enough to trip a CLIFF without GAP"
    )

    # ...and WITH grade adjustment the exact same slowdown is absorbed — proving
    # GAP (not the corroboration gate) is what suppresses the false bonk here.
    gap = grade_adjusted_pace(
        MOUNTAIN_UPHILL["pace_per_km"],
        MOUNTAIN_UPHILL["altitude"],
        MOUNTAIN_UPHILL["time_seconds"],
    )
    gap_moments = detect_pace_drop(
        MOUNTAIN_UPHILL["time_seconds"], MOUNTAIN_UPHILL["pace_per_km"], gap_pace=gap
    )
    assert not any(m.type == MomentType.CLIFF for m in gap_moments), (
        "GAP must absorb the uphill slowdown so no CLIFF fires on the adjusted stream"
    )


def test_mountain_uphill_emits_grade_adjustment():
    """The material grade correction is surfaced as an informational moment."""
    signals = extract_run_signals(MOUNTAIN_UPHILL, PROFILE_CTX)
    assert MomentType.GRADE_ADJUSTMENT in _types(signals)


# ---------------------------------------------------------------------------
# 3. BONK
# ---------------------------------------------------------------------------


def test_bonk_flags_cliff_high():
    """A sustained flat-terrain collapse flags a high-severity CLIFF."""
    signals = extract_run_signals(BONK, PROFILE_CTX)
    cliffs = [m for m in signals.moments if m.type == MomentType.CLIFF]
    assert cliffs, "BONK must produce a CLIFF moment"
    assert cliffs[0].severity == Severity.HIGH


def test_bonk_flags_positive_split():
    """A bonked second half is slower → POSITIVE_SPLIT."""
    signals = extract_run_signals(BONK, PROFILE_CTX)
    assert MomentType.POSITIVE_SPLIT in _types(signals)
    assert signals.split_ratio is not None and signals.split_ratio > 1.05


# ---------------------------------------------------------------------------
# 4. DECOUPLE
# ---------------------------------------------------------------------------


def test_decouple_flags_decoupling():
    """Steady pace + rising HR → DECOUPLING with decoupling_pct > 5%."""
    signals = extract_run_signals(DECOUPLE, PROFILE_CTX)
    assert MomentType.DECOUPLING in _types(signals)
    assert signals.decoupling_pct is not None and signals.decoupling_pct > 0.05


def test_decouple_no_false_cliff_or_split():
    """A pure decoupling run must not also fire CLIFF or POSITIVE_SPLIT."""
    signals = extract_run_signals(DECOUPLE, PROFILE_CTX)
    types = _types(signals)
    assert MomentType.CLIFF not in types
    assert MomentType.POSITIVE_SPLIT not in types


# ---------------------------------------------------------------------------
# Confidence + semantic HR zone keys
# ---------------------------------------------------------------------------


def test_confidence_low_when_max_hr_source_default():
    """max_hr_source == 'default' forces low confidence (Za mało danych)."""
    signals = extract_run_signals(FLAT_CLEAN, PROFILE_CTX_DEFAULT)
    assert signals.confidence == Severity.LOW


def test_confidence_not_low_when_max_hr_resolved():
    """A resolved max HR + adequate duration keeps confidence above low."""
    signals = extract_run_signals(FLAT_CLEAN, PROFILE_CTX)
    assert signals.confidence != Severity.LOW


def test_hr_zones_use_semantic_keys_not_z1():
    """HR zones use semantic keys (recovery/endurance/...), never raw Z1/Z2."""
    signals = extract_run_signals(FLAT_CLEAN, PROFILE_CTX)
    assert set(signals.hr_zones.keys()) == {
        "recovery",
        "endurance",
        "tempo",
        "threshold",
        "max",
    }
    for key in signals.hr_zones:
        assert not key.upper().startswith("Z"), f"forbidden raw zone label: {key}"


def test_schema_version_present():
    """RunSignals carries schema_version=1 so the JSON shape can evolve."""
    signals = extract_run_signals(FLAT_CLEAN, PROFILE_CTX)
    assert signals.schema_version == 1


# ---------------------------------------------------------------------------
# Empty / degenerate input safety
# ---------------------------------------------------------------------------


def test_empty_streams_no_crash():
    """Empty streams produce an empty, low-confidence RunSignals without raising."""
    signals = extract_run_signals({}, PROFILE_CTX_DEFAULT)
    assert signals.moments == []
    assert signals.duration_s == 0
    assert signals.confidence == Severity.LOW


# ---------------------------------------------------------------------------
# #82 — Run Replay analysis fixes
# ---------------------------------------------------------------------------

# Long, well-run marathon: 42 samples one every ~5 min (≈3h30). Fast-ish settle,
# then a genuinely NEGATIVE split (2nd half faster), flat HR (~0% drift), stable
# cadence. This is the run that used to get "forma runęła na km 1-3" because the
# quick opening km set a too-fast baseline. It must produce NO cliff and ≥1
# strength.
_MARATHON_N = 42
_MARATHON_TIME = [i * 300.0 for i in range(_MARATHON_N)]
# First 3 km slightly quick (5:05 → settles to 5:00), second half clearly faster
# (~4:45). No collapse anywhere — a textbook negative split.
_MARATHON_PACE = (
    [5.05, 5.03]
    + [5.0] * 19            # settled first half at 5:00
    + [4.75] * 21           # negative split — steady 2nd half a solid ~5% faster
)
_MARATHON_ALT = [100.0 + (i % 3) for i in range(_MARATHON_N)]  # flat, tiny noise
_MARATHON_CAD = [174.0 - (i % 2) for i in range(_MARATHON_N)]  # held cadence
_MARATHON_HR = [150.0 + (i % 2) for i in range(_MARATHON_N)]   # flat HR → ~0 drift
# Native GPS distance stream: cumulative metres, ~8.4 km over each 5-min sample
# at ~5:00/km would be 1000 m per 5 min → build a realistic monotone stream.
_MARATHON_DIST = [round(i * 1000.0, 1) for i in range(_MARATHON_N)]

MARATHON_NEGATIVE_SPLIT = {
    "time_seconds": _MARATHON_TIME,
    "pace_per_km": _MARATHON_PACE,
    "altitude": _MARATHON_ALT,
    "cadence": _MARATHON_CAD,
    "heartrate": _MARATHON_HR,
    "distance_m": _MARATHON_DIST,
}


def test_good_marathon_has_no_false_cliff_headline():
    """A 42-sample negative-split run with ~0% drift must NOT read as a collapse.

    The core #82 regression: every run got "forma runęła na km 1-3" from a
    fast-start baseline. With a settled baseline + corroboration gate, a
    well-executed run produces zero CLIFF and zero POSITIVE_SPLIT.
    """
    signals = extract_run_signals(MARATHON_NEGATIVE_SPLIT, PROFILE_CTX)
    types = _types(signals)
    assert MomentType.CLIFF not in types, f"false CLIFF on a good run: {types}"
    assert MomentType.POSITIVE_SPLIT not in types


def test_good_marathon_shows_a_strength():
    """A good run always surfaces at least one 'co poszło dobrze' (#82 point 3)."""
    signals = extract_run_signals(MARATHON_NEGATIVE_SPLIT, PROFILE_CTX)
    assert len(signals.strengths) >= 1
    strength_types = {s.type for s in signals.strengths}
    # 2nd half faster → the headline strength is a negative split.
    assert StrengthType.NEGATIVE_SPLIT in strength_types


def test_bonk_moment_km_matches_real_distance_not_time_over_360():
    """The CLIFF km label follows real GPS distance, not the old time/360 guess.

    BONK collapses in its 2nd half. With an explicit distance stream the moment's
    ``km`` must equal the cumulative distance there — and must differ from the old
    ``round(mid_time / 360)`` hack.
    """
    # Give BONK a native distance stream: 1200 m per 600 s sample (≈5:00/km).
    bonk = dict(BONK)
    bonk["distance_m"] = [round(i * 1200.0, 1) for i in range(len(BONK["time_seconds"]))]
    signals = extract_run_signals(bonk, PROFILE_CTX)
    cliffs = [m for m in signals.moments if m.type == MomentType.CLIFF]
    assert cliffs, "BONK must still flag a CLIFF"
    cliff = cliffs[0]
    assert cliff.km is not None and cliff.distance_m is not None
    # The collapse starts around sample 6 → ~7200 m → ~7.2 km.
    assert cliff.km == pytest.approx(7.2, abs=0.5)
    # The old hack would have read mid_time/360 ≈ a very different number.
    old_hack_km = round(((cliff.start_s + cliff.end_s) / 2) / 360)
    assert cliff.km != old_hack_km


def test_cumulative_distance_integrates_pace_when_no_distance_stream():
    """Without a native distance stream, distance is integrated from pace+time."""
    # 5:00/km for 600 s = 2000 m per sample.
    time_s = [0.0, 600.0, 1200.0]
    pace = [5.0, 5.0, 5.0]
    cum = cumulative_distance_m(pace, time_s)
    assert cum[0] == 0.0
    assert cum[1] == pytest.approx(2000.0, abs=20)
    assert cum[2] == pytest.approx(4000.0, abs=40)


def test_uncorroborated_pace_wobble_is_not_a_cliff():
    """A single slow stretch with no cardiac drift and no positive split is not a bonk.

    One slow km in the middle (traffic light, photo stop) surrounded by steady
    pace — HR flat, both halves even. It must NOT headline as a collapse.
    """
    wobble = {
        "time_seconds": _TIME,
        # One slow sample at idx 6, otherwise a dead-even 5:00 run.
        "pace_per_km": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 6.2, 5.0, 5.0, 5.0, 5.0, 5.0],
        "altitude": [100] * 12,
        "cadence": [172] * 12,
        "heartrate": [150] * 12,  # perfectly flat → no decoupling
    }
    signals = extract_run_signals(wobble, PROFILE_CTX)
    assert MomentType.CLIFF not in _types(signals), (
        "a lone pace wobble with no corroboration must not be a CLIFF"
    )


def test_cliff_caught_late_in_run_not_the_warmup():
    """A collapse in the final third is found — the scan covers the whole run.

    The old code returned on the FIRST drop window it saw and used a fast-start
    baseline, so it caught the warmup, not the bonk. Here the run cruises evenly
    then collapses at the very end; the CLIFF must sit in the late portion.
    """
    late_bonk = {
        "time_seconds": _TIME,
        "pace_per_km": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.9, 6.1, 6.2, 6.3],
        "altitude": [100] * 12,
        "cadence": [172, 172, 172, 172, 172, 172, 172, 171, 169, 168, 167, 166],
        "heartrate": [150, 150, 150, 150, 150, 150, 150, 150, 151, 151, 152, 152],
    }
    signals = extract_run_signals(late_bonk, PROFILE_CTX)
    cliffs = [m for m in signals.moments if m.type == MomentType.CLIFF]
    assert cliffs, "a late collapse must still be caught"
    # The collapse is in the last third → start_s well past the warmup.
    assert cliffs[0].start_s >= _TIME[7], "CLIFF must be in the late run, not the warmup"
