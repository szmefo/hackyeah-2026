# Background IP

- UltraSoul existed before HackYeah 2026.
- No UltraSoul proprietary source code was initially copied into this repository.
- Any pre-existing components introduced during the hackathon must be documented here.
- New work developed after the HackYeah task reveal should be clearly distinguishable from pre-existing work.

## UltraSoul components introduced into this repository

No entries at initialization. Importing anything requires Greg's explicit decision
after reviewing the full task. This includes code, components, prompts, algorithms,
datasets, assets and documentation copied from UltraSoul.

| Component | Source | Existing before HackYeah | Added at | Notes |
| --- | --- | --- | --- | --- |

For each later entry, identify the exact source repository, path and commit/tag;
record the original creation/pre-event evidence, actual import timestamp with
timezone, destination paths, import commit and any modifications. Explain its
role in the demo. Keep the source attribution when adapting a component.

## Separately disclosed pre-event preparation

This repository's **entire initial commit** was created on 2026-10-01 before the
task reveal. It contains a newly written, neutral Next.js starter (page, health
endpoint, synthetic fixture, tooling and documentation). It is not UltraSoul IP
and must not be represented as a solution built during HackYeah.

Third-party frameworks/tooling are registered in `THIRD_PARTY.md`; preparation
assisted by AI is registered in `AI_USAGE.md`. Git tag `pre-hackathon-starter-2026`
identifies this preparation. Further pre-reveal edits also belong to preparation.

At the actual reveal, record the time in `docs/HACKATHON.md` and tag the current
pre-implementation state as `task-reveal-2026`. Separate new implementation,
Background IP imports and third-party additions when explaining the Git diff.

## UltraSoul snapshot reminder

Before the event, Greg should mark the intended UltraSoul Background IP state as
`pre-hackyeah-2026` in its own repository. No UltraSoul tag was created by this task.
First commit the intended source changes; a Git tag does not capture uncommitted files.

```sh
git -C C:/_UltraSoulAI status --short
git -C C:/_UltraSoulAI tag -a pre-hackyeah-2026 -m "UltraSoul Background IP before HackYeah 2026"
git -C C:/_UltraSoulAI push origin pre-hackyeah-2026
```

Check that the tag does not already exist before creating it; do not replace an
existing snapshot. Record its SHA here if a component is later imported.

These records document provenance. They do not establish eligibility, an IP
exemption or organizer acceptance; check the actual task rules after reveal.
