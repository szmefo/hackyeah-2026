# Hackathon working notes

## Event and sources

HackYeah 2026: October 3–4, TAURON Arena Kraków. Solo preparation.
Official homepage consulted on 2026-10-01: https://hackyeah.pl/
Task listing: https://hackyeah.pl/tasks-prizes

SPORT & HEALTHCARE is an interest, not a committed competition solution. Its teaser
was verified on the rendered official task listing on 2026-10-01: it describes
turning scattered sports, health and wellbeing data into useful decisions. The
listing currently shows **8,000 PLN**, rather than the earlier 5,000 PLN supplied
in the preparation brief. The full brief and specific rules must be checked at reveal.
No eligibility or AI/IP permission is inferred from the teaser or older editions.

Main regulations link discovered on the official site: https://hackyeah.pl/rules?lang=en
It opens a PDF; its clauses were not analyzed during this starter preparation.

## Planned times (Europe/Warsaw, UTC+02:00)

The rendered official agenda was checked on 2026-10-01. It lists the times below,
including a **final submission deadline at 11:00**, not 12:00, and describes the
20:00 checkpoint as submitting a first project draft. Greg supplied a main-rules
platform deadline of 12:00, which has not been independently reconciled here.
Plan to submit before 11:00 and recheck regulations/task rules at reveal; do not
rely on an additional hour. The internal readiness target should leave upload time.

| Date | Time | Milestone |
| --- | --- | --- |
| October 3 | 08:30 | Check-in |
| October 3 | 10:00 | Opening |
| October 3 | 10:30 | Team building |
| October 3 | 11:00 | Expected full task reveal and coding start |
| October 3 | 20:00 | Official checkpoint deadline: submit first draft; aim for working end-to-end version |
| October 4 | Before 11:00 | Internal target: ready with enough time to upload |
| October 4 | 11:00 | Final submission deadline shown by the official agenda |
| October 4 | 12:00 | Supplied platform limit — unverified; do not use as planning deadline |
| October 4 | 15:00 | Finalists |
| October 4 | 16:00 | Pitching |
| October 4 | 17:45 | Results |

## Actual reveal record

- Actual task reveal timestamp (with timezone): TBD
- Full task text / official URL and saved version: TBD
- Main regulations URL / version / relevant clauses: TBD
- Specific task regulations URL / version / relevant clauses: TBD
- Confirmed coding and submission windows: TBD
- Evaluation criteria and weights: TBD
- Existing code / starter eligibility: TBD
- AI assistance / application AI restrictions: TBD
- Third-party resources / datasets restrictions: TBD
- IP ownership / license / submission obligations: TBD
- Required files, repository visibility, demo and pitch format: TBD
- Submission platform and confirmed deadline: TBD

## When Greg pastes the full task

1. Read the complete task and current official regulations; save links/version and
   extract exact evaluation criteria, deadlines and submission requirements.
   Separate confirmed clauses from unknowns. Resolve any eligibility ambiguity
   affecting pre-event preparation, Background IP, AI or resources before using them.
2. Propose the smallest feasible MVP for the remaining time: one problem, one insight,
   one solution, one end-to-end demo. Spell out acceptance evidence and cuts.
3. Assess whether any UltraSoul element is useful. List exact candidates, source paths
   and revisions; do not import automatically. Wait for Greg's explicit import decision.
4. For approved imports, update `BACKGROUND_IP.md` at import time. Record external
   resources and AI use in their separate registers. Do not relabel imports as new work.
5. Record the actual reveal and create the baseline tag before implementation:

   ```sh
   git status --short
   git tag -a task-reveal-2026 -m "Actual task reveal; last pre-implementation state"
   git push origin task-reveal-2026
   ```

   Commit any pre-reveal preparation honestly before tagging; do not overwrite an
   existing tag. Timestamp and tag indicate provenance, not legal permission.
6. Choose and document architecture based on the task. Divide the **remaining** time
   into build, end-to-end checkpoint, polish, deployment, submission and pitch stages.
   Protect time before the confirmed deadline for submission problems.
7. Implement, run the full use case, inspect the rendered result and make focused
   commits. Start with a working vertical slice. Cut additions that threaten the demo.
8. Update README, registers, decision log and submission materials as they become
   real. Compare baseline and final commits for the jury; disclose preparation/imports.

No competition feature or final pitch is prepared before the full task is known.
