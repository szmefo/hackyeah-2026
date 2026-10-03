# Phase 2 review — 2026-10-03

Public review: https://cukier-w-biegu.vercel.app

## Delivered

FIT + Dexcom Clarity CSV upload with timezone selection and separate processing consent.
Measured Python facts, gaps/nulls, contextual windows, shared charts, observations,
clinician brief and browser print flow. Optional Anthropic interpretation plus separate
AI quality review and code checks. No additional UltraSoul imports or patient persistence.

Demo pair: 94 minutes, 16.7 km, 73% numeric glucose coverage, minimum 65 mg/dL,
two point readings below 70. Completely synthetic FIT/CSV, generated during HackYeah.
Selected moment 80 min: numeric minimum 65 and accumulated minute-median ascent 40 m;
net height change is negative, so net height alone would miss the overlapping uphill.

## Executed checks

- Python: 87 tests passed, including parser/signal Background IP tests and new CSV,
  timestamp/DST, alignment, flags, missingness, terrain contrast and protected API cases.
- Node: 29 AI/transport tests passed: routing, destination-specific headers, consent
  boundary, JSON/fact/language guards, bounded correction, independent review and outages.
- Next typecheck + ESLint passed; local production build passed.
- Remote Vercel install/build passed, web and engine READY.
- Public Next-to-Python integration: 10 tests passed, using synthetic originals through
  the actual deployed proxy/engine. Correct results and safe actionable invalid uploads.
- Deployed AI endpoint: JSON null and mismatched provider consent return safe HTTP 400.
- Brave mobile at 390x844: measured story renders with no horizontal overflow; screenshot in C:/_HackYeah2026/review/phase-2/phone.jpg. Changing moment clears AI results and consent.
- Brave desktop: sample-pair button, consent, actual upload, measured story selection,
  dynamic Anthropic consent verified. Live model completion status recorded below.

## AI verification

Runtime /api/ai-status confirms configured=true, provider=Anthropic. The sensitive
credential remains on Vercel. Early synthetic drafts were rejected for unsupported
references and never shown as approved AI. One bounded correction and a shared
54-second deadline are implemented. Live model calls confirmed Anthropic authentication and structured output. A semantic endpoint/minimum contradiction was caught manually and given a regression guard; corrected synthetic interpretation completed on source 301c28b: it explicitly recognized the lower intermediate reading, compared pace/HR halves, considered terrain and sensor uncertainty, then passed separate review. Final display cleanup removes redundant internal separation flags; its regression test passed.

## Limits

This is a hackathon MVP, not clinical validation. AI review is a second quality check.
Language/reference checks are narrow, not a complete clinical or semantic validator.
One FIT/CSV pair, 2 MB per file; running activities and EGV CSV readings only.
Results/notes live in tab memory. Refresh/new tab restores the built-in synthetic example.
No database/auth, Garmin, period summaries, other diabetes profiles or final submission.
Printing has A4 CSS and opens the browser dialog; page count/native PDF was not verified.
Long notes/model results can require more than one page. Rate limits are per instance.

See phase-2-deployment.json for exact source and deployment artifact hashes.

Recorded at 2026-10-03T15:39:05.9263158+02:00. Human product review pending; final web runtime source 9344056.
