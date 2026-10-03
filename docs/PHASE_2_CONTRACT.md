# Phase 2 contract — upload to one run story

Owner approved implementation on 2026-10-03. This phase uses transient processing:
no patient database, auth, GPS storage, original-file retention or Garmin login.

## Routes

Browser `POST /api/import`: multipart `fit` (one FIT), `glucose` (Dexcom CSV),
`timezone` (IANA, default Europe/Warsaw), `consent` (literal `true`),
`synthetic` (literal true only when using our explicitly provided synthetic pair).
Both files combined max 4 MB (each max 2 MB); no content/file names in logs.
Next proxy forwards to private Python `POST /analyze` with same fields and
`X-Engine-Secret` from env. Engine requires shared secret in production.
Success `{run: RunStory}`; failure `{error: string, code: string}` with appropriate 4xx/5xx.
Do not cache responses. No files persist; browser run lives in React memory.

Browser `POST /api/interpret`: JSON `{run, momentId, observations, consent:true}`.
Separate explicit AI consent. Server sends only computed facts and selected-moment
summaries plus consented observations to the configured provider, never original files/GPS/name.
Success `{status:'ai', claims:[{text,factIds}], alternatives:[{text,factIds}],
unknowns:string[], questions:string[], review:'passed', provider:'OpenAI'|'Anthropic', model:string}`.
Unavailable/rejected response `{status:'fallback', reason:string}`; UI keeps facts/template.
AI output is not independently medically verified. Model config stays server-only.

## RunStory

Compatible with `data/demo-run.json`, but all missing measurements are `null`.
`schemaVersion:1, synthetic:boolean, seed?:number, title:string, date:YYYY-MM-DD,
start:ISO timestamp with offset, timezone:string, durationMinutes:number,
distanceKm:number|null, samples:[{minute,pace:number|null,hr:number|null,
altitude:number|null,distanceKm:number|null}], glucose:[{minute,value:number}],
glucoseFlags?:[{minute,flag:'below_range'|'above_range'}],
glucoseSegments:[[{minute,value}]], gaps:[{start,end}], moments:[Moment], facts:Facts,
provenance:{kind:'synthetic'|'uploaded',engineUsed:boolean,clinicalValidation:false},
factRegistry?:{[stableId]:{value:number|string|null,unit:string,description:string}},
strengths?:string[], warnings?:string[]`.

`Moment`: id, minute, label, title, distanceKm nullable, windowStart/windowEnd,
minGlucose nullable, readingCount, pace nullable, hr nullable, altitudeChange nullable,
factors:[{id,label,evidence,factId}], narrative, unknowns:string[], question,
separable:boolean. At least one meaningful moment even if no detected slowdown.
Labels/narrative honest deterministic fallback, not invented causality.

`Facts`: coveragePct, coveredMinutes, minGlucose nullable, below70Count,
below54Count, readingCount, averagePace nullable, basis:string.
Count only numeric point readings; flags get separate counts if needed, never invented values.
Coverage is observed intervals no longer than 10 min, clipped to run, no imputed threshold duration.
Render glucose line only between numeric readings at most 15 min apart; do not cross Low/High flags.
Leading/trailing missing coverage included in gaps. CGM moment windows ±10 min.
CSV timestamps local unless explicit offset. Ambiguous DST timestamps reject with actionable error.
FIT needs running sport, real UTC start, timestamp-based samples. Reject ordinal-only timing
for glucose alignment rather than fabricating matching. Missing HR/altitude stays unknown.

## Ownership

- Engine worker: new `engine/app/services/glucose.py`, `analysis.py` only; do not edit Background IP.
- Web worker: `src/lib/demo.ts`, new story types, `src/components/`, `/sources` and `/runs`, CSS.
- QA: new tests under `engine/tests/`, fixture generator and public synthetic FIT only.
- Root: API routes, `engine/main.py`, requirements/config, AI service/tests, docs/Git/deployment.

Root commits explicit scoped files. Workers do not commit, stage, deploy, read secrets or edit
other owners' files; report cross-cutting needs. Import adaptation stays separate from new modules.

Provider update: Anthropic is the owner's current selection. `/api/ai-status` returns
only configured/provider; `/api/interpret` requires provider-matching separate consent.
Model transport/payload/retention: AI_INTERPRETATION.md. UI numbers remain Python facts.

