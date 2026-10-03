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

- Actual task reveal timestamp (with timezone): **2026-10-03T11:00:00+02:00**, confirmed by Greg in this chat on October 3. This record is committed at the actual current time; no backdating.
- Full task text / saved version: owner-supplied `C:/Users/szmef/Downloads/Details - SPORT & HEALTHCARE.pdf`; public viewer https://drive.google.com/file/d/1y62pvmn8k7O2wdknlWzSY7aTtDX6adn8/view. Product specification: owner-approved `PRODUCT_BRIEF.md`, version 2, 2026-10-03.
- Main regulations URL / version / relevant clauses: TBD
- Specific task regulations / saved version: owner-supplied `C:/Users/szmef/Downloads/Rules - SPORT & HEALTHCARE.pdf`, reviewed October 3. Clause 14 states awarded proprietary copyrights are not transferred to the sponsor.
- Coding and submission windows: Greg confirms reveal at 11:00 October 3; internal submission target before 11:00 October 4. Task rules contain `11:00 PM` wording inconsistent with the supplied agenda; do not silently treat that wording as resolved. Main-rules review/organizer clarification remains pending.
- Evaluation criteria and weights: Idea & Innovation 30%, Relation to Category 20%, Practical Applicability / Usability 20%, Design 20%, Completeness & Implementation Value 10%.
- Existing code / starter eligibility: task Details permit properly cited existing resources and require distinguishing pre-existing work. Starter and approved imports remain separately disclosed.
- AI assistance / application AI restrictions: task Details permit AI assistance, require disclosure of significant AI/resources, and leave responsibility and understanding with the team. Phase 1 uses development assistance, no application model calls.
- Third-party resources / datasets restrictions: TBD
- IP ownership / license / submission obligations: TBD
- Required files and format: title, team name, members, description and a PDF of at most 10 slides; demo/repository/screenshots optional; Polish or English. No submission produced in phase 1.
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

## Implementation baseline and phase 1

The `task-reveal-2026` tag identifies the last state before application implementation,
recorded now, not a claim that this commit existed at 11:00. Post-reveal product planning
and ImageGen concept exploration occurred before this tag; they are disclosed in AI_USAGE.md.
Greg selected visual concept 02 (Opowieść) and authorized a working site for review.
Phase 1 is a synthetic single-run journey, clickable moments, in-memory demo observations
and a printable clinician brief. Real FIT/CGM upload, health-data persistence, authentication
and model narration remain later phases. Approved Python imports are provenance groundwork,
not claimed as new hackathon logic or as already used by this UI demo.
