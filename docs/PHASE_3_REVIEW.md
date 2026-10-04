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
- ~~The "Co poszło dobrze" heading also holds the neutral CGM-coverage observation in
  scenario 2; the owner may want to rename the heading.~~ Resolved: the CGM sentence was
  removed from strengths (see "Review findings").

Recorded at 2026-10-03T22:26:10+02:00 (Europe/Warsaw).

## Review findings (2026-10-04)

Reviewers checked the branch at bcc2d2c. Each finding was reproduced before it was
fixed. All eight were real, and none was skipped. The fixes are local commits that
have not been pushed:

| Commit | Topic |
| --- | --- |
| d9d7d5b | fix(engine): keep glucose out of strengths and claims out of narratives |
| ddf6e52 | fix(demo): name scenario 2 "Podbieg, glukoza w zakresie" |
| 8cd72ef | fix(ui): keep a flat run flat in the pace chart terrain fill |
| 26f81d8 | fix(brief): keep the clinician brief on one A4 page with observations |

| Severity | Finding | Resolution |
| --- | --- | --- |
| major | The CGM sentence "Odczyty sensora objęły cały bieg i żaden z nich nie był niższy niż 70 mg/dL." appeared under "Co poszło dobrze". That framed glucose as a success. It also ignored high readings: a run at 265–286 mg/dL was still listed. | Removed. Strengths now hold only sentences derived from the watch, so the intro "Obliczone z pomiarów zegarka" is true for every item. Glucose coverage is still shown as "Pokrycie glukozy" in the brief metrics. Regression test: scenario 02 with every reading raised by 150 gives `strengths == []`. |
| major | The uphill, in-range narrative always said "W danych widać podbieg, nie spadek glukozy.", even when glucose fell from 178 to 72 mg/dL inside the window. | Sentence dropped. The narrative keeps only the computed fact that every reading fell within 70–180 mg/dL. Regression test uses the falling CSV from the review. |
| minor | Gender agreement: "wystąpił flaga Low/High z sensora". | `_occurred()` picks "wystąpiła" when the subject starts with "flaga". Covered by a regression test that uses the Low-flag CSV from the review. |
| minor | The uphill, in-range question mentioned "zwolnienie" even when no slowdown was detected. | Without a slowdown, the question now reads "Czy taki podbieg przy glukozie w zakresie warto omawiać w kontekście cukrzycy?". |
| minor | The name "Podbieg, cukier w normie" implied a clinical judgement. | Renamed to "Podbieg, glukoza w zakresie" in `src/lib/demo.ts`, `scripts/test_routes.mjs` and `submission/README.md`. Folder slugs are unchanged, because byte matching uses file paths. `demos/synthetic-scenarios/README.md` only mentions the slug. |
| major | The terrain fill auto-scaled to ±5 m. In scenario 1 ("na płaskim"), a 4 m wobble therefore drew as hills next to "Nie było tu podbiegu". | The terrain domain now spans at least 60 m. Measured at 390 px: the scenario 1 terrain edge varies by 7 of 150 SVG units, while the 44 m hill in scenario 2 still spans 78 units. Evidence: `.verification/review-fix/chart-s1-390.png`. |
| minor | Run screen: the "Obliczone z pomiarów zegarka" intro was wrong for the CGM sentence. | Resolved by the first fix. |
| minor | The "one-page" brief spilled onto a second A4 page after two or three observations. | The brief now prints the three most recent observations. Each is clamped to 110 characters with "…", followed by "Starsze obserwacje pominięte w wydruku: N." if any were left out. In print, the title fits on one line and observations use 9 px. The on-screen brief applies the same cap; the run screen keeps the full observations. |

Page counts measured with `page.pdf` (A4, print media) after client-side navigation,
using 500-character observations. All were **1 page**:

| Pair | 0 obs | 1 obs | 3 obs | 5 obs |
| --- | --- | --- | --- | --- |
| Built-in | 1 | 1 | 1 | 1 |
| Scenario 1 | 1 | 1 | 1 | 1 |
| Scenario 3 | 1 | 1 | 1 | 1 |

Scenarios 2 and 4 were measured at 0, 3 and 5 observations (an earlier 160-character
clamp, also 1 page). The built-in pair leaves the least room: about 22 px of the A4
content height with 5 observations. An "ai"-status AI section in the brief was not
measured, because there is no key locally. With that section, a long brief could still
run onto a second page.

