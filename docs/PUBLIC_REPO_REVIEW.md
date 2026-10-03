# Public repository review

Verified at 2026-10-03T19:12:39+02:00 (Europe/Warsaw).

At Greg's explicit request, repository visibility was changed through Brave/GitHub
from private to public after credential screening and owner GitHub Mobile approval.
Anonymous GitHub API reports public/private=false; raw main README returns HTTP 200.

Scope before publication: all 35 reachable commits after fetching both remote
branches and tags. Gitleaks 8.30.1, default rules, full-history scan with redacted
output: no leaks found (approximately 822 KB scanned). Additional historical
filename check found no tracked local env, credentials or private-key paths.
.env.example contains configuration placeholders. Local .env.local and .vercel
configuration are excluded from Git. GitHub Actions had no runs to expose.
Demo FIT/CSV data are generated synthetic fixtures. Six approved UltraSoul imports
remain publicly visible and explicitly attributed in BACKGROUND_IP.md.

This was credential screening, not a comprehensive application security audit or
a guarantee that every possible secret format can be detected. No credentials
were copied into the report; no history rewrite or license change was performed.
