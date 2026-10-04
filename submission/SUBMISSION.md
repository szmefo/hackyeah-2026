# HackTribe submission fields — Glucose on the Run

Prepared 2026-10-04T02:17+02:00 (Europe/Warsaw) by Claude Code (Anthropic) for Greg's
review. Each section below the line is meant to be pasted into the matching
HackTribe field. The sections follow the existing draft
(`C:\_HackYeah2026\review\hacktribe-draft.txt`) and keep its voice. The difference is
that they now describe what is built, not the plan.

**Before pasting (not part of the fields):**

- The text assumes that the morning deploy of `overnight/phase-3` is live: scenario
  cards on **Źródła**, the scenario 2 name "Podbieg, glukoza w zakresie", and the
  one-page brief. If the deploy does not happen, change INSTRUCTIONS step 2 to:
  "click **Wybierz przykładową parę**", and drop the sentence about four scenario
  cards. Those cards are not on the current public site; on 2026-10-04 at 02:15,
  `/scenarios/...` returned 404.
- TEAM NAME is not decided anywhere in the repository. Confirm it (see `CHECKLIST.md`).
- Field length limits on HackTribe are unknown. If a field is too long, shorten
  PROGRESS first and leave the disclosure section intact.

---

## PROJECT TITLE

Glucose on the Run (Cukier w biegu)

## TEAM NAME

<!-- TO CONFIRM: the team name as registered on HackTribe. Suggested: Cukier w biegu -->
Cukier w biegu

## TEAM MEMBERS

Grzegorz Walencik (solo)

## NAME

Glucose on the Run

--------------------

## PROBLEM

At kilometre 14, your pace falls apart. Was it the hill, the way you started, or your glucose? A pace chart alone cannot answer that.

For an adult runner with type 1 diabetes, the watch records pace, heart rate and terrain, while the glucose sensor records another part of the same run. Even when glucose is visible on the wrist, reviewing what happened afterwards means jumping between separate apps and trying to line up the timelines by hand.

The same gap follows the runner into the doctor's office. 'How is exercise going?' gets an answer like 'It depends', instead of a clear account of when a difficult moment happened, what the glucose readings showed and what information is missing.

Glucose on the Run turns those separate records into something the runner can understand and take to a diabetologist. The target group is deliberately narrow: adult runners with type 1 diabetes who use a continuous glucose monitor (CGM).

--------------------

## SOLUTION

Glucose on the Run puts one run and its glucose readings on one timeline, then turns them into a one-page brief for a conversation with a diabetologist.

The working path: upload one FIT file from a running watch and one Dexcom Clarity CSV, choose the time zone of the CSV export, confirm consent and open the run. Glucose, pace with the terrain profile, and heart rate are drawn as three charts on one shared time axis. The app picks out the difficult moments, for example a pace drop, and shows each one with the facts measured in a window of ±10 minutes around it. CGM readings are never treated as a second-by-second match. When the watch data show it, the app also names what went well, such as even pacing.

The useful part is the context, including its limits. A slowdown may coincide with a low glucose reading, an uphill section, or both. When both happen in the same window, the app says plainly that the data cannot separate their effects. Missing readings stay visible as gaps and are never filled in. Each moment has three short parts: what we see, what we do not know, and one question for the doctor. The runner can add an observation (how they felt, a stop, a meal, route conditions) at a given minute. The observation goes into the brief, and the app suggests noting context on the next run, because the watch and the sensor cannot record it.

The brief is a printable A4 page. It holds the run summary, glucose coverage, the lowest reading, a table of point readings below 70 mg/dL, the facts for the selected moment, the unknowns, the questions and the runner's latest observations.

Python code computes the facts and every displayed number. Optional AI analysis (Anthropic Claude) is a separate step with its own consent. It compares the co-occurring signals, considers alternative explanations and suggests questions. Every AI statement must cite the IDs of computed facts. Code checks then reject model-written numbers, unsupported references, causal certainty, diagnoses and medication or food instructions, and a second Claude call reviews the answer. If anything fails, the app keeps the deterministic facts and brief. The app does not diagnose, recommend insulin doses or prescribe food.

The app is designed for a phone browser, with plain Polish and one main thought per screen. Files are processed in memory and nothing is written to a database. The result does not include GPS coordinates or the original files, and refreshing the page deletes the result and the notes. All demo data are synthetic and labelled "Dane syntetyczne" on screen and in the brief.

--------------------

## PROGRESS

Before the event (disclosed, not hackathon work)

- A neutral Next.js starter, tooling and empty cloud accounts (Vercel, GitHub, and a Supabase project that the app does not use). Git tag `pre-hackathon-starter-2026`, 2026-10-01.
- Background IP from my earlier UltraSoul project: three Python modules and their tests (the FIT parser, the FIT adapter and the run-signal extractor). They were imported byte-for-byte from UltraSoulAI commit 3c3f49d184d1fabd4997daabd88248b4f08382e4. They detect pace drops, a slower second half, heart-rate/pace decoupling, cadence changes and run strengths. The only change made at the event (the parser and one of its tests) removes an HTTP framework dependency. Source paths, revisions, SHA-256 hashes and import times are in BACKGROUND_IP.md.

Built at HackYeah (after tag `task-reveal-2026`, task revealed 2026-10-03 11:00 Europe/Warsaw)

