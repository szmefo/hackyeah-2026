# Scenariusz demo i pitchu — Cukier w biegu (3 minuty)

Przygotował Claude Code (Anthropic) 2026-10-04 ok. 02:20 (Europe/Warsaw) do przeglądu
przez Grega. Etykiety przycisków, liczby i zdania z aplikacji poniżej sprawdziłem lokalnie
2026-10-04 o 02:13 na buildzie produkcyjnym (`next start`) gałęzi `overnight/phase-3`,
z silnikiem Pythona i bez klucza AI. Dowody (poza Git) leżą w
`.verification/submission-demo/`: zrzuty, `demo-path.json` i PDF briefu (1 strona).

**Ważne:** ta ścieżka działa na publicznej stronie dopiero po porannym deployu.
Przed nim kart scenariuszy w **Źródłach** nie ma, patrz `CHECKLIST.md`.

Główny kontrast to **scenariusz 2 kontra scenariusz 3**. Oba biegi mają ten sam
podbieg pod koniec, ale inną glukozę. W pierwszym aplikacja wskazuje tylko podbieg.
W drugim uczciwie mówi, że danych nie da się rozdzielić. Ten kontrast to sedno pomysłu.

---

## Przygotowanie (15 minut przed wyjściem na scenę)

1. Otwórz Chrome w trybie normalnym (nie incognito) z powiększeniem 100–110%.
   Otwórz trzy karty:
   - **Karta A:** https://cukier-w-biegu.vercel.app/sources — na niej robisz demo na żywo.
   - **Karta B (AI, przygotowana wcześniej):** zaimportuj scenariusz 3 (**Źródła →
     Wczytaj scenariusz** na karcie 3 → zgoda → **Połącz pliki i zobacz bieg**). Potem
     w sekcji **Spójrzmy na ten moment razem** zaznacz zgodę Anthropic i kliknij
     **Przeanalizuj ten moment z AI**. Poczekaj na wynik z plakietką „Interpretacja AI ·
     Anthropic” (do ok. minuty). **Nie odświeżaj tej karty**, bo odświeżenie kasuje wynik.
   - **Karta C (awaryjna):** folder `submission/screenshots/`, otwarty w przeglądarce
     albo w podglądzie zdjęć: `run-scenario-02-desktop.png`, `run-scenario-03-desktop.png`,
     `brief-scenario-03-desktop.png`. Zawsze możesz też przejść do PDF prezentacji.
2. Limit AI wynosi ok. 2 analizy na minutę i 8 na godzinę z jednej sieci. Wi-Fi na hali
   jest wspólne, więc nie klikaj AI „na próbę” tuż przed pitchem. Jedna analiza
   w karcie B wystarczy.
3. Sprawdź, że karta A pokazuje sekcję **Scenariusze demo** z czterema kartami.

---

## Przebieg (≈3:00)

### 0:00–0:25 — Problem

**Mów:**
> „Czternasty kilometr, tempo się sypie. Co to było: podbieg, za szybki start czy
> cukier? Biegacz z cukrzycą typu 1 ma dwa osobne zapisy tego samego biegu: zegarek
> i sensor glukozy. Żeby je porównać, skacze między aplikacjami. Potem lekarz pyta
> »jak idzie z bieganiem?«, a odpowiedź brzmi »różnie«.”

*(Na ekranie karta A, strona Źródła: „Dwa źródła. Jedna oś czasu.”)*

### 0:25–0:45 — Rozwiązanie w jednym zdaniu

**Mów:**
> „Cukier w biegu łączy jeden plik FIT z zegarka i eksport Dexcom Clarity na jednej
> osi czasu. Wybiera trudne momenty i robi z nich jednostronicowy brief do
> diabetologa: co widać, czego nie wiemy i o co zapytać. Wszystkie dane w demo są
> syntetyczne i aplikacja tak je oznacza.”

**Klik:** pokaż sekcję **Scenariusze demo** (cztery karty, plakietka **Dane syntetyczne**).

### 0:45–1:25 — Scenariusz 2: podbieg, glukoza w zakresie

**Kliki (karta A):**
1. Na karcie „Scenariusz 2 · Podbieg, glukoza w zakresie” kliknij **Wczytaj scenariusz**.
2. Zaznacz zgodę „Zgadzam się na przesłanie plików…”.
3. Kliknij **Połącz pliki i zobacz bieg**. Po 1–3 s otworzy się ekran biegu.

