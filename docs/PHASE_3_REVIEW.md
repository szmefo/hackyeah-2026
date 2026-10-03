# Phase 3 review — local verification, 2026-10-03

Branch `overnight/phase-3` (local only), based on `origin/main` 3e62471. Owner decision
for tonight (option B): **local work only**. Nothing was deployed, pushed or merged,
and the production AI endpoint was not called. Deploy, production AI checks and the
merge to `main` wait for the owner's approval in the morning.

Development assistant: Claude Code (Anthropic), as integration lead over three parallel
workers (engine, UI, scenarios). All data used is synthetic.

## Commits (local, not pushed)

| Commit | Topic |
| --- | --- |
| 1275794 | fix(engine): distinct moments, honest separability and real run strengths |
| c579e8e | fix(engine): name run and CSV time ranges when they do not overlap |
| 33ad087 | fix(ui): readable chart axes and synthetic labelling |
| fcef999 | feat: one-click synthetic scenarios with byte-verified labels |
| 78f78f1 | fix: honest AI status, clear engine outage message and app icon |
| c8c7c44 | fix(demo): sensor-gap moment in the default fixture is not separable |

No Background IP file was edited (`run_signal_extractor.py`, `fit_parser.py`,
`fit_adapter.py` and their tests are unchanged). Nothing new was imported from UltraSoul.

## What changed

- **Engine story.** One moment per real story: half-run detector patterns no longer
  create a duplicate moment at an arbitrary midpoint, and overlapping windows with the
  same glucose/terrain story merge. `separable` is false for sensor gaps, partial CGM
  coverage and low/high readings on an uphill. Titles and narratives describe
  co-occurrence only. Strengths are plain sentences from the detector's strengths; the
  technical fallback sentence is gone, so an empty list hides the section.
- **Integration fixes made during this review.**
  - Fact references have labels for the new engine facts (`glucose.maximum`,
    `glucose.partial`, Low/High counts in the window, signal start/end). Yes/no
    flags show as "tak"/"nie" without a technical unit.
  - Watch-derived factors (for example "Zwolnienie tempa") use a clock icon instead
    of a glucose drop.
  - `/api/ai-status` returns `provider: null` when no key is configured. Before this,
    the unconfigured consent text named OpenAI as the destination.
  - An unreachable engine now returns a specific Polish 503 that points to the example
    run, instead of a generic import failure.
  - A CSV from another day fails with both local time ranges and the time zone, for
    example: "Odczyty CSV nie pokrywają się z biegiem. Bieg: 03.10.2026 08:30–10:04.
    Odczyty w CSV: 01.10.2026 08:30–01.10.2026 10:04 (Europe/Warsaw). Wyeksportuj CSV
    z dnia biegu albo sprawdź strefę czasową eksportu."
  - `src/app/icon.svg` stops the `/favicon.ico` 404 from showing as a console error.
  - The default landing fixture (`data/demo-run.json`) had its sensor-gap moment marked
    separable. That flag is now false, and `scripts/test_demo.py` guards it.
  - `.gitattributes` marks `*.fit` as binary, so the byte-matched scenario files can
    never be normalised by Git.

## Automated checks (final run at HEAD c8c7c44, 2026-10-03T22:25:41+02:00)

| Command | Result |
| --- | --- |
| `npm run check` (tsc + eslint `--max-warnings 0`) | pass |
| `npm run build` | pass (all routes, plus `/icon.svg`) |
| `node --experimental-strip-types --test scripts/test_ai.mjs scripts/test_transport.mjs` | 29 pass, 0 fail |
| `engine/.venv python -m pytest tests -q` (cwd `engine`) | 100 passed, 1 warning (existing Starlette/httpx deprecation) |
| `python -m unittest test_demo` (cwd `scripts`) | 5 tests OK |
| `QA_BASE_URL=http://127.0.0.1:3811 node --test scripts/test_routes.mjs` | 13 pass, 0 fail |

Local servers: the engine (uvicorn) ran on 127.0.0.1:8811 and `next start` on
127.0.0.1:3811, sharing a random local `ENGINE_SHARED_SECRET`. No AI key was set.
Both servers were stopped afterwards.

## Browser E2E (Playwright with system Chrome, `next start` production build)

Each run waited for networkidle plus 1500 ms before interacting. The flow was:
Źródła → scenario card (or "Wybierz przykładową parę") → focus moves to consent →
consent → import → run screen → each moment → "Dodaj obserwację" dialog → brief
link (client-side navigation, checked with a window marker that survives only
same-document navigation).

All 5 pairs passed at both 1440x900 and 390x844: 10 runs, 0 failed checks.

