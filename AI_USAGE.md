# AI usage

Record development assistants (Codex, ChatGPT, Claude, Cursor or others) separately
from models used by the running application. Do not assume the 2026 Open Task
permits a particular use of AI; verify and record its actual rules after reveal.

## Development assistance

| Timestamp / phase | Tool | Model if known | Purpose | Output / paths | Human direction / review |
| --- | --- | --- | --- | --- | --- |
| 2026-10-01, Europe/Warsaw — before event | Codex | GPT-6-based agent; exact model identifier unavailable | Stack selection, newly written neutral skeleton, documentation, dependency installation and local verification | Entire initial repository except downloaded third-party packages | Greg requested this preparation; no permission to import UltraSoul; Greg reviews delivered starter |
| 2026-10-02, Europe/Warsaw — before event | Codex | Exact model identifier unavailable | Brave account verification and neutral cloud preparation | docs/CLOUD.md and resource / decision registers | Greg completed account sign-in; database password entry and final project creation handed to Greg; no UltraSoul import or application integration |
| 2026-10-02, Europe/Warsaw — before event | Codex | Exact model identifier unavailable | Verify owner-created database and finish the owner-selected GitHub association | Supabase dashboard settings; docs/CLOUD.md, THIRD_PARTY.md, DECISIONS.md | Greg selected / authorized szmefo/hackyeah-2026 and requested completion; automatic DB deployment disabled; verified empty public schema |
| 2026-10-03, after owner-confirmed 11:00 reveal, Europe/Warsaw; precise session times not retained | Claude (owner-supplied brief), Codex and built-in ImageGen | Claude version described by owner as Fable 5; image model identifier unavailable | Product brief review and three visual concepts with corrections, before implementation baseline | PRODUCT_BRIEF.md supplied by owner; concept PNGs and prompt logs in C:/_HackYeah2026/mockups/2026-10-03, outside application repo | Greg approved final brief and chose concept 02 Opowieść. Images were visually reviewed, not runtime screenshots |
| 2026-10-03, Europe/Warsaw — current implementation session, after reveal | Codex | GPT-6-based agent; exact model identifier unavailable | Git provenance, approved byte-exact imports, phase-1 synthetic UI and print view, local/browser checks and deployment | engine/; scripts/; data/; src/; documentation; focused commits recorded in Git | Greg explicitly authorized phase 1 and a working site for review. Verification results will be recorded in docs/VERIFICATION.md; human product review pending |

No task-specific prompts or algorithms were authored before reveal. No UltraSoul
source code or data was read or imported to construct the starter. Public Next.js
and HackYeah references were consulted; npm packages came from the public registry.

For each session during the event, record tool/model, timestamp with timezone,
what AI contributed, relevant paths/commits, human decisions and validation.
If the rules require prompt transcripts, retain a sanitized export and link it
here. Never include credentials or personal health data in that export.

## Application AI

| Added at | Provider / model version | Purpose / endpoint | Data sent | Cost / limits | Relevant rules / notes |
| --- | --- | --- | --- | --- | --- |

Phase 1 record: no model SDK, API key or live model call in either the starter or phase-1 demo.
Owner's revised target role is documented in [docs/AI_INTERPRETATION.md](docs/AI_INTERPRETATION.md):
AI analysis of patterns/alternatives, synthesis, separate AI review and deterministic checks.
Provider/version and data payload were not selected in phase 1.

## Phase 2 development session

| Timestamp with timezone | Tool / model | Contribution | Paths / commits | Human decision and verification |
| --- | --- | --- | --- | --- |
| 2026-10-03T14:42:33+02:00 | Codex orchestrator plus engine, web and QA subagents; exact model deployment identifier unavailable | FIT/CSV alignment, measured facts, upload UI, AI interpretation/review prompts and guards, integration/deployment | engine/app/services/analysis.py and glucose.py, engine/main.py, src/, scripts/test_ai.mjs, scripts/test_routes.mjs, new engine tests; commits recorded in Git | Greg approved phase 2 and subagents, selected OpenAI; root inspected changes, independent QA exercised contrast scenarios and negative inputs; verification report records actual results |

Application integration: OpenAI Responses, model default `gpt-4.1-2025-04-14`
(override `OPENAI_MODEL` recorded with each displayed result). Two distinct model calls:
pattern interpretation and adversarial quality review. No medical verification claimed.
First live check uses only synthetic cases; health data requires separate UI consent.
No SDK dependency: server uses fetch. No keys, original uploads or raw GPS in Git.

## Phase 1 verification closure

2026-10-03T13:42:19+02:00: current Codex session produced the Opowieść implementation,
synthetic Python facts, provenance records, tests and manual Vercel artifact deployment.
Checks and limits: [docs/PHASE_1_REVIEW.md](docs/PHASE_1_REVIEW.md).
Source UI release: `9523dd9`; artifact deployment retains honest Git authorship.
Greg reviews the live direction before real-data/model integration.

## Anthropic integration session

