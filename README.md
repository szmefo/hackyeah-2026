# Cukier w biegu — HackYeah 2026

## Project name
Cukier w biegu · Glucose on the Run. Repository: `szmefo/hackyeah-2026`.

## Challenge
SPORT & HEALTHCARE. Revealed 2026-10-03 at 11:00 Europe/Warsaw, confirmed by Greg.
[Event and IP record](docs/HACKATHON.md).

## Problem
Running-watch and glucose data live separately. A difficult moment needs context,
visible missing measurements and useful questions for a clinician.

## Solution
Upload one running FIT and a Dexcom Clarity CSV, confirm the CSV timezone and processing
consent, then inspect their shared timeline and a printable clinician brief.
The Python engine computes all displayed measurements and selects contextual windows.
Missing data stay missing; co-occurrence does not establish causality.
No diagnosis, medication doses or food recommendations.

A supplied, wholly synthetic FIT/CSV pair exercises the same import pipeline.
The built-in synthetic story is always available, including when the engine is unavailable.
Optional Anthropic/OpenAI interpretation examines patterns and alternatives, then passes a separate
AI quality review and code checks. Failure keeps the measured facts and deterministic brief.
Provider availability and actual verification are in [PHASE_2_REVIEW.md](docs/PHASE_2_REVIEW.md).

## Architecture
Next.js 16 / React 19 / TypeScript / plain CSS and SVG; a separate Python FastAPI
processor. Next proxies uploads with a server secret and signs the resulting facts.
No patient database, authentication, localStorage, GPS retention or original-file storage.
Uploaded results, observations and AI responses live in React memory until reset/refresh.
[Architecture](docs/ARCHITECTURE.md) · [API contract](docs/PHASE_2_CONTRACT.md).

## Demo
**https://cukier-w-biegu.vercel.app**

1. Open **Źródła**, click **Wybierz przykładową parę**.
2. Confirm processing consent, click **Połącz pliki i zobacz bieg**.
3. Inspect the selected moment, compare glucose/pace/heart rate/terrain and switch to the gap.
4. Add an observation and open **Brief dla lekarza** → **Drukuj / zapisz PDF**.
5. If AI is configured, separately consent to the displayed provider processing and analyze the moment.
6. **Źródła → Usuń wgrane dane i wróć do demo** clears the uploaded result and notes.

Numbers in the supplied pair: 94 minutes, 16.7 km, 73% numeric glucose coverage,
minimum 65 mg/dL, two point readings below 70. These are synthetic, not patient measurements.
Import uses automatically detected/contextual moments; the original built-in story
has manually selected illustrative moments. See provenance on each dataset.

Refresh or direct opening a new tab restores the built-in example. Printing opens
the browser print flow; long notes/AI content can require more than one page.

## Running locally
Node **24.x**, npm, Python **3.12+**, Git and PowerShell **7**.
Private repository: cloning requires GitHub access.

```powershell
git clone https://github.com/szmefo/hackyeah-2026.git
cd hackyeah-2026
npm ci
python -m venv engine/.venv
engine/.venv/Scripts/python.exe -m pip install -r engine/requirements.txt
.\scripts\start_engine.ps1
```

The last command keeps the engine running on port 8000. It creates ignored
`.env.local` from the example if absent and generates a shared secret if empty.
In a **second terminal**, from the repository:

```powershell
npm run dev
```

Open **http://127.0.0.1:3000**. Start the engine before Next so Next loads the same secret.
The standalone built-in example can run with only `npm ci` and `npm run dev`.
For optional Claude AI, set `ANTHROPIC_API_KEY` in ignored `.env.local` and restart Next.
Default `ANTHROPIC_MODEL=claude-sonnet-4-6`. OpenAI remains optional via `OPENAI_API_KEY` / `OPENAI_MODEL`; no key is exposed to the browser.

Verification:
```powershell
npm run build
npm run check
Push-Location engine
.venv/Scripts/python.exe -m pytest tests -q
Pop-Location
node --experimental-strip-types --test scripts/test_ai.mjs scripts/test_transport.mjs
node --test scripts/test_routes.mjs
```

Route tests require the local engine and Next server. They use only synthetic data
and do not call the paid model. Use `npm start` after building for production-mode checks.
Regenerate demo with `python scripts/build_demo.py` and
`engine/.venv/Scripts/python.exe scripts/build_fit_demo.py`.

## Deployment
Vercel projects `cukier-w-biegu` and `cukier-w-biegu-engine`, scope `hack-yeah1`.
Web needs `ENGINE_URL`, `ENGINE_SHARED_SECRET`; engine needs the same secret.
Only web needs optional `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` (or OpenAI settings). No secrets in Git.
Manual authenticated artifact deployment; automatic GitHub deployment remains disabled.
[Cloud status](docs/CLOUD.md).

## Background IP
[BACKGROUND_IP.md](BACKGROUND_IP.md): six approved UltraSoul source/test imports with
source SHA, hashes, prior history and separate HTTP adaptation. Phase 2 invokes those
parsers and run signals; CSV/context/UI/AI/API are newly authored hackathon work.
No additional UltraSoul components imported and UltraSoul itself was not modified.

## AI & external resources
[AI_USAGE.md](AI_USAGE.md) · [THIRD_PARTY.md](THIRD_PARTY.md) ·
[AI interpretation and data disclosure](docs/AI_INTERPRETATION.md) ·
[DECISIONS.md](DECISIONS.md).
Import does not send data to an AI provider. Separate consent sends selected computed summaries
and nearby notes to the named provider. Both providers have retention policies; see the disclosure.

## Built during HackYeah
Reveal history is honest and not backdated. Import commits are `import(background-ip):`,
changes to imported code `adapt(background-ip):`, new work `feat:` / `test:` / `docs:`.

```sh
git log --reverse --oneline task-reveal-2026..HEAD
git diff --stat task-reveal-2026..HEAD
```

`pre-hackathon-starter-2026` records neutral preparation. Imports remain Background IP.
Phase 1 implemented Opowieść and synthetic review; phase 2 adds actual import, measured
contexts and optional model integration. No DB/auth, Garmin, period summaries, extra
diabetes profiles or final submission in this phase.

## Verification
[Phase 1](docs/PHASE_1_REVIEW.md) · [Phase 2](docs/PHASE_2_REVIEW.md).
[Submission folder](submission/README.md) remains a placeholder.
