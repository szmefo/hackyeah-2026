# Jury demo guide — Cukier w biegu

**Działająca aplikacja: https://cukier-w-biegu.vercel.app/**

## Najszybsza ścieżka demo

1. Otwórz **Źródła** i kliknij **Wybierz przykładową parę**.
2. Zaznacz zgodę na przetwarzanie i kliknij **Połącz pliki i zobacz bieg**.
3. Porównaj momenty biegu, w tym lukę w danych. Dodaj obserwację.
4. Otwórz **Brief dla lekarza**. Opcjonalna analiza Anthropic wymaga osobnej zgody.

## Cztery dodatkowe scenariusze syntetyczne

Na komputerze prezentacyjnym: **`C:\_HackYeah2026\tmp\synthetic-scenarios`**
(lokalnie: `tmp\synthetic-scenarios`).

W repozytorium, dla sędziów na innym komputerze:
[**demos/synthetic-scenarios**](../demos/synthetic-scenarios/README.md).
Lokalny folder `tmp` nie jest dostępny na GitHubie; jego poprawione pary są
zapisane w katalogu `demos`.

Wybierz `bieg.fit` i `glukoza.csv` z jednego scenariusza, ustaw **Europe/Warsaw**,
zaznacz zgodę na przetwarzanie. Checkbox „Używam pobranej poniżej pary…” pozostaw
odznaczony — służy wyłącznie do wbudowanej pary ze strony.
Wszystkie cztery pary są syntetyczne, choć zwykła ścieżka importu oznacza je jako
dane wgrane. Żaden z tych zestawów nie pochodzi od pacjenta.

Odświeżenie strony usuwa wgrany wynik i obserwacje z pamięci karty.

## Pochodzenie pracy

[Background IP](../BACKGROUND_IP.md) · [AI usage](../AI_USAGE.md) ·
[Third-party resources](../THIRD_PARTY.md) · [Full README](../README.md).
Historia względem `task-reveal-2026` rozdziela importy wcześniejszej pracy i nową
implementację. Starter sprzed wydarzenia oraz importy UltraSoul nie są nową pracą konkursową.

To instrukcja demonstracji. Finalny opis, pitch, prezentacja i zgłoszenie pozostają
do przygotowania zgodnie z wymaganiami zadania.
