# Third-party resources

Keep libraries, APIs, model providers/models, datasets, open-source code and
external assets here. The lockfile is the exact dependency inventory, including
transitive packages; this table records direct dependencies and external services.
If the task requires a full license inventory, produce it from the final lockfile.

## Starter dependencies (introduced before the event, 2026-10-01)

| Resource | Version | Source | License / terms | Purpose |
| --- | --- | --- | --- | --- |
| Next.js | 16.3.8 | https://github.com/vercel/next.js | MIT | GUI and server routes |
| React / React DOM | 19.3.0 | https://github.com/facebook/react | MIT | UI runtime |
| TypeScript | 5.9.3 | https://github.com/microsoft/TypeScript | Apache-2.0 | Type checking |
| ESLint | 9.39.5 | https://github.com/eslint/eslint | MIT | Linting; pinned for Next.js plugin compatibility |
| eslint-config-next | 16.3.8 | https://github.com/vercel/next.js | MIT | Framework lint rules |
| @types/node | 24.19.0 | https://github.com/DefinitelyTyped/DefinitelyTyped | MIT | Node types |
| @types/react / @types/react-dom | 19.3.0 | https://github.com/DefinitelyTyped/DefinitelyTyped | MIT | React types |
| Node.js | 24.x (verified on 24.21.0) | https://nodejs.org | MIT plus bundled licenses | Local runtime |
| npm | Verified on 11.19.0 | https://github.com/npm/cli | Artistic-2.0 plus bundled licenses | Package installation |

## Other resources

| Resource | Type | Source / version | Added at (timezone) | Used in | License / terms / attribution | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Prettier | Formatting tool, ephemeral npm exec | 3.6.2; https://github.com/prettier/prettier | 2026-10-03, Europe/Warsaw | Format newly authored TSX/CSS for readable review | MIT | Not a runtime dependency; pinned invocation; no UltraSoul files formatted |
| Vercel deployment | Application hosting | cukier-w-biegu; CLI locally 53.4.0, remote build CLI 62.1.0 | 2026-10-03, Europe/Warsaw | Phase-1 synthetic public demo | Existing Vercel Hobby service terms | https://cukier-w-biegu.vercel.app; no app keys or patient data; manual CLI deployment, no automatic GitHub connection |
| pydantic | Python library | 2.12.5; https://github.com/pydantic/pydantic | 2026-10-03, Europe/Warsaw | Imported signal models, engine/requirements.txt | MIT | Existing local runtime verified; not a browser dependency |
| garmin-fit-sdk | Official Python FIT decoder | 21.214.0; https://github.com/garmin/fit-python-sdk | 2026-10-03, Europe/Warsaw | Imported FIT parser and fixtures | Garmin FIT SDK license in package / source repository; preserve applicable notices | Pin matches source environment with Encoder fixture support; global 21.195.0 lacks Encoder. No Garmin account integration; no real FIT uploaded in phase 1 |
| pytest | Python test runner | 9.0.2; https://github.com/pytest-dev/pytest | 2026-10-03, Europe/Warsaw | Imported engine tests | MIT | Verification tooling |
| GitHub | Repository hosting | https://github.com/szmefo/hackyeah-2026 | 2026-10-01, Europe/Warsaw | Source history | GitHub service terms | Private at initialization |
| Vercel | Hosting account / workspace | https://vercel.com/hack-yeah1 | 2026-10-02, Europe/Warsaw — before event | Prepared for later deployment | https://vercel.com/legal/terms | Hobby workspace verified; no deployment or GitHub connection |
| Supabase | PostgreSQL database / GitHub association | https://supabase.com/dashboard/project/omutcnsoxmjzagfbzkwa | 2026-10-02, Europe/Warsaw — before event | Empty database prepared for later use | https://supabase.com/terms | Free project created; public schema empty; hackyeah-2026 repository linked with automatic DB deployment off; no application integration; see docs/CLOUD.md |

At the end of phase 1, no application APIs, LLMs, external datasets or external visual assets were connected.
`data/example.json` is newly written synthetic preparation data. Fonts are the
platform's system fonts. Cloud account preparation is recorded in
[docs/CLOUD.md](docs/CLOUD.md). These sentences describe preparation; phase-1
application hosting on Vercel is disclosed separately above. Supabase is still not
connected to the application.

When adding a resource, record exact version/model identifier or dataset revision,
origin, license/terms link, attribution obligations and relevant restrictions.
For external APIs, record whether any user data is sent and the demo dependency.
Record AI-assisted development in `AI_USAGE.md` as well.

## Phase 2 resources — 2026-10-03T14:42:33+02:00

| Resource | Version / source | License / terms | Purpose and data |
| --- | --- | --- | --- |
| FastAPI | 0.142.2; https://github.com/fastapi/fastapi | MIT | Transient Python upload API; engine/requirements.txt |
| Uvicorn | 0.54.0; https://github.com/Kludex/uvicorn | BSD-3-Clause | Local ASGI server, access logging disabled |
| python-multipart | 0.0.32; https://github.com/Kludex/python-multipart | Apache-2.0 | Multipart parsing, accepted uploads kept below RAM spool threshold |
| httpx | 0.28.1; https://github.com/encode/httpx | BSD-3-Clause | API test client |
| tzdata | 2026.5; https://github.com/python/tzdata | Apache-2.0 package; IANA timezone data | ZoneInfo timezone conversion, including Windows |
| Vercel Python service | cukier-w-biegu-engine; Python 3.12 | https://vercel.com/legal/terms | Separate transient FIT/CGM processor; no patient DB or file retention |
| OpenAI Responses API | Configurable OPENAI_MODEL; default gpt-4.1-2025-04-14 | https://openai.com/policies/services-agreement/ | Interpretation and separate review; only selected computed facts, window summaries and consented nearby notes, never GPS or source files |
| Synthetic FIT demo | Newly authored scripts/build_fit_demo.py + public/demo-run.fit | Project-generated synthetic data; Garmin SDK encoder terms apply | Same-time pair with public/demo-glucose.csv; no patient/device/private data |
| Prettier | 3.9.1, ephemeral formatting invocation in phase 2 | MIT | Source formatting only, no runtime dependency |

OpenAI disclosure and exact payload: docs/AI_INTERPRETATION.md. Integration is implemented;
live provider verification depends on the owner's server key. `store:false` does not
eliminate default provider abuse-monitoring retention. Supabase remains unconnected.

## Owner-selected Anthropic provider

| Resource | Version / source | License / terms | Purpose and data |
| --- | --- | --- | --- |
| Anthropic Messages API | Default claude-sonnet-4-6; configurable ANTHROPIC_MODEL | https://www.anthropic.com/legal/commercial-terms | Native server fetch; selected computed facts and separately consented nearby notes. Interpretation + separate review; no source files, GPS or keys sent as prompt data. Standard retention and exceptions disclosed in docs/AI_INTERPRETATION.md. |
