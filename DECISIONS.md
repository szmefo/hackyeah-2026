# Decisions

Use actual ISO 8601 timestamps with timezone. One short entry per meaningful decision.

| Timestamp | Decision | Reason |
| --- | --- | --- |
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
