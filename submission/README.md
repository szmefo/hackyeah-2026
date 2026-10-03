# Jury demo guide — Cukier w biegu

**Działająca aplikacja: https://cukier-w-biegu.vercel.app/**

## Najszybsza ścieżka demo

1. Otwórz **Źródła**. W sekcji **Scenariusze demo** kliknij **Wczytaj scenariusz**
   na jednej z czterech kart (albo **Wybierz przykładową parę** niżej na stronie).
2. Zaznacz zgodę na przetwarzanie i kliknij **Połącz pliki i zobacz bieg**.
3. Tytuł biegu pokazuje wybrany scenariusz, a ekran ma oznaczenie **Dane syntetyczne**.
   Porównaj momenty biegu, w tym luki w danych. Dodaj obserwację.
4. Otwórz **Brief dla lekarza**. Opcjonalna analiza Anthropic wymaga osobnej zgody.

## Cztery scenariusze syntetyczne

Każdy jest dostępny jednym kliknięciem na stronie **Źródła**:

1. **Niski cukier na płaskim** — zwolnienie na płaskim odcinku w tym samym czasie
   co niższy odczyt glukozy.
2. **Podbieg, cukier w normie** — zwolnienie na podbiegu przy stabilnej glukozie.
3. **Podbieg i niski cukier naraz** — oba sygnały w jednym oknie; dane nie
   rozdzielają ich wpływu.
4. **Luka w danych sensora** — brak odczytów w drugiej części biegu, pokazany
   jako luka, bez uzupełniania.

Karty mają też linki do pobrania pliku FIT i CSV. Te same pary są w repozytorium:
[**demos/synthetic-scenarios**](../demos/synthetic-scenarios/README.md).
Wszystkie pięć par (cztery scenariusze i para wbudowana) aplikacja oznacza jako
**Dane syntetyczne** po bajtowym porównaniu z plikami na serwerze, również przy
ręcznym wgraniu pobranych plików. Każdy inny plik jest oznaczany jako dane wgrane.
Żaden z tych zestawów nie pochodzi od pacjenta.

Odświeżenie strony usuwa wgrany wynik i obserwacje z pamięci karty.

## Pochodzenie pracy

[Background IP](../BACKGROUND_IP.md) · [AI usage](../AI_USAGE.md) ·
[Third-party resources](../THIRD_PARTY.md) · [Full README](../README.md).
Historia względem `task-reveal-2026` rozdziela importy wcześniejszej pracy i nową
implementację. Starter sprzed wydarzenia oraz importy UltraSoul nie są nową pracą konkursową.

To instrukcja demonstracji. Finalny opis, pitch, prezentacja i zgłoszenie pozostają
do przygotowania zgodnie z wymaganiami zadania.
