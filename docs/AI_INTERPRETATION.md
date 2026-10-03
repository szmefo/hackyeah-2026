# Updated AI role — owner steering during phase 1

Greg supplied this update on 2026-10-03 while the phase-1 site was being verified.
It revises the final brief's restriction that the model only phrases existing conclusions.

## Target behavior, not implemented in phase 1

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

Phase 1 currently has **no application model selected, SDK, key or model call**. The
owner-supplied screenshot/text describes a future plan recorded in submission fields;
this implementation session has not edited or submitted those fields.
