# Phase 1 review — 2026-10-03

Recorded at 2026-10-03T13:42:19+02:00, Europe/Warsaw. Human product review pending.

## Delivered

https://cukier-w-biegu.vercel.app

Selected Opowieść design; desktop/phone run page; SVG glucose/pace/HR/terrain on a
shared axis; three selectable moments; explicit missing CGM interval; facts, unknowns
and clinician questions; temporary observations; run list/source information;
sample CSV; clinician brief and browser print action/A4 styles.

All activity/glucose values are synthetic. This is a working UI/journey prototype,
not real FIT/CSV analysis or clinical validation. No application model or health-data
persistence. Latest owner AI direction is recorded in AI_INTERPRETATION.md.

## Executed checks

- `npm run check`: typecheck and ESLint passed on the final mobile code.
- `npm run build`: all four page routes and health handler built successfully locally.
- Vercel clean remote install/build succeeded, and final deployment is READY:
  `dpl_9X2jZZ2EGwJLyXifnBxufts26VFH`, from web artifact of source `9523dd9`.
- Before adaptation: original signal tests, 19 passed.
- After adaptation and isolated dependencies: `cd engine` then
  `.venv/Scripts/python.exe -m pytest tests -q`: 27 passed.
- `python scripts/test_demo.py`: 4 passed. The gap guard rejects a deliberately
  bridged synthetic path with `CGM gap was bridged`. Counts, reproducibility, missing
  window and non-separable co-occurrence were checked.
- Public `/api/health`: `{"status":"ok","service":"cukier-w-biegu","phase":"phase-1-synthetic-demo"}`.
- Public sample CSV downloaded through HTTP: 16 EGV readings, including a real gap
  in timestamps; no interpolated missing rows.
- Brave on production: selected gap, steady segment and two-signal moment. Gap gives
  no glucose value; co-occurrence shows both signals and non-separability wording.
- Added synthetic observation through dialog; it appeared in the run and brief.
  Matching missing-observation text was removed. Empty submit was disabled.
- Navigation to `/runs`, `/sources`, `/brief` visibly verified; no console errors/warnings
  reported by browser log inspection during that check.
- Final mobile production check at 390 x 844: no horizontal overflow; all three charts
  use compact `0 0 400 130` viewBoxes. Axes, missing interval and moments visually reviewed.
  Temporary viewport overrides reset after testing.

## Print verification boundary

Brief content and observations were verified in the browser. Clicking the local print
button invokes `window.print()`; browser automation timed out at the native print flow.
Native preview/page count and the saved PDF were **not** independently verified.
A4 print CSS hides navigation and controls. Include print/save-PDF in Greg's review.
Long observations may result in additional pages; content is not truncated.

## Evidence and deployment

Runtime screenshots (outside Git): `C:/_HackYeah2026/review/phase-1/`:
`desktop.jpg`, `brief.jpg`, `mobile-final.jpg`, `mobile-charts-final.jpg`.
These are actual browser captures, separate from the earlier ImageGen concepts.

Vercel blocked the second Git-associated deployment because the Git author is not
linked to the Hobby account. Final artifact deployment through the authenticated owner
succeeded without changing Git authorship or expanding permissions. See CLOUD.md.

UltraSoul was not changed. Approved engine imports remain unused by this UI runtime.
No database migration, health-data collection, Garmin auth, AI call or submission
was performed during this phase.
