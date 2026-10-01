# HackYeah 2026

## Project name

HackYeah 2026 — temporary name. Repository: `hackyeah-2026`.

Neutral development starter prepared **before** the challenge reveal. This is not
the competition solution. No UltraSoul source code was copied into this repository.

## Challenge

TBD — full challenge will be revealed on October 3, 2026.

SPORT & HEALTHCARE is a task of interest, not a confirmed product specification.

## Problem

TBD

## Solution

TBD

## Architecture

TBD — competition architecture depends on the full task.

Starter only: one Next.js application, React GUI and Route Handler API,
TypeScript, npm, plain CSS. See [starter architecture](docs/ARCHITECTURE.md).

## Demo

TBD — the local starter page is an environment check, not a competition demo.

## Running locally

Prerequisites: **Node.js 24.x**, npm and Git. No database, Docker or API key needed.

From a fresh clone (PowerShell, bash or another terminal):

```sh
git clone https://github.com/szmefo/hackyeah-2026.git
cd hackyeah-2026
npm ci
npm run dev
```

Open **http://127.0.0.1:3000** and click **Sprawdź API**.
Expected result: **API działa. Odpowiedź serwera: ok.**

The repository is initially private; cloning requires your GitHub account's access.
For the already-created local checkout, just run `npm ci` and `npm run dev` there.

`.env.example` documents the empty initial configuration. Copying it to
`.env.local` is optional; no variables are consumed by the starter.
Add server-side provider credentials only when an integration is selected.

Health endpoint:

```sh
curl http://127.0.0.1:3000/api/health
```

Expected JSON:

```json
{"status":"ok","service":"hackyeah-2026","phase":"pre-hackathon-starter"}
```

On Windows PowerShell 5, use `curl.exe` instead of its `curl` alias.
If port 3000 is occupied, use `npm run dev -- --port 3010` and adjust the URL.

Checks and production run (stop the dev server with Ctrl+C first):

```sh
npm run check
npm run build
npm start
```

`npm run build` generates Next.js types automatically. In a completely clean clone,
run `npm run build` before `npm run check` if `next-env.d.ts` does not exist yet.

## Deployment

When ready, import this GitHub repository into Vercel, select the Next.js preset,
leave the root directory as `.` and use Node.js 24.x. No environment variables
are initially required. No deployment has been created during preparation.

Alternatively, a host with Node.js can run `npm ci`, `npm run build`, then
`npm start -- --hostname 0.0.0.0 --port 3000`. Use deployment settings for secrets.
Do not use a static export when the solution needs server API routes.

## Background IP

See [BACKGROUND_IP.md](BACKGROUND_IP.md). The UltraSoul register is initially empty.
The pre-event starter is separately disclosed in that file and in Git history.

## AI & external resources

- [AI_USAGE.md](AI_USAGE.md)
- [THIRD_PARTY.md](THIRD_PARTY.md)

## Built during HackYeah

**Nothing yet.** Everything in the initial commit was prepared before the event.

At the actual task reveal, record the timestamp and official task/rules links in
[HACKATHON.md](docs/HACKATHON.md), then create an annotated `task-reveal-2026`
tag at the last pre-implementation commit. Record any intervening pre-event edits.
Do not backdate commits. Make regular, focused commits during implementation.

The initial `pre-hackathon-starter-2026` tag identifies the original starter.
After the reveal, compare it with the solution using:

```sh
git log --reverse --oneline task-reveal-2026..HEAD
git diff --stat task-reveal-2026..HEAD
git diff task-reveal-2026..HEAD
```

Imported Background IP and third-party additions inside that diff must still be
identified separately in their registers; a post-reveal commit alone does not
prove that every line was created during the event.

## Hackathon mode

Paste: **Full HackYeah task is below: [full task]**.

The working procedure is in [AGENTS.md](AGENTS.md) and [HACKATHON.md](docs/HACKATHON.md).
One strong problem → one clear insight → one convincing solution → one excellent demo.

## Submission

See [submission/README.md](submission/README.md). No final submission prepared yet.

## Verification

See [docs/VERIFICATION.md](docs/VERIFICATION.md) for the recorded clean-start checks.
