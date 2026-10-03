# Architecture — phase 2

One Next.js web app (React/TypeScript, CSS/SVG) and one small Python FastAPI processor.

1. Browser selects a running FIT and Dexcom CSV, timezone and processing consent.
2. Next bounds each file at 2 MB and proxies generic filenames to the authenticated engine.
3. Python parses real timestamps, aligns point glucose readings and running signals,
   preserves gaps, calculates measurements and selects contextual moments.
4. Next HMAC-signs the returned story. Browser displays facts, observations and a brief.
5. Separate provider-specific consent enables server-only AI interpretation and a second
   quality review. JSON/reference/language checks reject unsafe or unsupported output;
   deterministic facts/templates remain available on failure.

## Boundaries

Original files and parsed results are processed in memory, not a patient database.
Browser state is React memory; refresh/reset clears uploaded results, notes and AI.
No localStorage, GPS retention, raw-file storage, authentication or Garmin connection.
Supabase is prepared but remains unconnected. No new UltraSoul imports in phase 2.

All displayed measurements come from Python facts. CGM is considered in an approximate
window, not an exact blood measurement at the running second. Co-occurrence is not
causality. Missing measurements are null/gaps, not interpolated clinical conclusions.

Claude default: claude-sonnet-4-6; optional OpenAI transport remains supported.
Only selected computed summaries and nearby consented notes reach the named provider.
No FIT/CSV binaries, raw trajectories, GPS, absolute dates, file/device identity or secrets.
Provider retention and payload are detailed in AI_INTERPRETATION.md.

## Practical limits

Upload: 2 MB per file. One activity at a time; only running FIT and EGV CSV readings.
CSV ambiguous/nonexistent local DST times require corrected input, not silent guesses.
Two bounded model calls may take tens of seconds. Review is a quality check, not medical
validation. Rate limits are in-memory per server instance, not a distributed spend cap.
Printing uses the browser dialog; long notes/AI content can exceed one A4 page.

Contract: PHASE_2_CONTRACT.md. Verification: PHASE_2_REVIEW.md.