| Pair | Moments (label · minute · km) | Strengths shown |
| --- | --- | --- |
| Built-in | Luka w danych · 37,5 · 6,7 km; Dwa sygnały · 80 · 14,4 km | none |
| 1 Niski cukier na płaskim | Odczyt do omówienia · 50 · 9,0 km | even pacing sentence |
| 2 Podbieg, cukier w normie | Podbieg, glukoza w zakresie · 84 · 15,0 km | CGM full-coverage observation |
| 3 Podbieg i niski cukier naraz | Dwa sygnały · 85 · 15,1 km | none |
| 4 Luka w danych sensora | Luka w danych · 84 · 15,0 km | none |

Checked in every run:

- The scenario title is shown, with the DANE SYNTETYCZNE badge on the glucose chart.
- Moments are distinct by label, minute and title.
- Clicking a moment sets `aria-pressed` and updates the title. On the built-in pair
  (two moments), the window facts also change.
- The strengths section appears only for non-empty strengths.
- Chart text labels do not overlap: 0 overlapping bounding boxes in any SVG.
- `scrollWidth == clientWidth` on the run screen and the brief.
- The AI section shows "AI nie jest jeszcze podłączone…", with a disabled consent and
  button and no provider named.
- The observation appears in the brief, with the scenario title and badge.
- The console has no errors.

The default pages (`/`, `/brief`, `/sources`, `/runs`) without an import showed no
label overlaps, no horizontal scroll and no console errors at both widths.

Evidence (gitignored), under `.verification/`:

- `e2e/<pair>-<desktop|phone>-run.png` and `-brief.png`, plus `e2e/results.json`
- `pdf/`
- `errors/`

## PDF of the brief

The PDFs were made on `/brief` after importing scenario 03 and reaching the brief by
client-side navigation. Each used `page.emulateMedia({media: "print"})` and
`page.pdf({format: "A4", printBackground: true})`.

| File | Pages (regex count and pypdfium2) |
| --- | --- |
| `.verification/pdf/brief-s03.pdf` | 1 |
| `.verification/pdf/brief-s03-note400.pdf` (one 400-character observation) | 1 |

Page 1 was rendered by opening each PDF in Chrome's own PDF viewer and taking a
screenshot (`*-chrome-viewer.png`); a pypdfium2 render (`*-p1-pdfium.png`) is also
saved. In the viewer screenshot:

- navigation, toolbar and buttons are hidden (no `nav`, `.no-print` or `button` was
  visible under print media);
- nothing is cut off;
- the DANE SYNTETYCZNE badge, the low-readings table, the 400-character observation
  and the disclaimer "To nie jest porada medyczna…" are all present.

Honest limit: `page.pdf` uses Chrome's print pipeline, but the native print dialog
(`window.print()` → system dialog → Save as PDF/printer) was not clicked. Other
browsers and printer margins were not tested.

## Error states (through the real Źródła form)

| Case | Result |
| --- | --- |
| `.txt` in the FIT slot / CSV in both slots | 422 "Potrzebujemy pliku .fit i .csv." |
| CSV renamed to `.fit` | 422 "Nie można odczytać pojedynczego biegu z FIT. Wyeksportuj plik ponownie." |
| Non-Dexcom CSV | 422 "Brak kolumn Timestamp, Event Type i Glucose Value. Użyj eksportu Dexcom Clarity." |
| Missing consent | Submit button disabled |
| File > 2 MB | Client-side message "Każdy plik może mieć maksymalnie 2 MB…", no request sent; the server also enforces 413 (route test) |
| CSV from another day | 422 with both time ranges (message above) |
| CSV partly overlapping (shifted by 1 h, API check) | 200, honest coverage 27%, warning "Glukoza nie obejmuje całego biegu. Luki pozostały widoczne.", labelled uploaded, both moments `separable=false` |
| Engine stopped | 503 "Serwer analizy jest chwilowo niedostępny. Spróbuj ponownie za chwilę albo otwórz przykładowy bieg na stronie głównej." The home page then still renders the built-in synthetic run (badge present) |

## Not verified / pending owner approval

- **Production deploy** of this branch. Nothing was deployed tonight.
- **Production AI** (Anthropic) on the new moment semantics: interpretation and review
  were not run locally (no key) and the production endpoint was not called.
- `test_routes.mjs` against the deployed URL. This would confirm that the
  `public/scenarios` files are readable from the serverless import function. The
  local build trace `.next/server/app/api/import/route.js.nft.json` lists all 10 pair
  files (checked), but production was not checked.
- Merge to `main` and push: not done.
- Native print dialog, and browsers other than Chrome.
- The default landing run (`data/demo-run.json`, "Bieg nad Wisłą") is a phase 1 static
  fixture. It still shows three illustrative moments, unlike the engine's one story per
  run. Only its gap separability was corrected.
- The "Co poszło dobrze" heading also holds the neutral CGM-coverage observation in
  scenario 2; the owner may want to rename the heading.

Recorded at 2026-10-03T22:26:10+02:00 (Europe/Warsaw).