| Timestamp with timezone | Tool / model | Contribution | Paths | Human direction and verification |
| --- | --- | --- | --- | --- |
| 2026-10-03T14:59:05+02:00 | Codex, model not exposed in this session; root plus engine/web/QA subagents | Anthropic transport, provider routing, consent UI and mocked tests | src/lib/server/provider-config.ts; llm-transport.ts; api/interpret; api/ai-status; ai-analysis.tsx; scripts/test_transport.mjs | Greg selected Anthropic; root integrates; independent QA, type/build checks and synthetic live verification recorded in docs/PHASE_2_REVIEW.md |

Application AI provider update: owner selected Anthropic, default `claude-sonnet-4-6`.
Two separate requests interpret and review. Only explicit consent sends selected
computed facts and nearby notes. Actual live verification is in docs/PHASE_2_REVIEW.md.

Live synthetic verification completed: Anthropic claude-sonnet-4-6 interpreted the
imported run and a separate call approved the corrected explanation. It described
the lower intermediate reading despite higher endpoints, pace/HR changes, competing
terrain context and unresolved causality. Final presentation strips redundant internal
separation-flag annotations; 29 Node tests cover transport/guards/presentation.
No personal health records were used for provider verification.

Final public synthetic application-model check: 2026-10-03T15:43:09.4279041+02:00; source 9344056; Anthropic claude-sonnet-4-6; selected facts and no runner notes; UI and brief reviewed manually.
## Cream and lavender UI — 2026-10-03T15:30:58+02:00

Greg selected v3 concept 04 and requested implementation isolated from concurrent agents. Codex implemented a new presentation stylesheet and small run-summary/timeline markup changes on codex/cream-lavender-ui, based on c40ebe9, in a separate managed worktree. No backend/model logic or shared checkout files changed. Built-in ImageGen had generated the reference in the earlier design session (model identifier unavailable). Build, typecheck/lint, 10 integration tests and desktop/mobile browser checks passed. See docs/CREAM_LAVENDER_UI.md for scope, evidence and integration boundaries.

| 2026-10-03T15:55:34+02:00 | Codex | GPT-6 | Integrated cream/lavender commit eb510e2 as a86ea60 preserving newer application changes; resolved append-only documentation conflicts; tested and published existing Vercel site. | docs/CREAM_LAVENDER_UI.md; a86ea60 | User requested integration/publication; build, check, 29 AI tests, 10 production route tests and Brave GUI verified. |

2026-10-03T18:54:39+02:00 — Codex (GPT-6): diagnosed mismatched FIT/CSV dates in local synthetic scenarios, regenerated all four pairs, verified each with analyze_upload and scenario 03 through production import (HTTP 200). Added the existing synthetic generator and corrected pairs under demos/synthetic-scenarios with portable repository paths at Greg's request to commit/push. No model API used.

2026-10-03T18:55:38+02:00 — Codex (GPT-6): updated README to match deployed cream/lavender UI, Anthropic provider, versioned synthetic scenarios, local commands and actual verification scope. Checked documentation against repository files and recorded release evidence; Greg requested README update.

2026-10-03T18:58:57+02:00 — Codex (GPT-6): documented public app URL, local tmp/synthetic-scenarios path versus versioned demos copy, and short jury demo steps in README, submission/README and scenario README. Requested by Greg; checked file paths against repository.

2026-10-03T19:12:39+02:00 — Codex (GPT-6): screened 35 reachable commits with Gitleaks and sensitive-path checks; completed user-requested public visibility via Brave after owner reauthentication; confirmed anonymous API/README access and updated visibility documentation. See docs/PUBLIC_REPO_REVIEW.md.

2026-10-03T22:28:16+02:00 — Claude Code (Anthropic), integration lead over three parallel workers (engine, UI, scenarios) on local branch overnight/phase-3: distinct engine moments and honest separability, readable chart axes and synthetic labelling, one-click synthetic scenarios with byte-verified labels, plus integration fixes (AI status without provider when unconfigured, engine outage message, CSV date-range error, app icon, default fixture gap separability). Owner chose option B: local only, no deploy/push/merge, no production AI call. Verified locally; evidence in docs/PHASE_3_REVIEW.md.

2026-10-04T02:45:18+02:00 — Claude Code (Anthropic), overnight orchestrated session (2026-10-03T21:35+02:00 to now) on local branch overnight/phase-3, delegating to subagents with scoped file ownership: engine (distinct moments, separability, strengths, CSV range errors), UI (chart axes, synthetic labelling, terrain fill, one-page brief), scenarios (one-click cards with byte-verified synthetic labels), integration, an independent review whose eight findings were reproduced and fixed, a 10-slide deck with screenshots, and English HackTribe texts, demo script and morning checklist. Subagent output was reviewed by the orchestrator; Greg reviews everything before deploy, merge or submission. Verified locally with npm run check/build, engine pytest, AI/transport tests, route tests against local engine+next, Playwright with system Chrome (desktop and 390 px) and A4 PDF page counts; evidence in docs/PHASE_3_REVIEW.md. No deploy, push, merge or production AI call (owner option B). All data synthetic.
