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
| GitHub | Repository hosting | https://github.com/szmefo/hackyeah-2026 | 2026-10-01, Europe/Warsaw | Source history | GitHub service terms | Private at initialization |

No application APIs, LLMs, external datasets or external visual assets are connected.
`data/example.json` is newly written synthetic preparation data. Fonts are the
platform's system fonts. Vercel is a documented deployment option, not a deployed service.

When adding a resource, record exact version/model identifier or dataset revision,
origin, license/terms link, attribution obligations and relevant restrictions.
For external APIs, record whether any user data is sent and the demo dependency.
Record AI-assisted development in `AI_USAGE.md` as well.
