# Syntetyczne scenariusze demo — Cukier w biegu

**Aplikacja: https://cukier-w-biegu.vercel.app/**

Lokalna kopia na komputerze prezentacyjnym: `C:\_HackYeah2026\tmp\synthetic-scenarios`.
Ten katalog `demos/synthetic-scenarios` jest kopią zapisaną w Git, dostępną dla sędziów
po pobraniu repozytorium. [Instrukcja demo](../../submission/README.md).

DANE SYNTETYCZNE. Wygenerowane skryptem `generate.py` (seed stały), nie pochodzą od pacjenta.
Każdy katalog: `bieg.fit` + `glukoza.csv` (format Dexcom Clarity, czas lokalny Europe/Warsaw).

- **01-niski-cukier-na-plaskim** (start 2026-09-12T08:00:00+02:00): Zwolnienie na płaskim odcinku (44.-54. min) zbiega się z odczytem ~63 mg/dL. Brak podbiegu.
- **02-podbieg-cukier-w-normie** (start 2026-09-19T08:30:00+02:00): Zwolnienie na podbiegu (~78.-86. min), glukoza stabilnie 115-135 mg/dL przez cały bieg.
- **03-podbieg-i-niski-cukier** (start 2026-09-26T09:00:00+02:00): Podbieg i odczyt ~64 mg/dL w tym samym oknie; dane nie rozdzielają wpływu. Pełne pokrycie CGM.
- **04-luka-w-danych** (start 2026-10-01T18:00:00+02:00): Sensor traci sygnał od ~58. minuty do końca biegu; podbieg bez odczytów glukozy.

Upload both files from the same folder with Europe/Warsaw selected. Leave the checkbox for the downloaded website example unchecked: it applies only to the exact built-in demo pair. These four scenarios are entirely synthetic, although this upload path labels them as uploaded data. Regenerate from the repository root with: engine/.venv/Scripts/python.exe demos/synthetic-scenarios/generate.py
