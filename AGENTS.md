# HackYeah 2026 workspace instructions

This is a standalone repository. UltraSoul's code, design system, product scope,
configuration, secrets and repository workflows are not starter assets here.

## Before task reveal

Only neutral environment preparation is authorized. No SPORT & HEALTHCARE domain,
recommendation algorithm, task-specific prompts, competition solution or final
submission. Do not treat the teaser or UltraSoul's existing concept as the brief.
All current files are pre-event preparation, not work built during the hackathon.

## After task reveal

Follow `docs/HACKATHON.md` when Greg says "Full HackYeah task is below". Task first,
then regulations and evaluation criteria, then one small MVP, then implementation.
One strong problem → one clear insight → one convincing solution → one excellent demo.
Favor speed and readable code; avoid speculative features and infrastructure.

UltraSoul is Background IP. Import any element only after Greg explicitly chooses
it following reveal. Record exact source path/revision, destination, timestamps and
modifications in `BACKGROUND_IP.md`. Also distinguish this pre-event starter from
event implementation. Do not assume that documentation makes prior work eligible.

Keep `AI_USAGE.md`, `THIRD_PARTY.md` and `DECISIONS.md` current. Use real timestamps
with timezone, never backdate history or describe imported work as newly authored.
Unknown rules remain unknown until verified from current official sources.

## Local workflow

- Node 24.x, `npm ci`, `npm run dev`; default http://127.0.0.1:3000.
- For changes: `npm run check`, `npm run build`, then exercise the actual GUI/API
  end-to-end. In a clean checkout, build first to generate Next.js type files.
- Server credentials belong in `.env.local`/host settings, never in client code or Git.
- Before a commit, inspect `git status` and `git diff --cached --stat`; stage explicit
  files and keep commits focused. Never rewrite provenance history to look eligible.
- Update documentation when observed behavior, dependencies or scope change.
- Do not publish a deployment, alter UltraSoul or prepare final submission unless
  the current task authorizes it. This preparation does not authorize those actions.