Checks after the fixes, final run at HEAD 26f81d8:

| Command | Result |
| --- | --- |
| `npm run check` | pass |
| `npm run build` | pass |
| `node --experimental-strip-types --test scripts/test_ai.mjs scripts/test_transport.mjs` | 29 pass, 0 fail |
| `engine/.venv python -m pytest tests -q` (cwd `engine`) | 103 passed, 1 warning (the existing Starlette/httpx deprecation) |
| `python -m unittest test_demo` (cwd `scripts`) | 5 tests OK |
| `QA_BASE_URL=http://127.0.0.1:3811 node --test scripts/test_routes.mjs` | 13 pass, 0 fail |
| Playwright E2E, scenarios 1 and 2, at 1440x900 and 390x844 | 4 runs, 14/14 checks each |

Servers: the engine ran on 127.0.0.1:8811 and `next start` on 127.0.0.1:3811, sharing a
random local secret. No AI key was set. Nothing was deployed, pushed or merged, and
the production AI endpoint was not called. The browser evidence is in
`.verification/review-fix/` (gitignored).

Note: the table above under "Browser E2E" records the state before review. At that
point, scenario 2 was named "Podbieg, cukier w normie" and showed the CGM sentence as
a strength. Neither is true now.

Recorded at 2026-10-04T02:08:34+02:00 (Europe/Warsaw).

## Final local gate (HEAD 89f5715, 2026-10-04T02:50:11+02:00)

| Check | Result |
| --- | --- |
| `git status --short` | clean (only ignored files: `.env.local`, `.next/`, `.verification/`, caches) |
| `npm run check` | pass |
| `npm run build` | pass (all routes plus `/icon.svg`) |
| `engine/.venv python -m pytest tests -q` (cwd `engine`) | 103 passed, 1 warning (existing Starlette/httpx deprecation) |
| `node --experimental-strip-types --test scripts/test_ai.mjs scripts/test_transport.mjs` | 29 pass, 0 fail |
| `python -m unittest test_demo` (cwd `scripts`) | 5 tests OK |
| `QA_BASE_URL=http://127.0.0.1:3811 node --test scripts/test_routes.mjs` | 13 pass, 0 fail; `/api/ai-status` = `{"configured":false,"provider":null}` |
| Gitleaks 8.30.1 `git --log-opts=origin/main..HEAD --redact` and `dir submission` | 15 commits scanned, no leaks found |
| grep of `git diff origin/main...HEAD` for `sk-ant-`, `sk-…`, `BEGIN … PRIVATE KEY`, assigned `ENGINE_SHARED_SECRET`/`API_KEY` values, and the actual `.env.local` values | 0 matches |

Servers: engine (uvicorn) on 127.0.0.1:8811 and `next start` on 127.0.0.1:3811 with a
fresh random `ENGINE_SHARED_SECRET`, no AI key; both stopped after the run. Nothing was
deployed, pushed or merged; the production AI endpoint was not called.

## Morning handoff

Prepared at 2026-10-04T02:50:11+02:00. **None of these commands has been run.** Each step needs Greg's
approval. PowerShell on this computer. The detailed version with expected outputs,
the four-scenario browser table and the Claude checklist is `submission/CHECKLIST.md`.
Deploy uses the manual artifact flow from `docs/CLOUD.md` (`git archive` of committed
files plus the existing `.vercel` project link); environment variables are already set
in both Vercel projects, so do not change env.

### 1. Review and optional re-run of the gate (about 10 min)

```powershell
cd C:\hackyeah-2026-p3
git status --short
git log --oneline origin/main..overnight/phase-3
npm run check
node --experimental-strip-types --test scripts/test_ai.mjs scripts/test_transport.mjs   # 29 pass
cd engine; C:\hackyeah-2026\engine\.venv\Scripts\python.exe -m pytest tests -q; cd ..    # 103 passed
```

### 2. Deploy engine, then web (about 15 min)

