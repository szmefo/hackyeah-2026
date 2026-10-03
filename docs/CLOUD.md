# Cloud preparation — before HackYeah

Status verified in Brave on 2026-10-02 (Europe/Warsaw).
These are preparation resources, not functionality built during the event.

| Service | Resource | Verified status |
| --- | --- | --- |
| GitHub | https://github.com/szmefo/hackyeah-2026 | Separate private repository with the neutral starter |
| Vercel | https://vercel.com/hack-yeah1 | HackYeah workspace, Hobby plan; correct requested account signed in; no projects or deployments |
| Supabase | https://supabase.com/dashboard/project/omutcnsoxmjzagfbzkwa | `hackyeah-2026` created by owner in the Free organization; public schema has no tables or views; GitHub repository link saved |

## Supabase repository settings

The owner completed database password entry and project creation. The creation
form was prepared for Europe, Data API enabled, automatic exposure of new tables
disabled and automatic Row Level Security enabled. Never send passwords in chat
or commit them.

Saved GitHub integration settings, verified in the dashboard:

- Repository: `szmefo/hackyeah-2026`, selected and authorized by the owner.
- Working directory: `.` (root; any future `supabase/` folder goes here).
- Deploy to production: **off**. Git commits do not automatically migrate the DB.
- Automatic branching: **off / unavailable on Free**; no paid upgrade enabled.

This is a dashboard repository association. It does not connect the running
application to the database. No `supabase/` migration/configuration folder exists
yet. Define migrations only after selecting the actual challenge and schema.

## During the event

After the brief and rules are known, choose the minimal schema and access policies.
The starter does not yet use Supabase: there is no SDK, schema, application data,
credential configuration or database connection. Local start remains unchanged.

For deployment, connect only this repository to Vercel when needed. GitHub access
has not been granted to the new Vercel account. Add required credentials through
local environment files and deployment settings, never Git or client source.
Record new resources and any imported UltraSoul elements in their registers.

## Phase 1 deployment — 2026-10-03

Project: `cukier-w-biegu`, Vercel Hobby workspace `hack-yeah1`.
Public address: https://cukier-w-biegu.vercel.app
First production deployment: https://cukier-w-biegu-l5444hebk-hack-yeah1.vercel.app
Inspector: https://vercel.com/hack-yeah1/cukier-w-biegu/8jt5FzbNUk5G52wWh2WVr8NQk5dw

Vercel CLI authenticated to the owner-requested account. Deployment finished READY.
The project was linked through the CLI. Automatic GitHub linking failed because a
GitHub Login Connection is missing on the Vercel account; it is not required for
manual CLI deployment and was not added. No new GitHub grant or paid upgrade.

Runtime uses only synthetic fixture data. No environment secrets, patient database,
Garmin connection or application model. Python engine is excluded from deployment.
The previously prepared Supabase project is unchanged and remains unconnected.

Follow-up mobile chart polish is deployed to the same public alias; exact final
deployment and checks are recorded in VERIFICATION.md.

### Manual review package and deployment metadata

The first deployment succeeded, but Vercel blocked the later Git-associated
deployment `J1WrAi25Wm7TGY6TcHNhWiQRgKwx`: commit author `szmefo` is not linked to
the Vercel Hobby account. No project/security permission was weakened and no author
was impersonated or rewritten.

The updated web artifact was submitted through the authenticated owner's normal
non-Git CLI deployment flow. Package location:
`C:/_HackYeah2026/deploy/phase1-9523dd9`, copied from source revision `9523dd9`.
It contains only `src`, `data`, `public`, package manifest/lockfile, Next/TypeScript
configuration, ignores and the existing project link. No `.git`, Python engine,
credentials or UltraSoul source files. Future releases can use this explicit
artifact flow or, after the owner's account setup, ordinary Git deployment.

Updated deployment inspector:
https://vercel.com/hack-yeah1/cukier-w-biegu/9X2jZZ2EGwJLyXifnBxufts26VFH
This is artifact deployment, not automatic synchronization with GitHub.

### Phase 2 — transient import and model integration

Web alias: https://cukier-w-biegu.vercel.app
Engine alias: https://cukier-w-biegu-engine.vercel.app
Engine deployment: dpl_5vHuojkv9sFRdUqGXX6Zx779jUTQ, READY.

Web has ENGINE_URL and ENGINE_SHARED_SECRET; engine has the matching shared secret.
Owner provided a sensitive Anthropic credential under the legacy OPENAI_API_KEY name.
Runtime prefix recognition routes it only to Anthropic. Preferred future name is
ANTHROPIC_API_KEY. No secret value was recovered, printed or committed.

Next and Python process uploads transiently; Supabase remains empty/unconnected.
Model data are sent only after separate Anthropic consent. Only summaries and nearby
notes, never source files or GPS. Provider retention: AI_INTERPRETATION.md.

Final web revision, deployment and artifact hashes: phase-2-deployment.json.
Artifact exports exclude .git, env credentials and unrelated source; source hashes
allow matching the deployed artifact to Git without changing commit authorship.
