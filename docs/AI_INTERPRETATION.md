# Updated AI role — owner steering during phase 1

Greg supplied this update on 2026-10-03 while the phase-1 site was being verified.
It revises the final brief's restriction that the model only phrases existing conclusions.

## Target behavior adopted after phase 1

- Python computes aligned summaries, facts with stable identifiers, window measurements,
  sensor gaps and observation metadata. UI numbers remain directly sourced from facts.
- A model analyzes relationships across run/glucose summaries, considers alternative
  co-occurring factors, identifies missing context, and synthesizes an explanation,
  a summary and questions for the clinician. Its contribution is interpretation and
  synthesis, not merely rewriting a predetermined conclusion.
- Each claim references supporting fact IDs. A separate AI review checks contradictions,
  unsupported claims and alternatives. That review is a quality check, not independent
  clinical verification or proof of causality.
- Code checks the schema, references, number substitution, required uncertainty and
  safety constraints. Valid fact IDs alone do not prove that a claim follows from them;
  evaluation must also test the supporting relationship against known scenarios.
- Keep deterministic fact/template fallback when model calls fail or output is rejected.
  No medication/food directions, diagnosis or causal attribution from co-occurrence.

## Before connecting a provider

Choose provider/version and the minimum fact/summary payload. Document whether any
runner notes or health data are transmitted, destination, consent, retention and deletion
behavior. Initially validate on explicitly synthetic cases. Never send GPS, credentials
or FIT binaries to the model.

Phase 1 had **no application model selected, SDK, key or model call**. The
owner-supplied screenshot/text describes a future plan recorded in submission fields;
this implementation session has not edited or submitted those fields.

## Phase 2 implementation — 2026-10-03T14:42:33+02:00

Provider chosen by Greg: OpenAI. Next server-only Responses requests use configurable
`OPENAI_MODEL`, default `gpt-4.1-2025-04-14`, `store:false`, strict JSON schema,
bounded output and timeouts. No model SDK. Key belongs only in Next server settings.
The first call interprets measured patterns and competing explanations; a separate
call reviews factual support, alternatives and safety. Rejected/failed output is
never presented as AI analysis; the deterministic run story and brief remain usable.

Exact payload: chosen moment's computed facts (CGM minimum/count/endpoint change,
pace and HR window-half means, preceding pace baseline, detector metrics, net height
and minute-median accumulated ascent, missingness), global coverage/low-reading count,
window unknowns and nearby consented observations. No original binary/CSV, raw streams,
run title, absolute timestamps, GPS, device identity, filename or credentials.
Notes are untrusted JSON data, not instructions. No direct quotes are generated.

The import proxy signs the run using HMAC. AI accepts an authentic computed run or
the exact built-in synthetic fixture. Guards reject unknown/unrelated fact IDs,
obvious unsupported missing-data claims, model-authored numbers, diagnostic statements,
medication/food directives and causal certainty. A narrow language guard is not a
complete semantic or clinical validator; independent contrast tests and review remain
necessary. Model output is quality-reviewed, never claimed medically verified.

Separate UI consent names OpenAI and possible health data. Results and notes are held
only in tab memory; reset/refresh clears them. Import consent is separate and does
not trigger AI. OpenAI can retain abuse-monitoring logs by default up to 30 days;
`store:false` is not a claim of zero retention or guaranteed deletion of provider logs.
Source: https://developers.openai.com/api/docs/guides/your-data

Rate limiting is bounded in-memory per server instance (two requests/minute,
eight/hour per hashed network bucket, three concurrent calls), not a global distributed
quota. Configure provider spend limits before exposing an unrestricted public workload.
Verification status, including any unavailable live key, is in PHASE_2_REVIEW.md.
