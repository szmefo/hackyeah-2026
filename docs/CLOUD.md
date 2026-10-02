# Cloud preparation — before HackYeah

Status verified in Brave on 2026-10-02 (Europe/Warsaw).
These are preparation resources, not functionality built during the event.

| Service | Resource | Verified status |
| --- | --- | --- |
| GitHub | https://github.com/szmefo/hackyeah-2026 | Separate private repository with the neutral starter |
| Vercel | https://vercel.com/hack-yeah1 | HackYeah workspace, Hobby plan; correct requested account signed in; no projects or deployments |
| Supabase | Organization `gwalencik`, Free plan | Signed in; new-project form prepared for `hackyeah-2026`, Europe; creation pending the owner's database password and final submission |

## Finish database creation

In the prepared Supabase form, the owner sets and saves the database password,
then clicks **Create new project**. Do not send the password in chat or commit it.
The form has Data API enabled, automatic exposure of new tables disabled and
automatic Row Level Security enabled. Project creation and readiness still need
verification; no database is claimed as created yet.

## During the event

After the brief and rules are known, choose the minimal schema and access policies.
The starter does not yet use Supabase: there is no SDK, schema, application data,
credential configuration or database connection. Local start remains unchanged.

For deployment, connect only this repository to Vercel when needed. GitHub access
has not been granted to the new Vercel account. Add required credentials through
local environment files and deployment settings, never Git or client source.
Record new resources and any imported UltraSoul elements in their registers.