**Na ekranie:** tytuł „Scenariusz 2: Podbieg, glukoza w zakresie”, moment
**„Podbieg, glukoza w zakresie · 84. min · 15,0 km”**, nagłówek „Zwolnienie na
podbiegu, glukoza w zakresie.”, a w pasku wybranego okna (74–94 min): **najniższa
glukoza w oknie 119 mg/dL**, tempo 6:47 min/km.

**Mów:**
> „Trzy wykresy, jedna oś: glukoza, tempo z profilem trasy i tętno. W 84. minucie
> tempo spada na podbiegu o 41 metrach przewyższenia. Wszystkie odczyty w oknie
> plus minus 10 minut są w zakresie 70–180, najniższy to 119. Aplikacja mówi
> wprost: to współwystępowanie, nie dowód przyczyny. Pytanie do lekarza też jest
> ostrożne: czy takie zwolnienie przy glukozie w zakresie warto w ogóle omawiać
> w kontekście cukrzycy.”

*(Wskaż kartę **O co spytać lekarza**.)*

### 1:25–2:05 — Scenariusz 3: ten sam podbieg i niski cukier naraz

**Kliki:**
1. Kliknij **Źródła** w górnej nawigacji. Nie odświeżaj strony.
2. Na karcie „Scenariusz 3 · Podbieg i niski cukier naraz” kliknij **Wczytaj scenariusz**.
3. Upewnij się, że zgoda jest zaznaczona, i kliknij **Połącz pliki i zobacz bieg**.

**Na ekranie:** moment **„Dwa sygnały · 85. min · 15,1 km”**, nagłówek „Najniższy
odczyt glukozy w biegu, w tym samym oknie co podbieg.”, **najniższa glukoza w oknie
62 mg/dL**. W **Czego nie wiemy** pojawia się dodatkowe zdanie: „Dane nie pozwalają
rozdzielić wpływu współwystępujących czynników.”

**Mów:**
> „Ten sam podbieg, tylko w tym samym oknie jest odczyt 62. Większość narzędzi
> narysowałaby strzałkę: to przez cukier. My tego nie robimy. Oba sygnały wystąpiły
> razem, więc dane nie rozdzielają ich wpływu i aplikacja mówi to otwarcie. Zamiast
> zgadywać, daje pytanie na wizytę: jak odróżnić spadek glukozy od zmęczenia na
> podbiegu, gdy wystąpiły w tym samym czasie. Ta szczerość to nasza główna myśl.”

### 2:05–2:35 — Obserwacja i brief

**Kliki:**
1. Kliknij **Dodaj obserwację**. Rodzaj: **Odczucia**, minuta jest już ustawiona na
   85. Wpisz krótko, np. „Nogi ciężkie, bez zawrotów głowy.”, i kliknij **Dodaj do briefu**.
2. Kliknij **Brief dla lekarza**.

**Na ekranie:** jedna strona A4 z plakietką **Dane syntetyczne**. Są na niej dystans
16,7 km, czas 1:34:00, pokrycie glukozy 100% i najniższy odczyt 62 mg/dL. Jest też
tabela odczytów poniżej 70 mg/dL (63 i 62 mg/dL w 80. i 85. minucie), sekcje
„Czego dane nie rozstrzygają” i „Pytania na wizytę” oraz Twoja obserwacja.

**Mów:**
> „Biegacz dopisuje to, czego zegarek ani sensor nie zapiszą. Wszystko trafia na
> jedną stronę do wydruku albo PDF (przycisk »Drukuj / zapisz PDF«). Liczby liczy
> kod, nie model. Brak danych zostaje brakiem. Nie ma diagnozy, dawek insuliny ani
> rad o jedzeniu.”

### 2:35–2:50 — AI (karta B, przygotowana wcześniej)

**Klik:** przełącz na kartę B i przewiń do wyniku „Interpretacja AI · Anthropic”.

