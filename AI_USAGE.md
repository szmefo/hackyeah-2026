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

Empty: no model SDK, API key or live model call in either the starter or phase-1 demo.
Owner's revised target role is documented in [docs/AI_INTERPRETATION.md](docs/AI_INTERPRETATION.md):
AI analysis of patterns/alternatives, synthesis, separate AI review and deterministic checks.
Provider/version and data payload have not yet been selected.

## Phase 1 verification closure

2026-10-03T13:42:19+02:00: current Codex session produced the Opowieść implementation,
synthetic Python facts, provenance records, tests and manual Vercel artifact deployment.
Checks and limits: [docs/PHASE_1_REVIEW.md](docs/PHASE_1_REVIEW.md).
Source UI release: `9523dd9`; artifact deployment retains honest Git authorship.
Greg reviews the live direction before real-data/model integration.
