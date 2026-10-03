# Cukier w biegu — HackYeah 2026

## Project name
Cukier w biegu. Repository: `szmefo/hackyeah-2026`.

## Challenge
SPORT & HEALTHCARE. Reveal: 2026-10-03 at 11:00 Europe/Warsaw, confirmed by Greg. See [working record](docs/HACKATHON.md).

## Problem
A runner has activity data and glucose readings in separate places. Discussing a difficult moment with a clinician needs facts, context and explicit gaps.

## Solution
Phase 1: a responsive **synthetic single-run demo** in the selected Opowieść design. Open a run, select one of three moments, inspect co-occurring signals and unknowns, add a temporary observation, then open a printable clinician brief.

The run, CGM readings and selected moments are entirely synthetic, not patient data or clinically validated analysis. The imported signal engine is not called by this phase. No medication or nutrition recommendations.

## Architecture
Next.js 16, React 19, TypeScript, plain CSS and native SVG. Python generates a deterministic JSON fixture. The application renders its facts and templates without an LLM. Observations live only in React memory. [Architecture](docs/ARCHITECTURE.md).

## Demo
Production: **https://cukier-w-biegu.vercel.app**; deployment evidence/status in [CLOUD.md](docs/CLOUD.md).

- `/` — run story, synchronized charts, clickable moments, observations.
- `/runs` — one example run.
- `/sources` — synthetic source information and downloadable CSV.
- `/brief` — selected moment, facts, questions, observations and print styles.
- `/api/health` — health response.

Review: select **Luka w danych**, **Spokojny odcinek**, **Dwa sygnały**; add an observation; open **Brief dla lekarza**; click **Drukuj / zapisz PDF**. Observations stay in the current tab, are not sent to a server and disappear on refresh. Directly opening `/brief` starts with the default moment and no observations.

## Running locally
Node.js **24.x**, npm and Git. No database, API key or Python needed to run the checked-in web demo.

```sh
git clone https://github.com/szmefo/hackyeah-2026.git
cd hackyeah-2026
npm ci
npm run dev
```

Open **http://127.0.0.1:3000**. If occupied: `npm run dev -- --port 3010`. The repository is private and cloning requires access.

```sh
npm run build
npm run check
npm start
```

Build first in a clean checkout to generate Next.js types. No env variables required; `.env.example` lists unused future placeholders.

Health JSON: `{"status":"ok","service":"cukier-w-biegu","phase":"phase-1-synthetic-demo"}`.

### Optional Python checks and regeneration
```sh
python scripts/build_demo.py
python scripts/test_demo.py
```

Imported engine tests, PowerShell (Python 3.12+; verified locally with 3.14):

```powershell
python -m venv engine/.venv
engine/.venv/Scripts/python.exe -m pip install -r engine/requirements.txt
cd engine
.venv/Scripts/python.exe -m pytest tests -q
```

## Deployment
Vercel project `cukier-w-biegu`, scope `hack-yeah1`. No runtime secrets. `.vercelignore` excludes the engine and scratch artifacts from CLI uploads. Authorized CLI deployment; automatic GitHub deployment is not enabled. [Cloud status](docs/CLOUD.md).

## Background IP
[BACKGROUND_IP.md](BACKGROUND_IP.md) documents six approved UltraSoul source/test files with source SHA, SHA-256 hashes, pre-event history and adaptation. The pre-event starter is separately disclosed. Imported code is not used by the phase-1 runtime. UltraSoul itself was not changed.

## AI & external resources
- [AI_USAGE.md](AI_USAGE.md): concept/design and development assistance; no application AI calls.
- [THIRD_PARTY.md](THIRD_PARTY.md): frameworks, engine libraries, hosting.
- [DECISIONS.md](DECISIONS.md): decisions and reasons.

## Built during HackYeah
The reveal tag precedes implementation and was recorded at the actual current time, not backdated. `import(background-ip):` commits identify pre-existing files; `adapt(background-ip):` identifies modifications; `feat:`, `test:` and `docs:` identify new demo work. Earlier product planning/design is disclosed in the AI register.

```sh
git log --reverse --oneline task-reveal-2026..HEAD
git diff --stat task-reveal-2026..HEAD
```

`pre-hackathon-starter-2026` identifies neutral preparation. Post-tag imports remain Background IP.

## Phase 1 boundary
For Greg's UI/journey review. Real FIT/CGM import, automatic analysis, health-data storage, consent/auth, Supabase schema, Garmin, LLM narration and submission are later phases. The sources page says this explicitly.

Updated future AI role: [analysis, alternative explanations, synthesis and a separate AI review](docs/AI_INTERPRETATION.md), backed by deterministic facts and checks. No model is connected in this phase.

## Verification
[docs/VERIFICATION.md](docs/VERIFICATION.md). [Submission folder](submission/README.md) remains a placeholder.