**Mów:**
> „AI jest opcjonalne i wymaga osobnej zgody. Claude dostaje tylko obliczone fakty,
> bez plików i GPS. Rozważa różne wyjaśnienia, a każde zdanie musi wskazać fakt,
> na którym się opiera. Kod odrzuca liczby wymyślone przez model, pewność
> przyczynową i zalecenia leczenia, a drugie wywołanie sprawdza odpowiedź. Gdy coś
> nie przejdzie, zostają fakty i brief.”

*(Jeśli karta B nie ma wyniku AI, pomiń ten blok i powiedz tylko ostatnie zdanie.)*

### 2:50–3:00 — Zamknięcie

**Mów:**
> „Zbudowane na HackYeah: import CSV, wspólna oś czasu, warstwa kontekstu,
> interfejs, brief i AI z kontrolą. Parser FIT i detektor sygnałów biegu to
> ujawnione wcześniejsze moduły z mojego projektu UltraSoul. Jeden bieg, jeden
> moment, jedna lepsza rozmowa z lekarzem.”

---

## Plan awaryjny

| Problem | Co robisz | Co mówisz |
| --- | --- | --- |
| AI zwraca błąd, limit albo nic nie przychodzi | Nie czekaj. Zostań przy fakcie i briefie. Komunikat w aplikacji kończy się zdaniem „Fakty i pytania z danych pozostają dostępne.” | „Tak to zaprojektowaliśmy: model jest dodatkiem, a fakty i brief działają bez niego.” |
| Import zwraca „Serwer analizy jest chwilowo niedostępny…” (silnik nie działa) | Kliknij logo „Cukier w biegu”, żeby wrócić na stronę główną. Jeśli w tej karcie udał się już wcześniej jakiś import, zostaje on w pamięci karty. Jeśli nie, widać wbudowany bieg syntetyczny „Bieg nad Wisłą” („Spadek tempa zbiegł się z dwoma sygnałami.”), który działa bez silnika. Ma momenty „Luka w danych” i „Dwa sygnały”, a także brief. Możesz też przejść do karty B, bo wynik jest już w pamięci. | „Pokażę to samo na wbudowanym biegu demonstracyjnym.” |
| Brak internetu albo strona nie wstaje | Przejdź do karty C (zrzuty z `submission/screenshots/`) albo do slajdów w PDF. Opowiedz tę samą historię: 2 kontra 3, potem brief. | „Pokażę zrzuty z tej samej ścieżki.” |
| Masz chwilę i laptop z repo | Lokalnie: `scripts/start_engine.ps1` w jednym terminalu, `npm run dev` w drugim, potem http://127.0.0.1:3000. Bez klucza AI zobaczysz „AI nie jest jeszcze podłączone…”, i tak ma być. | — |

Czego **nie** mówić:
- „cukier spowodował spadek tempa” — mów o współwystępowaniu;
- „klinicznie zweryfikowane” — to demo na danych syntetycznych;
- „AI sprawdza poprawność medyczną” — drugie wywołanie to kontrola jakości, nie weryfikacja medyczna.

## Pytania jury (krótkie odpowiedzi)

- **Dlaczego nie wskazujecie przyczyny?** Bo z jednego biegu się nie da. Gdy podbieg
  i niski odczyt wystąpiły razem, rzetelna odpowiedź brzmi „nie wiadomo”, a właściwe
  pytanie trafia do lekarza.
- **Skąd okno ±10 minut?** CGM mierzy glukozę w płynie śródmiąższowym, z opóźnieniem
  i co kilka minut. Dlatego porównujemy okno czasu, a nie pojedynczą sekundę.
- **Co z prywatnością?** Pliki są przetwarzane w pamięci, bez bazy danych. Wynik nie
  zawiera GPS ani oryginalnych plików, a odświeżenie strony usuwa wynik. AI ma osobną
  zgodę i dostaje tylko obliczone fakty.
- **Co jest Waszą pracą, a co wcześniejszą?** Wcześniejsze są trzy moduły UltraSoul:
  parser FIT, adapter i detektor sygnałów biegu, z testami, zaimportowane bajt w bajt
  (szczegóły w BACKGROUND_IP.md). Reszta powstała po ogłoszeniu zadania: CSV, oś
  czasu, kontekst, UI, brief, AI i scenariusze.
- **Co dalej?** Najpierw testy z prawdziwymi biegaczami i diabetologiem. Potem widok
  kilku biegów i inne profile cukrzycy. Celowo nie ma ich w MVP.
