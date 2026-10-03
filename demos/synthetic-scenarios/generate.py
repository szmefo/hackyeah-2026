"""Four synthetic FIT + Dexcom Clarity CSV pairs for Cukier w biegu demo.

All values are synthetic (seeded), not from any patient. Run with
engine/.venv/Scripts/python.exe demos/synthetic-scenarios/generate.py
"""
from __future__ import annotations

import copy, json, random, sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from build_fit_demo import build_fit  # noqa: E402

OUT = Path(__file__).resolve().parent
BASE = json.loads((REPO / "data" / "demo-run.json").read_text(encoding="utf-8"))
HEADER = "Timestamp (YYYY-MM-DDThh:mm:ss),Event Type,Glucose Value (mg/dL)\n"


def story(start: str, flat: bool = False, slow: tuple[int, int] | None = None) -> dict:
    s = copy.deepcopy(BASE)
    s["start"] = start
    for x in s["samples"]:
        m = x["minute"]
        if flat and x.get("altitude") is not None:
            x["altitude"] = 205 + round(2 * ((m // 7) % 3) - 2)  # gentle 203-207 m
            if 75 <= m <= 88:
                x["pace"] = 5.5 + 0.08 * ((m % 4) - 1.5)
                x["hr"] = min(x["hr"], 156) if x.get("hr") else x.get("hr")
        if slow and slow[0] <= m <= slow[1]:
            depth = 1 - abs((m - (slow[0] + slow[1]) / 2) / ((slow[1] - slow[0]) / 2))
            x["pace"] = round(5.55 + 1.5 * max(depth, 0.35), 3)
            if x.get("hr"):
                x["hr"] = x["hr"] + round(6 * depth)
    return s


def glucose(start: str, duration: int, curve, gaps=(), seed=1) -> str:
    rnd = random.Random(seed)
    t0 = datetime.fromisoformat(start).replace(tzinfo=None)
    rows = []
    for m in range(-30, duration + 16, 5):
        if any(a <= m <= b for a, b in gaps):
            continue
        v = round(curve(m) + rnd.gauss(0, 3))
        rows.append(f"{(t0 + timedelta(minutes=m)).isoformat()},EGV,{max(40, min(400, v))}")
    return HEADER + "\n".join(rows) + "\n"


def lerp(points):
    def f(m):
        for (a, va), (b, vb) in zip(points, points[1:]):
            if a <= m <= b:
                return va + (vb - va) * (m - a) / (b - a)
        return points[0][1] if m < points[0][0] else points[-1][1]
    return f


SCENARIOS = [
    ("01-niski-cukier-na-plaskim", "2026-09-12T08:00:00+02:00",
     dict(flat=True, slow=(44, 54)),
     lerp([(-30, 150), (0, 148), (25, 125), (40, 88), (48, 63), (55, 66), (65, 104), (94, 118), (110, 122)]), (),
     "Zwolnienie na płaskim odcinku (44.-54. min) zbiega się z odczytem ~63 mg/dL. Brak podbiegu."),
    ("02-podbieg-cukier-w-normie", "2026-09-19T08:30:00+02:00",
     dict(), lerp([(-30, 128), (20, 134), (50, 122), (80, 118), (94, 125), (110, 130)]), (),
     "Zwolnienie na podbiegu (~78.-86. min), glukoza stabilnie 115-135 mg/dL przez cały bieg."),
    ("03-podbieg-i-niski-cukier", "2026-09-26T09:00:00+02:00",
     dict(), lerp([(-30, 142), (10, 150), (45, 128), (70, 92), (80, 64), (86, 67), (94, 98), (110, 112)]), (),
     "Podbieg i odczyt ~64 mg/dL w tym samym oknie; dane nie rozdzielają wpływu. Pełne pokrycie CGM."),
    ("04-luka-w-danych", "2026-10-01T18:00:00+02:00",
     dict(), lerp([(-30, 135), (20, 140), (55, 118), (110, 115)]), ((58, 125),),
     "Sensor traci sygnał od ~58. minuty do końca biegu; podbieg bez odczytów glukozy."),
]

if __name__ == "__main__":
    readme = ["# Syntetyczne scenariusze demo — Cukier w biegu", "",
              "DANE SYNTETYCZNE. Wygenerowane skryptem `generate.py` (seed stały), nie pochodzą od pacjenta.",
              "Każdy katalog: `bieg.fit` + `glukoza.csv` (format Dexcom Clarity, czas lokalny Europe/Warsaw).", ""]
    for i, (name, start, opts, curve, gaps, note) in enumerate(SCENARIOS, 1):
        d = OUT / name; d.mkdir(exist_ok=True)
        s = story(start, **opts)
        (d / "bieg.fit").write_bytes(build_fit(s))
        (d / "glukoza.csv").write_text(glucose(start, s["durationMinutes"], curve, gaps, seed=100 + i), encoding="utf-8", newline="\n")
        readme.append(f"- **{name}** (start {start}): {note}")
    (OUT / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print("ok")

