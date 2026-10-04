# Decisions

Use actual ISO 8601 timestamps with timezone. One short entry per meaningful decision.

| Timestamp | Decision | Reason |
| --- | --- | --- |
| 2026-10-03T14:42:33+02:00 | Orchestrator plus three independent workers, scoped file ownership, root-controlled review/commits/deployment | Owner requests parallel speed with verified quality |
| 2026-10-03T14:42:33+02:00 | Phase 2: single FIT + Dexcom CSV, transient processing, no DB/auth/Garmin | Complete one golden path without storage/integration overhead |
| 2026-10-03T14:42:33+02:00 | Separate FastAPI project on existing Vercel account, shared server secret | Official Python support allows upload MVP without another hosting account; Garmin MFA still needs a future long-lived service |
| 2026-10-03T14:42:33+02:00 | OpenAI interpretation of window patterns plus separate AI review, signed facts and conservative guards | Owner requires intelligent interpretation; review alone cannot establish correctness |
| 2026-10-03T14:42:33+02:00 | Accumulate positive changes between minute-median heights, keep net height change separately | A hill returning to its starting height must not disappear from the context |
| 2026-10-03T14:42:33+02:00 | Synthetic checkbox accepted only for the exact supplied demo pair | Prevent ordinary uploads from being misrepresented as demo data |
| 2026-10-03T13:33:16+02:00 | Phase 1: selected Opowieść design, one wholly synthetic run, three clickable moments and a printable clinician brief | Greg requests a live site for visual/journey review before the next phase |
| 2026-10-03T13:33:16+02:00 | Byte-exact approved UltraSoul import, then HTTP adaptation in a separate commit | Preserve ownership and provenance; no UltraSoul repository changes |
| 2026-10-03T13:33:16+02:00 | Generate demo facts in Python, render directly; no application AI or patient persistence in this phase | Review the UI without provider dependencies; synthetic claims remain reproducible and explicit |
| 2026-10-03T13:33:16+02:00 | Future model analyzes patterns/alternatives and synthesizes evidence-linked conclusions, with a separate AI review and code checks | Owner update revises phrasing-only role; target documented in docs/AI_INTERPRETATION.md, not yet implemented |
| 2026-10-03T13:33:16+02:00 | Manual Vercel CLI deployment in hack-yeah1; defer automatic GitHub linking | Existing account lacks GitHub Login Connection; working public review site requires no new grant or paid plan |
| 2026-10-03T13:33:16+02:00 | Mobile SVG uses a compact viewBox rather than scaling desktop labels down | Phone check found unreadable small axis text |
| 2026-10-01T21:44:58+02:00 | New standalone `hackyeah-2026` repository outside UltraSoul; initially private | Clear Git/IP separation; no publishing decision needed before task reveal |
| 2026-10-01T21:44:58+02:00 | Single Next.js app, TypeScript, npm and plain CSS; GUI + Route Handler API | Solo 24h work benefits from one install, one server and one deployment |
| 2026-10-01T21:44:58+02:00 | Pin direct packages and commit npm lockfile; use Node 24.x | Repeatable setup without version drift during the event |
| 2026-10-01T21:44:58+02:00 | Implement only a neutral page and health endpoint; no domain, LLM, database or integrations | Full challenge and task rules are not known |
| 2026-10-01T21:44:58+02:00 | Disclose initial starter as pre-event preparation and tag it | Jury can distinguish preparation, imports and work after reveal |
| 2026-10-01T21:44:58+02:00 | No UltraSoul imports without Greg's explicit post-reveal decision and provenance entry | Existing UltraSoul remains separately identified Background IP |
| 2026-10-01T21:44:58+02:00 | One complete end-to-end use case takes priority over feature count | A convincing demo is the delivery target |
| 2026-10-01T21:56:25+02:00 | Keep ESLint 9.39.5 for this starter | ESLint 10.11.0 failed at runtime in Next.js's React lint plugin; version 9 passes. npm flags version 9 as unsupported; revisit compatibility if this starter becomes a longer-lived product |
| 2026-10-01T21:56:25+02:00 | Disable automatic framework edits to AGENTS.md | Starting dev should not modify the IP/scope instructions or dirty Git history |
| 2026-10-02T21:45:59+02:00 | Prepare a separate Vercel Hobby workspace and a Supabase Free project form; defer schema and application integration | Greg requested cloud readiness before the event; the full brief remains unknown. Database password and creation are an owner handoff; readiness is tracked in docs/CLOUD.md |
| 2026-10-02T21:52:35+02:00 | Save owner-selected Supabase GitHub association with root directory `.` and Deploy to production off | Keep requested repository association without running migrations or adding a speculative schema; database public schema verified empty; no paid branching |

| 2026-10-03T14:59:05+02:00 | Select Anthropic after owner confirmation; route sk-ant credentials by prefix even under legacy env name | Sensitive Vercel values cannot be pulled; avoid exposing or sending a credential to the wrong provider |
| 2026-10-03T14:59:05+02:00 | Bind separate AI consent to the actual configured provider | Changing providers must not reuse consent naming a different destination |

## Review handoff — phase 2

Core import, consent, measured contexts, Anthropic interpretation/review and printable
brief implemented. No additional Background IP imports/adaptations in this phase.
Public synthetic verification and release hashes: docs/PHASE_2_REVIEW.md.

Recorded review handoff at 2026-10-03T15:39:05.9263158+02:00 (Europe/Warsaw); Greg reviews before further product scope.
| 2026-10-03T15:30:58+02:00 | Implement approved v3 concept 04 in an isolated worktree, with a separate cream-lavender.css presentation layer | Greg requested the summary-first cream/lavender layout and protection from concurrent edits; retain current phase-2 import/AI behavior and existing print styles |

| 2026-10-03T15:55:34+02:00 | Cherry-pick cream/lavender UI onto b0e45ec; preserve both documentation histories and publish a86ea60 to existing Vercel project. | Application files merged cleanly; newer Anthropic, validation and import code unchanged; production checks passed. |

| 2026-10-03T18:54:39+02:00 | Version four corrected synthetic scenario pairs and their generator in demos/synthetic-scenarios. | Local tmp assets were absent from Git; reproduce matching FIT/CSV dates and preserve demo inputs on GitHub. |

| 2026-10-03T22:28:16+02:00 | Phase 3 tonight is local only (option B): six topic commits on overnight/phase-3; deploy, production AI checks and merge to main wait for owner approval | Owner decision; local checks, Playwright E2E, PDF and error states recorded in docs/PHASE_3_REVIEW.md |
| 2026-10-03T22:28:16+02:00 | Label a run synthetic only on exact byte match with one of five known public pairs; one story per run; separable=false for gaps, partial CGM and low/high glucose on an uphill | Prevents mislabelled uploads and duplicate or overclaiming moments; co-occurrence never causation |
| 2026-10-04T02:45:18+02:00 | Strengths list only watch-derived sentences; glucose coverage stays a metric, not a success | Review found a CGM sentence framed glucose as a success and ignored high readings |
| 2026-10-04T02:45:18+02:00 | Clinician brief prints the 3 most recent observations, each clamped to 110 characters; the run screen keeps full text | Keeps the brief on one A4 page; an AI section may still push it to two pages (unmeasured locally) |
| 2026-10-04T02:45:18+02:00 | Deploy, production AI checks, push and fast-forward merge to main deferred to owner approval; exact steps in docs/PHASE_3_REVIEW.md "Morning handoff" | Owner option B; changes after the submission deadline do not count, so the morning steps go first |