- Dexcom Clarity CSV parsing with time zones and DST, FIT/CSV time alignment, coverage and gap computation, and a window of ±10 minutes around each moment.
- The context layer: moment selection, terrain (accumulated ascent), low and in-range glucose, separability, co-occurrence-only wording, unknowns and questions for the doctor.
- A FastAPI processing service and a Next.js upload proxy with a shared secret and HMAC-signed results.
- The user interface ("cream and lavender" design): run summary, three aligned charts, moments, observations, and a one-page printable clinician brief.
- Optional Claude analysis with fact citations, code guards, a separate AI review call, one bounded correction, a 54-second budget, rate limiting and a deterministic fallback.
- Four synthetic FIT/CSV scenarios plus a built-in pair, each loaded with one click. A run is labelled synthetic only when both files are byte-identical to a known pair.
- Tests: 103 Python tests (including the imported Background IP tests), 29 AI/transport tests, 13 end-to-end API tests and 5 demo-fixture tests. Browser checks at desktop and 390 px phone width.

Deployed at https://cukier-w-biegu.vercel.app (web) with a separate Python service on Vercel. A full Claude analysis and its review completed on the public site on synthetic data. The four demo cases from the plan are all there: low glucose on flat terrain, a hill with glucose in range, a hill and low glucose at the same time, and a gap in glucose data. These are demo scenarios, not clinical validation.

Not built, on purpose: the multi-run view, type 2 diabetes and prediabetes profiles, manual glucometer entries and Garmin Connect sync. File upload is the core path.

--------------------

## SKILLS

Solo project. The team is complete; I am not recruiting additional members.

--------------------

## REPOSITORY

https://github.com/szmefo/hackyeah-2026

Live demo: https://cukier-w-biegu.vercel.app/

To see exactly what was built at the event: `git log --reverse --oneline task-reveal-2026..HEAD`. Commits of imported pre-existing code start with `import(background-ip):` and the single change to it starts with `adapt(background-ip):`.

--------------------

## INSTRUCTIONS

No account is needed. Everything works on a phone or laptop browser.

1. Open https://cukier-w-biegu.vercel.app/ and go to **Źródła**.
2. Under **Scenariusze demo**, click **Wczytaj scenariusz** on any of the four cards. For the clearest comparison, start with scenario 2 and then open scenario 3.
3. Tick the processing consent and click **Połącz pliki i zobacz bieg**.
4. On the run screen, check the selected moment, the three charts and the cards **Co widać / Czego nie wiemy / O co spytać lekarza**.
5. Click **Dodaj obserwację**, add a note, then open **Brief dla lekarza** and use **Drukuj / zapisz PDF**.
6. Optional: in **Spójrzmy na ten moment razem**, tick the separate Anthropic consent and click **Przeanalizuj ten moment z AI**. The limit is about 2 analyses per minute and 8 per hour from one network. If it is reached, or the model fails, the facts and the brief still work.

The four scenarios:

- **1 Niski cukier na płaskim**: a slowdown on flat ground at the same time as a reading below 70 mg/dL.
- **2 Podbieg, glukoza w zakresie**: a slowdown on a hill (about 41 m of climb), with every reading at 70–180 mg/dL, so the hill is the only factor flagged in that window.
- **3 Podbieg i niski cukier naraz**: the same kind of hill, with a 62 mg/dL reading in the same window. The app says that the data cannot separate their effects.
- **4 Luka w danych sensora**: the sensor stops in the second half of the run, so the hill has no glucose readings and the gap stays visible.

The same files are in the repository under `demos/synthetic-scenarios`, and each card has **Pobierz FIT / Pobierz CSV** links. Use time zone Europe/Warsaw. Any other file is labelled as uploaded data, not synthetic. Refreshing the page clears the result and the notes.

To run locally: see the README (Node 24, Python 3.12+, `npm ci`, the engine started with `scripts/start_engine.ps1`, then `npm run dev`).

--------------------

## AI & EXTERNAL RESOURCES

AI inside the app

- Anthropic Claude through the Messages API (server-side `fetch`, no SDK), used only for the optional analysis after separate consent. One call interprets the moment and a second call reviews it. The model version is set on the server; the default is listed in README.md and docs/AI_INTERPRETATION.md. The model receives only computed facts for the selected moment, run-level coverage and nearby observations the runner entered. It never receives the FIT or CSV files, raw streams, GPS, absolute timestamps or file names. Anthropic's standard API retention (up to 30 days, with exceptions) is disclosed in the consent text.
- The code also supports OpenAI's Responses API as an alternative provider. It is not configured on the public site.
- AI review is a quality check, not clinical verification.

AI used in development

- Codex (OpenAI): the main coding agent at the event, also used for pre-event starter preparation. It built the engine, UI, AI integration, tests and deployment under my direction and review.
- Claude Code (Anthropic): overnight integration, review fixes, verification and these submission texts.
- Claude (claude.ai): review of the product brief.
- Codex built-in image generation: three UI concept images, used only as visual references.
- Session details, paths and human decisions are in AI_USAGE.md.

Libraries and services

- Web: Next.js 16, React 19, TypeScript, ESLint.
- Engine: Python 3.12, FastAPI, Uvicorn, pydantic, python-multipart, tzdata, and Garmin's official FIT SDK (garmin-fit-sdk) for decoding.
- Tests: pytest and httpx. Playwright with Chrome for local browser checks only.
- Hosting: Vercel (web and engine) and GitHub.
- Supabase was prepared before the event but is not connected.
- Versions and licences are in THIRD_PARTY.md.

Data

- All demo runs and glucose readings are synthetic. They were generated during the event by scripts in the repository (`scripts/build_fit_demo.py`, `demos/synthetic-scenarios/generate.py`). No patient or personal health data was used. The CSV follows the Dexcom Clarity export format; no Dexcom data or API is used.

Pre-existing work

- The Background IP is three UltraSoul modules and their three test files at commit 3c3f49d184d1fabd4997daabd88248b4f08382e4, imported 2026-10-03 13:02 (Europe/Warsaw) with one documented adaptation.
- The neutral starter was built on 2026-10-01.
- Everything else was built after the task reveal. See BACKGROUND_IP.md.
