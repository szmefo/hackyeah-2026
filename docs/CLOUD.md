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
