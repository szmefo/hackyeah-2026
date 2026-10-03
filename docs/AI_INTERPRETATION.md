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

## Provider update — 2026-10-03T14:59:05+02:00

Greg confirmed an Anthropic credential. Default Claude model: `claude-sonnet-4-6`.
Native server Messages API uses structured JSON, 1800 output tokens and a 22-second
limit per call. Anthropic has no `store:false` parameter. Two calls still perform
interpretation and separate quality review; numerical facts stay computed by Python.

`ANTHROPIC_API_KEY` takes precedence. The owner's existing sensitive credential may
remain under `OPENAI_API_KEY`: a `sk-ant-` prefix selects Anthropic at runtime and
is never forwarded to OpenAI. The secret is not read back, printed or copied to Git.
UI consent names the runtime provider and the server rejects mismatched consent.

Anthropic's standard API retention is up to 30 days, with contractual, policy and
legal exceptions; this is not a zero-retention claim. See
https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data
and structured output docs:
https://platform.claude.com/docs/en/build-with-claude/structured-outputs
Live result and verification are recorded in PHASE_2_REVIEW.md.

## Live validation adjustment

The first synthetic Claude drafts failed the evidence-reference guard and were not
shown as AI interpretation. One bounded correction of a rejected draft is now allowed,
then the same code checks and separate AI review are required. Repeated failure keeps
the deterministic fallback. Each call is limited to 16 seconds; at most three calls
fit within the 60-second route budget. Logs contain only finite rejection labels,
never model text, notes, measurements or secrets.


Final latency adjustment: each request has at most 22 seconds and receives only the
remaining time in a shared 54-second budget. At most one correction and one review.
This replaces the initial 16-second cap; timeouts have a safe distinct diagnostic code.

Synthetic live semantic regression: a draft passed AI review but incorrectly asserted
that readings stayed above the threshold from two higher endpoint values, ignoring
the lower measured minimum. Manual review caught this. A specific contradiction guard,
regression test and explicit minimum-versus-endpoints reviewer instruction were added.
This demonstrates why valid citations and a second model call are not clinical proof.

Language guard contrast: descriptive increased heart rate/reduced pace and steady pace
are allowed; imperative instructions and medication units remain rejected. Added a
regression test distinguishing Polish descriptive forms from direct commands.
