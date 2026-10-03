# Architecture — phase 1

One Next.js app and four user-facing routes. Opowieść design is newly implemented in CSS/SVG; no UltraSoul UI, prompts or assets copied.

`scripts/build_demo.py` creates `data/demo-run.json` and `public/demo-glucose.csv` using a fixed seed. Distances, minima, counts and coverage are computed in Python. Moment positions are illustrative UI fixtures, not engine detections. CGM gaps remain separate paths.

`src/lib/demo.ts` loads the fixture. Components render facts/templates directly. React context keeps selection and temporary observations across client navigation. No localStorage, cookies, network persistence, LLM or patient database.

`/brief` shares selection/observations and renders an A4 print view with synthetic disclosure and basis. Browser print removes navigation/controls. Long added observations may extend the report to additional pages; nothing is silently truncated.

`engine/` contains six approved imports, with byte-exact import and separately registered adaptation. Tests use an isolated environment. Engine is not deployed/called in phase 1; `.vercelignore` excludes it from uploads.

After Greg's review: real FIT + Dexcom import, aligned timestamps and deterministic facts via a separate Python service. Choose consent-aware storage/auth/hosting then. Database preparation exists; phase 1 does not claim those integrations are complete.

Owner's latest AI direction: a model will analyze patterns and alternative explanations,
with a separate AI review and code-based evidence/safety checks. See
[AI_INTERPRETATION.md](AI_INTERPRETATION.md). This supersedes the brief's phrasing-only
model role; it is a future phase, not functionality claimed by this demo.