```powershell
vercel whoami                                   # owner account of scope hack-yeah1
$repo = "C:\hackyeah-2026-p3"
$sha  = (git -C $repo rev-parse --short HEAD).Trim()

# 2a. engine -> project cukier-w-biegu-engine
$eng = "C:\_HackYeah2026\deploy\phase3-engine-$sha"
New-Item -ItemType Directory -Force $eng | Out-Null
git -C $repo archive -o "$eng.tar" HEAD engine/main.py engine/requirements.txt engine/vercel.json engine/.python-version engine/.vercelignore engine/app
tar -xf "$eng.tar" -C $eng --strip-components=1
Copy-Item -Recurse "C:\_HackYeah2026\deploy\phase2-engine\.vercel" "$eng\.vercel"
Get-Content "$eng\.vercel\project.json"         # "projectName":"cukier-w-biegu-engine"
Set-Location $eng; vercel deploy --prod --scope hack-yeah1
curl.exe -s https://cukier-w-biegu-engine.vercel.app/health

# 2b. web -> project cukier-w-biegu
$web = "C:\_HackYeah2026\deploy\phase3-web-$sha"
New-Item -ItemType Directory -Force $web | Out-Null
git -C $repo archive -o "$web.tar" HEAD src data public package.json package-lock.json next.config.ts tsconfig.json .gitignore .vercelignore
tar -xf "$web.tar" -C $web
Copy-Item -Recurse "C:\_HackYeah2026\deploy\cream-lavender-a86ea60\.vercel" "$web\.vercel"
Get-Content "$web\.vercel\project.json"         # "projectName":"cukier-w-biegu"
Set-Location $web; vercel deploy --prod --scope hack-yeah1
```

Note both deployment URLs and IDs. Rollback (both projects together, only if needed):
`vercel rollback https://cukier-w-biegu-ec4av15y9-hack-yeah1.vercel.app --scope hack-yeah1`
(web, from `$web`) and `vercel rollback dpl_5vHuojkv9sFRdUqGXX6Zx779jUTQ --scope hack-yeah1`
(engine, from `$eng`). After a rollback, `submission/SUBMISSION.md` needs its fallback wording.

### 3. Production checks (about 25 min)

```powershell
curl.exe -s https://cukier-w-biegu.vercel.app/api/ai-status            # {"configured":true,"provider":"Anthropic"}
curl.exe -s -o NUL -w "%{http_code}`n" https://cukier-w-biegu.vercel.app/scenarios/03-podbieg-i-niski-cukier/glukoza.csv   # 200
curl.exe -s -o NUL -w "%{http_code}`n" https://cukier-w-biegu.vercel.app/icon.svg                                         # 200
cd C:\hackyeah-2026-p3
$env:QA_BASE_URL = "https://cukier-w-biegu.vercel.app"
node --test scripts/test_routes.mjs                                     # 13 pass, 0 fail; no paid model call
Remove-Item Env:QA_BASE_URL
```

Then in Chrome: the four scenario cards on **Źródła** (expected moments in
`submission/CHECKLIST.md` 3b), one Claude analysis per scenario with at least 35 s
between calls (rate limit 2/min, 8/h), and the brief print preview with and without
an AI section (1 page expected without; with AI it may run to 2 pages).

### 4. Record the deployment (about 10 min)

Add `docs/phase-3-deployment.json` (source `$sha`, both deployment IDs/URLs, artifact
paths and SHA-256), append step 3 results here and in `docs/CLOUD.md`, update README
"Deployment" (currently `a86ea60`), and commit as `docs:` on `overnight/phase-3`.

### 5. Push and fast-forward `main` (about 5 min)

```powershell
cd C:\hackyeah-2026-p3
git status --short
git fetch origin
git merge-base --is-ancestor origin/main overnight/phase-3; $?        # True = fast-forward possible (origin/main was 3e62471)
git push -u origin overnight/phase-3
git push origin overnight/phase-3:main                               # fast-forward only; never --force
git ls-remote origin main                                            # equals git rev-parse HEAD
```

If `origin/main` moved (the check prints False or the push is rejected): `git fetch origin`,
`git merge origin/main` on `overnight/phase-3`, resolve conflicts, re-run the gate (step 1
plus `npm run build` and the route tests), then push both commands again. Update the
local `main` in `C:\hackyeah-2026` only when Codex is not working there:
`git -C C:\hackyeah-2026 merge --ff-only origin/main`.

### 6. Submission (about 20 min, before 10:30)

Paste the fields from `submission/SUBMISSION.md` into HackTribe, attach
`submission/Glucose-on-the-Run.pdf` (check it has at most 10 pages), set the team
name, and submit. Treat 11:00 as the hard deadline. No deploy or push after submission.
