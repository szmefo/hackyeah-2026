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

## Jak je otworzyć w aplikacji

Najprościej: **Źródła → Scenariusze demo → Wczytaj scenariusz**, potem zgoda na
przetwarzanie i **Połącz pliki i zobacz bieg**. Bieg dostaje tytuł scenariusza
(np. „Scenariusz 4: Luka w danych sensora”) i oznaczenie **Dane syntetyczne**.
Każda karta ma też linki do pobrania obu plików.

Aplikacja serwuje identyczne kopie tych plików z `public/scenarios/<katalog>/`.
Zmieniając pary, zaktualizuj obie lokalizacje (pliki muszą być bajtowo identyczne).

Zasada oznaczania (`/api/import`): import jest oznaczony jako syntetyczny tylko wtedy,
gdy plik FIT i CSV są bajtowo identyczne z jedną ze znanych par (wbudowana para
`public/demo-run.fit` + `public/demo-glucose.csv` oraz cztery scenariusze). Serwer
porównuje je z plikami o stałych ścieżkach w `public/`. Znana para wgrana ręcznie,
bez kliknięcia karty, też zostanie oznaczona jako syntetyczna, bo jej zawartość jest
dokładnie tymi danymi. Każdy inny plik lub zmieniona para to dane wgrane; prośba
o oznaczenie syntetyczne dla takich plików jest odrzucana (`synthetic_mismatch`),
także gdy FIT pochodzi z jednego scenariusza, a CSV z innego.

Ręczny import: wybierz `bieg.fit` i `glukoza.csv` z jednego katalogu i ustaw
strefę Europe/Warsaw.

Regeneracja z katalogu głównego repozytorium:
`engine/.venv/Scripts/python.exe demos/synthetic-scenarios/generate.py`, a potem
skopiuj pary do `public/scenarios/`.
