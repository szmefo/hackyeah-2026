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

## Approved import at implementation start

Greg approved these six files in the final product plan and authorized phase 1.
Source revision is recorded rather than inventing a pre-event tag; UltraSoul remains untouched.

| Component / destination | Source revision | Existing before HackYeah | Added at | Notes / modifications |
| --- | --- | --- | --- | --- |
| `engine/app/services/run_signal_extractor.py` | `szmefo/UltraSoulAI:backend/app/services/run_signal_extractor.py` at `3c3f49d184d1fabd4997daabd88248b4f08382e4` | Yes; last source change `b36bba6e 2026-07-04T19:37:07Z` | 2026-10-03T13:02:36+02:00 | Byte-exact import; SHA-256 `1d2755c437851c80697a184afc2fab044901c43504418a7b78f7f270ba072078`; no modifications. Parser/signals/tests groundwork for later real import, not called by phase-1 UI. |
| `engine/app/services/fit_parser.py` | `szmefo/UltraSoulAI:backend/app/services/fit_parser.py` at `3c3f49d184d1fabd4997daabd88248b4f08382e4` | Yes; last source change `a274f8f0 2026-09-13T09:26:48+02:00` | 2026-10-03T13:02:36+02:00 | Byte-exact import; SHA-256 `b6be18517f3623d3ddd393c4881063a5be3c1acc1c5d0795243a7ee1729b76a9`; no modifications. Parser/signals/tests groundwork for later real import, not called by phase-1 UI. |
| `engine/app/services/fit_adapter.py` | `szmefo/UltraSoulAI:backend/app/services/fit_adapter.py` at `3c3f49d184d1fabd4997daabd88248b4f08382e4` | Yes; last source change `a4318276 2026-09-12T05:23:11Z` | 2026-10-03T13:02:36+02:00 | Byte-exact import; SHA-256 `1f15f6377fa6e0185f869113e6844761671c5f69c85465dce0bf14d35e0fb35a`; no modifications. Parser/signals/tests groundwork for later real import, not called by phase-1 UI. |
| `engine/tests/test_run_signal_extractor.py` | `szmefo/UltraSoulAI:backend/tests/test_run_signal_extractor.py` at `3c3f49d184d1fabd4997daabd88248b4f08382e4` | Yes; last source change `10c5d221 2026-07-03T07:14:19+02:00` | 2026-10-03T13:02:36+02:00 | Byte-exact import; SHA-256 `f76871b9cbc4629b889af4e61a756b969a4453465aa9ec505202d46893d73ae1`; no modifications. Parser/signals/tests groundwork for later real import, not called by phase-1 UI. |
| `engine/tests/test_fit_parser_alignment.py` | `szmefo/UltraSoulAI:backend/tests/test_fit_parser_alignment.py` at `3c3f49d184d1fabd4997daabd88248b4f08382e4` | Yes; last source change `a4318276 2026-09-12T05:23:11Z` | 2026-10-03T13:02:36+02:00 | Byte-exact import; SHA-256 `a9b212b1434ff3755e3e2ffad0d40b7c3241454cd0a07b86220ce47cd2bd8703`; no modifications. Parser/signals/tests groundwork for later real import, not called by phase-1 UI. |
| `engine/tests/fit_fixtures.py` | `szmefo/UltraSoulAI:backend/tests/fit_fixtures.py` at `3c3f49d184d1fabd4997daabd88248b4f08382e4` | Yes; last source change `081f95b8 2026-09-13T06:52:08+02:00` | 2026-10-03T13:02:36+02:00 | Byte-exact import; SHA-256 `6204a0d00b160f77a1e61d02941920253b83bb8ecda2377f368dbef23b561937`; no modifications. Parser/signals/tests groundwork for later real import, not called by phase-1 UI. |

Import commit: `import(background-ip): preserve approved UltraSoul parsers and signal extractor`.
SHA-256 hashes refer to bytes from the committed source revision and byte-identical imported files.
Any later adaptation must have its own commit and modification record.
