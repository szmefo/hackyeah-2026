# Starter architecture

Competition architecture: **TBD after task reveal**.

This file describes only the pre-event environment. One application and one npm
package; no workspace manager or shared/domain packages.

```text
Browser
  -> src/app/page.tsx + src/components/health-check.tsx
  -> GET /api/health
  -> src/app/api/health/route.ts
```

- GUI: Next.js App Router, React, TypeScript and plain CSS.
- API: same-origin Route Handlers in `src/app/api/<name>/route.ts`.
- Neutral synthetic fixture: `data/example.json`, not wired to the application.
- No database, authentication, queues, infrastructure or provider SDKs.

## Adding capabilities after reveal

Add a page/component and only the API routes needed for the selected use case.
Use `src/lib/` for shared functions or provider adapters when such code exists;
there are deliberately no empty packages or fake integrations now.

For an LLM/API integration: select a provider based on the actual task, log it in
`THIRD_PARTY.md` and `AI_USAGE.md`, keep credentials in `.env.local`/host settings,
and call the provider from a server route. Use the provider's SDK or native `fetch`
depending on what is fastest to verify. Add error handling, a timeout and cost limits
at that point. No LLM provider, model or API contract has been chosen yet.

Keep mock fixtures explicitly labeled synthetic. Add persistence or a separate API
process only if the task requires it. Update this file to describe the actual solution.

## Deployment

Vercel with the Next.js preset is the initial deployment option. A Node.js host
running `npm run build` and `npm start` is an alternative. No deployment or external
account configuration has been performed. See the README for commands.

## Official technical references

- https://nextjs.org/docs/app/getting-started/installation
- https://nextjs.org/docs/app/api-reference/file-conventions/route
- https://nextjs.org/docs/app/getting-started/deploying
