# Brief produktu — HackYeah 2026, Open Task „SPORT & HEALTHCARE" (wersja ostateczna)

Status: spec do implementacji. Wersja 2, 2026-10-03 (Europe/Warsaw), po recenzji i akceptacji Grega.
Nazwa robocza: **Cukier w biegu** (Greg może zmienić).

---

## 0. Instrukcja dla kodującego — przeczytaj najpierw

1. **Katalog roboczy:** repozytorium Git jest w `C:\hackyeah-2026` (GitHub: `szmefo/hackyeah-2026`). Katalog `C:\_HackYeah2026` nie jest repozytorium. Cała praca idzie w `C:\hackyeah-2026`.
2. **MVP = jedna ścieżka, dopracowana do końca:** dorosły biegacz z cukrzycą typu 1 i sensorem ciągłym (CGM). Upload FIT + CSV z Dexcom → wspólna oś czasu → wybrany moment biegu z tym, co współwystąpiło → jednostronicowy brief do rozmowy z diabetologiem. Online, z telefonu, z danymi demo. Dopóki to nie działa w przeglądarce na Vercelu, nic innego nie powstaje.
3. **Potem, w tej kolejności:** widok okresu → profile typ 2 i stan przedcukrzycowy z soczewkami celu → Garmin przez login i hasło (twardy budżet 2 godziny) → polish → zgłoszenie.
4. **Kolejność commitów z rozdziału 19 jest obowiązkowa.** Pierwszy commit po tagu to import bajt w bajt, bez zmian.
5. **Zasady z rozdziału 5 są nienegocjowalne**, w szczególności: współwystępowanie zamiast przyczyny, zero dawek leków, liczby na ekranie tylko z faktów policzonych kodem.

---

## 1. Kontekst konkursu (fakty z regulaminu i opisu zadania)

- Zadanie otwarte: stworzyć rozwiązanie, które pomaga ludziom świadomie i aktywnie dbać o zdrowie, aktywność fizyczną lub dobrostan. Wybrać **konkretną grupę użytkowników i konkretną potrzebę**. Pokazać **jasną ścieżkę użytkownika**, gdzie rozwiązanie daje praktyczną wartość, oraz jak pomaga **zrozumieć sytuację i zrobić osiągalny następny krok**. Uwzględnić dostępność, motywację i wysiłek regularnego używania.
- Kierunki z opisu, w które trafiamy wprost: „zrozumienie wzorców w aktywności, regeneracji i rutynach", „przygotowanie do wizyt lekarskich i komunikacja z profesjonalistami", „organizowanie informacji zdrowotnych i dzielenie ich z opiekunami".
- Kryteria i wagi: **Idea & Innovation 30%**, **Relation to Category 20%**, **Practical Applicability / Usability 20%**, **Design 20%**, **Completeness & Implementation Value 10%**. Minimum 50% punktów w fazie 1. Faza 1: ocena zgłoszeń na platformie. Faza 2: pitch finalistów na żywo.
- Nagroda 8 000 PLN. Zespół 1–6 osób. Pracujemy solo.
- Zgłoszenie MUSI zawierać: tytuł projektu, nazwę zespołu, listę członków, opis projektu, **PDF max 10 slajdów**. MOŻE zawierać: zrzuty ekranu, repozytorium, link do demo, grafiki. PL lub EN. Platforma: Challenge Rocket / HackTribe.
- Terminy: regulamin zadania mówi „start nie wcześniej niż 11:00 PM 3.10, oddanie nie później niż 11:00 PM 4.10"; oficjalna agenda mówi 11:00 w obu dniach. **Oddajemy przed 11:00 4.10.** Checkpoint 20:00 3.10: pierwszy draft. Zmiany po terminie nie są oceniane.
- AI: dozwolone na każdym etapie. **Trzeba ujawnić** istotne użycie AI, zewnętrznych modeli, API, datasetów, bibliotek. Nie trzeba podawać promptów ani procentu kodu z AI. Jury ocenia realną pracę techniczną i to, czy zespół **rozumie i potrafi obronić** każdą decyzję, także kod z AI.
- Istniejące zasoby: wolno, **jeśli zacytowane** i **wyraźnie oddzielone** od pracy z hackathonu. Przedstawianie gotowego rozwiązania jako pracy z hackathonu lub nieujawnienie znaczącej części istniejącego rozwiązania = dyskwalifikacja.

Konsekwencja: silnik analizy biegu z UltraSoul wchodzi jako **Background IP** z pełnym wpisem pochodzenia; wszystko wokół glukozy, profilu, Garmina w tym repo, UI i briefu powstaje na hackathonie i jest tak oznaczone. Repo ma do tego rejestry (`BACKGROUND_IP.md`, `AI_USAGE.md`, `THIRD_PARTY.md`, `DECISIONS.md`), procedurę w `docs/HACKATHON.md` i tag `task-reveal-2026` do założenia przed pierwszym commitem implementacji.

---

## 2. Pitch w jednym zdaniu

Glukoza z sensora potrafi już wyświetlić się na zegarku, ale po biegu nikt nie kładzie jej obok tempa, tętna i terenu, żeby uczciwie powiedzieć, co współwystąpiło z załamaniem na 14. kilometrze, czego dane nie rozstrzygają i o co zapytać diabetologa. My to robimy i oddajemy jedną stronę do rozmowy z lekarzem.

---

## 3. Dla kogo

| Profil | Kto to | Leczenie (typowe) | Pomiar (typowy) | Czego chce |
|---|---|---|---|---|
| **Typ 1** (MVP) | Osoba z cukrzycą autoimmunologiczną, rozpoznaną w dzieciństwie **lub w dorosłości**, zawsze na insulinie | Pompa albo pen | Sensor ciągły (Dexcom, Libre), odczyt co 5 min | Biegać dłużej bez niedocukrzeń na trasie; mieć konkret na wizytę |
| **Typ 2** (po MVP) | Zwykle 40+, dostał „ruszaj się" od lekarza | Leki doustne, czasem insulina | Glukometr 1–3 punkty dziennie, coraz częściej sensor | Zobaczyć związek biegania z cukrem; nie zrobić sobie krzywdy |
| **Stan przedcukrzycowy** (po MVP) | Największa grupa, często bez poczucia „choroby" | Bez leków | Glukometr albo nic | Zacząć biegać i nie odpuścić |

**Poza zakresem:** cukrzyca ciążowa, dzieci, LADA/MODY jako osobne opcje (mieszczą się w typie 1 lub 2 przez wybór leczenia).

Dwie cechy ważniejsze od typu, zbierane osobno:

- **Leczenie:** `insulin` (pompa lub pen) / `oral_hypo_risk` (leki doustne, które mogą obniżyć cukier w wysiłku: pochodne sulfonylomocznika, glinidy) / `oral_low_risk` (metformina, inhibitory SGLT2, agoniści GLP-1, inhibitory DPP-4) / `none`. W formularzu podpowiedź: „Nie wiesz, do której grupy należą Twoje leki? Zapytaj lekarza lub farmaceutę, w aplikacji zaznacz 'nie wiem'". Opcja `unknown` traktowana jak `oral_hypo_risk` (ostrożniej).
- **Pomiar:** `cgm` / `glucometer` / `none`. Sensor daje gęsty strumień. Glukometr daje punkty przed i po biegu, więc trasa jest nieobserwowana i aplikacja mówi to wprost.

---

## 4. Problem, prostym językiem

- Sensor i zegarek mogą pokazać glukozę na nadgarstku w trakcie biegu. Po biegu te dane rozchodzą się do dwóch aplikacji i nikt ich razem nie czyta.
- Biegacz po załamaniu na 14. km zgaduje: teren, tempo, cukier? Na wykresie tempa wyglądają identycznie, a reakcja na każde jest inna.
- Diabetolog pyta „jak wysiłek?", pacjent odpowiada „różnie". Ustalenia o posiłku przed startem i węglowodanach na trasie opierają się na wrażeniu, nie na danych.
- Osoba z typem 2 lub stanem przedcukrzycowym nie widzi związku między biegiem a cukrem. Brak sprzężenia zabija nawyk.

---

## 5. Zasady produktu (nienegocjowalne)

1. **Fakty liczy kod, model tylko je komentuje.** Każda liczba na ekranie pochodzi z deterministycznej funkcji w Pythonie i jest renderowana przez UI **bezpośrednio z obiektu faktów**, nigdy z tekstu modelu. Model dostaje fakty z identyfikatorami i pisze zdania, które odwołują się do tych identyfikatorów. Model nie widzi surowych strumieni.
2. **Współwystępowanie, nie przyczyna.** Nigdy nie piszemy „spadek tempa spowodowała glukoza". Piszemy, co **współwystąpiło** w oknie momentu i czy dane pozwalają to rozdzielić. Wzór zdania: „Spadek tempa zbiegł się z niskim odczytem glukozy. Na tym odcinku był też podbieg. Te dane nie pozwalają rozdzielić ich wpływu."
3. **CGM mierzy płyn śródtkankowy, nie krew.** Przy szybkich zmianach odczyt jest opóźniony o 5–15 minut. Dopasowanie do momentu biegu działa na **oknach ±10 minut**, nigdy na jednej minucie, i mówi o tym w UI („odczyt z okna ±10 min").
4. **„Czego nie wiem" to wynik pierwszej klasy.** Każdy bieg i okres ma listę `unknowns` po polsku: „Brak glukozy między 32. a 51. minutą, nie oceniam tego odcinka.", „Brak tętna, nie oceniam intensywności.", „Nie wiem, czy były węglowodany na trasie — nic nie zapisano." Zamiast „Niska pewność" piszemy „Za mało danych".
5. **Słowa biegacza to dane, nie instrukcje.** Notatka do biegu idzie do modelu w ogrodzonym bloku z adnotacją, że to tekst od człowieka. Cytaty weryfikowane dosłownie przeciw oryginałowi.
6. **Problem i mocne strony osobno.** Oś momentów, które kosztowały, i osobna lista tego, co poszło dobrze. Dobry bieg nie czyta się jak lista porażek.
7. **Język SMS-a od mądrego kumpla-trenera.** Gotowe porcje, pierwiastki po polsku, strefy tętna z kontekstem, bez biochemii. Zakazane wzorce w tekście dla usera: `mg/kg`, `g/kg`, `CHO`, `%HRmax`, surowe `Z1:`–`Z5:`, „Niska pewność". Wyjątek: brief dla lekarza może używać `mg/dL` i minut.
8. **Jedna myśl na ekran.** Duża liczba lub jedno zdanie pierwsze, kontekst pod nim.
9. **Zero zaleceń dotyczących leków i zero zaleceń żywieniowych na MVP.** Żadnego „weź mniej insuliny", żadnego „żel wcześniej", żadnego planu jedzenia na zawody. Aplikacja daje: fakty, współwystępowanie, braki danych, **pytania do specjalisty** i **obserwacje do zebrania** (rozdział 9.5). Regex po stronie serwera blokuje frazy o dawkach („jednostek", „j. insuliny", „zmniejsz dawkę", „zwiększ dawkę", „bolus", „baza").
10. **Disclaimer na każdym ekranie z glukozą i w briefie**, max 2 zdania: „To nie jest porada medyczna. Decyzje o lekach i jedzeniu w cukrzycy podejmuj z lekarzem."
11. **Dane syntetyczne podpisane na ekranie**, nie tylko w README. Badge „DANE SYNTETYCZNE" przy każdym wykresie glukozy z generatora.
12. **Zgoda na dane zdrowotne przed pierwszym zapisem** (RODO art. 9). Bez zgody rekord glukozy nie powstaje. „Usuń wszystko" kasuje naprawdę.
13. **Nie przechowujemy GPS ani plików binarnych.** Z FIT-a wyciągamy strumienie liczbowe, plik wyrzucamy po sparsowaniu.
14. **„Niżej po biegu" to obserwacja, nie sukces.** Nigdy „świetnie, cukier spadł". Zawsze „po biegu odczyt był niższy o X niż przed; co to znaczy dla Ciebie, omów z lekarzem".
15. **Awaria modelu nie blokuje niczego.** Ekran biegu i brief renderują się z faktów i szablonów deterministycznych; narracja modelu jest warstwą dodatkową.

---

## 6. Źródła danych

### 6.1 Biegi, droga A: upload plików FIT (MVP)

- Wiele plików naraz (drag & drop), `.fit`. GPX poza MVP.
- Parser: `garmin-fit-sdk` (oficjalne SDK Garmina, Python). Wyciągamy `time_seconds`, `heartrate`, `velocity_smooth` → `pace_per_km` (min/km), `altitude`, `cadence`, `distance`, czas startu (UTC + offset lokalny), sport, urządzenie, pauzy stopera. Odrzucamy multisport.
- Deduplikacja po czasie startu i długości.
- Pola developerskie z glukozą (Dexcom Connect IQ zapisuje glukozę do FIT) czytamy, jeśli są, jako źródło `fit_dev_field`. Nice-to-have, nie blokuje.

### 6.2 Biegi, droga B: konto Garmin Connect przez login i hasło (po MVP, budżet 2 h)

- Biblioteka `garminconnect` 0.3.13 (MIT, cyberjunky/python-garminconnect), loguje się jak użytkownik. Oficjalne API partnerskie wymaga zatwierdzenia aplikacji, nie zmieści się w 24 h.
- Przebieg: e-mail i hasło → kod MFA, jeśli konto go wymaga → wybór okresu (domyślnie 6 tygodni) → lista aktywności typu bieg → pobranie FIT każdej → ten sam parser co upload. Postęp „pobrano 7 z 12".
- **Pułapki znane z pilota UltraSoul (2026-09):**
  - `login(return_on_mfa=True)` wraca wcześnie w obu ścieżkach (MFA i bez); po zalogowaniu zawsze załadować profil, złapać id konta, wyczyścić hasło z pamięci.
  - Stan MFA żyje w **jednym obiekcie `Garmin` w jednym procesie**; `resume_login` ignoruje przekazany stan. Oczekujący login = aktor w pamięci procesu, nigdy serializowany, nigdy w DB ani kolejce. **Serwis Pythona musi być długożyjącym procesem, nie funkcją serverless.**
  - Jedna aktywna próba na usera; TTL 5 min; max 3 błędne kody.
  - Garmin blokuje czasowo przy wielu próbach. Nasz rate limit: odstęp między ręcznymi synchronizacjami, limit 30 aktywności na pierwszą synchronizację.
- **Bezpieczeństwo:** hasło nigdy w bazie, logach ani odpowiedziach API. Po zalogowaniu trzymamy tylko wyeksportowaną sesję (tokeny), zaszyfrowaną symetrycznie kluczem z env. „Odłącz Garmin" usuwa sesję.
- **Szara strefa:** regulamin Garmina nie błogosławi nieoficjalnych klientów. Nazywamy to wprost w `THIRD_PARTY.md` i na slajdzie o ryzykach, z planem migracji na oficjalne Garmin Health API po hackathonie.
- **Twardy budżet 2 godziny**, uruchamiany dopiero, gdy MVP działa online. Jeśli MFA nie przejdzie w budżecie, demo jedzie na FIT, a Garmin jest „w budowie" na slajdzie. To decyzja Grega.

### 6.3 Glukoza

1. **CSV z Dexcom Clarity (MVP).** Kolumny m.in. `Timestamp (YYYY-MM-DDThh:mm:ss)`, `Event Type` (`EGV` = odczyt, `Insulin`, `Carbs`, `Exercise`), `Glucose Value (mg/dL)`. Czytamy `EGV`. Wartości tekstowe `Low` / `High` zostają **flagami poza zakresem** (`below_range` / `above_range`), nie liczbami; na wykresie rysowane jako znacznik przy krawędzi zakresu, w faktach liczone jako „poniżej 40" / „powyżej 400" bez wartości. Rekordy `Carbs` i `Insulin` zachowujemy wyłącznie jako znaczniki na osi, bez wnioskowania o dawkach.
2. **CSV z LibreView (po MVP).** Dwie linie nagłówka, kolumny m.in. `Device Timestamp` (`DD-MM-YYYY HH:MM`), `Record Type` (0 = historyczny co 15 min, 1 = skan), `Historic Glucose mg/dL`, `Scan Glucose mg/dL`. Czytamy typy 0 i 1.
3. **Ręczne wpisy z glukometru (po MVP, przy profilach typ 2 / stan przedcukrzycowy).** Data/godzina, wartość, kontekst (`przed biegiem` / `w trakcie` / `po biegu` / `inne`), notatka.
4. **Pola developerskie z FIT** (6.1), gdy obecne.

Jednostki: domyślnie **mg/dL**; przełącznik na mmol/L (÷ 18,0) tylko jeśli zostanie czas. Strefa czasowa: CSV z sensora jest w czasie lokalnym bez strefy, FIT w UTC z offsetem; user potwierdza strefę przy imporcie, domyślnie `Europe/Warsaw`.

### 6.4 Notatka i obserwacje do biegu

Pole tekstowe „co się działo?" przy każdym biegu (z Garmina wstępnie wypełnione opisem aktywności). Osobno **obserwacje strukturalne**, które user może zaznaczyć: „jadłem węglowodany w trakcie" (z przybliżonym czasem), „postój", „zawroty / drżenie / głód", „upał". To są dane użytkownika i trafiają na oś czasu jako znaczniki.

---

## 7. Profil użytkownika

Onboarding, jedno pytanie na ekran, pasek postępu, powrót.

| Pole | Wartości | Co zmienia |
|---|---|---|
| `diabetes_type` | `type1` / `type2` / `prediabetes` | Ton, które fakty na pierwszym planie, treść disclaimera. MVP obsługuje `type1`; pozostałe włączane w bloku 5 planu |
| `therapy` | `insulin` / `oral_hypo_risk` / `oral_low_risk` / `none` / `unknown` | Przy `insulin`, `oral_hypo_risk`, `unknown`: minimum glukozy, czas poniżej 70 i 54, trend przed momentami. Przy `oral_low_risk` / `none`: trendy przed/po |
| `glucose_source` | `cgm` / `glucometer` / `none` | Gęsty vs rzadki pomiar → ile idzie do „czego nie wiem" |
| `goal` | `start_running` / `improve` / `race` | Soczewka (rozdział 10) |
| `race` (gdy `goal=race`) | nazwa, dystans km, data | Pytania do lekarza przed startem, lista braków danych |
| `max_hr` | liczba lub puste | Strefy tętna; puste → szacunek z wieku oznaczony jako szacunek i wpis do unknowns |
| `age`, `sex` | opcjonalne | Tylko do szacunku `max_hr` |
| `health_data_consent` | bool, wymagane do zapisu glukozy | Bramka RODO art. 9 |

---

## 8. Silnik sygnałów — Background IP z UltraSoul

Import wyłącznie trzech modułów i ich testów, po decyzji Grega (podjęta), z wpisem w `BACKGROUND_IP.md`: repo `szmefo/UltraSoulAI`, ścieżka, SHA commitu źródłowego, suma kontrolna SHA-256 każdego pliku, data importu ze strefą, ścieżka docelowa.

| Plik źródłowy | Co robi | Zależności | Adaptacja (osobny commit po imporcie) |
|---|---|---|---|
| `backend/app/services/run_signal_extractor.py` (1232 linie) | Czysty ekstraktor: strumienie + `ProfileCtx(max_hr, …)` → `RunSignals` (`Moment[]`, `Strength[]`, metryki, `confidence`). Zero DB, zero LLM | `pydantic` | brak |
| `backend/app/services/fit_parser.py` (426 linii) | FIT → strumienie `{"data": [...], "original_size": N}`, czas startu, urządzenie, pauzy, odrzucenie multisportu | `garmin-fit-sdk`, `fastapi.HTTPException` | usunąć zależność od FastAPI: własny `FitParseError`, mapowanie na HTTP w warstwie API |
| `backend/app/services/fit_adapter.py` (197 linii) | Wynik parsera → płaskie listy `heartrate` / `pace_per_km` (min/km) / `altitude` / `cadence` / `time_seconds` | brak | brak |
| `backend/tests/test_run_signal_extractor.py`, `test_fit_parser_alignment.py`, `fit_fixtures.py` | Testy i fixture'y | `pytest` | ścieżki importów |

Co silnik wykrywa (progi v1):

- **Momenty** (`MomentType`): `decoupling` (dryf tętno/tempo > 5%), `cliff` (załamanie tempa > 15% ponad bazę, liczone na GAP, czyli tempie skorygowanym o nachylenie), `positive_split` (druga połowa > 5% wolniejsza), `grade_adjustment` (informacyjny: surowe tempo vs GAP różnią się > 10%, czyli „to był podbieg"), `cadence_decay` (spadek kadencji szybszy niż 1,5 kroku/min na 10 minut).
- **Mocne strony** (`StrengthType`): `negative_split`, `even_pacing`, `cardiac_steady`, `cadence_stable`, `strong_finish`.
- **Severity** `low/medium/high`; strumień < 10 min → niska pewność całości.
- Pomocnicze: `sanitize_pace_stream` (odcina artefakty GPS do pasma 2–20 min/km), `grade_adjusted_pace`, `calculate_hr_zones`, `cumulative_distance_m`, `lead_moment`, `run_dot` (zielona/żółta/czerwona kropka na bieg).

Każdy `Moment` ma indeks czasu i dystans, do którego doklejamy glukozę.

---

## 9. Nowe moduły (powstają na hackathonie)

Każdy moduł w 9.1–9.5 jest czysty: bez DB, bez LLM, z testami.

### 9.1 `glucose_parsers.py`
Wejście: CSV (Dexcom na MVP, Libre później) lub lista wpisów ręcznych. Wyjście: `GlucoseReading(ts_utc, value_mgdl: int | None, range_flag: none|below_range|above_range, source: cgm|scan|manual|fit_dev_field, kind: egv|carbs|insulin|note)`. Autodetekcja formatu po nagłówku. mmol/L → mg/dL, jeśli plik tak raportuje.

### 9.2 `glucose_align.py`
Wejście: `RunSignals`, oś czasu biegu, `GlucoseReading[]`, `glucose_source`. Wyjście `GlucoseFacts`, każdy fakt z identyfikatorem (`g.min`, `g.coverage`, …), wartością, jednostką i polem `basis` (na czym policzony):

- `coverage_pct`: procent czasu biegu, dla którego istnieje odczyt w promieniu 10 min. Poniżej 60% → unknown „glukoza niepełna" i **wszystkie fakty czasowe liczone tylko na pokrytych odcinkach**, z podaniem, które odcinki są pokryte.
- CGM: interpolacja liniowa między odczytami **tylko** przy przerwie ≤ 15 min; każda interpolacja zapisana w `basis` („interpolacja między 32:10 a 41:55"). Większa luka = brak danych, nie zgadujemy.
- Glukometr: brak interpolacji. Punkty to zdarzenia („przed: 142, po: 96"); zmiana to różnica dwóch punktów z adnotacją „trasa nieobserwowana".
- Fakty na bieg: `start`, `end`, `min` (+ minuta), `max`, `delta`, `minutes_below_70`, `minutes_below_54`, `minutes_above_180`, `minutes_above_250` (każdy z `covered_minutes` jako mianownikiem), `slope_first_30min`, liczba odczytów `below_range` / `above_range`, znaczniki `carbs`/`insulin`/obserwacji usera na osi (tylko czas, bez wnioskowania).
- Dla każdego `Moment`: `glucose_window` = odczyty w oknie ±10 min, `glucose_min_in_window`, `trend_10min_before` (mg/dL/min, tylko jeśli ≥ 2 odczyty), `below_70_in_window: bool`, `data_present: bool`.

### 9.3 `moment_context.py` — co współwystąpiło (nie: co spowodowało)
Dla każdego momentu problemowego zwraca **zbiór obecnych czynników** z dowodem, bez wyboru „zwycięzcy":

| Czynnik | Reguła obecności (v1) | Dowód w faktach |
|---|---|---|
| `low_glucose_nearby` | w oknie ±10 min odczyt < 70 lub `below_range` | `g.moment.min_in_window` |
| `falling_glucose` | trend 10 min przed ≤ −1,5 mg/dL/min i wartość w oknie < 100 | `g.moment.trend_10min_before` |
| `uphill` | w oknie nachylenie > 4% lub moment typu `grade_adjustment` | `s.moment.grade_pct` |
| `fast_start` | pierwszy kwartyl szybszy o > 8% od mediany tempa biegu | `s.first_quartile_vs_median` |
| `heat` | temperatura startu > 24 °C (tylko jeśli pogoda dostępna, 9.6) | `w.temp_c` |
| `no_glucose_data` | `data_present == false` | `g.moment.data_present` |

Wyjście: `MomentContext(moment_id, factors: list[Factor], separable: bool, template_key)`. `separable` jest `false`, gdy obecne są ≥ 2 czynniki inne niż `no_glucose_data`. Szablony zdań deterministycznych (po polsku) dla każdej kombinacji, używane zawsze, także gdy model działa. Przykłady:

- tylko `low_glucose_nearby`: „Spadek tempa zbiegł się z niskim odczytem glukozy (okno ±10 min). Innych czynników w danych nie widzę."
- `low_glucose_nearby` + `uphill`: „Spadek tempa zbiegł się z niskim odczytem glukozy. Na tym odcinku był też podbieg. Te dane nie pozwalają rozdzielić ich wpływu."
- tylko `uphill`: „Spadek tempa przypada na podbieg; po korekcie o nachylenie tempo nie załamało się. Glukoza w tym oknie była w zakresie."
- `no_glucose_data`: „W tym miejscu nie mam odczytu glukozy, więc nie wiem, czy miała z tym związek."

### 9.4 `period_aggregator.py`
Wejście: lista `(RunSignals, GlucoseFacts, MomentContext[], meta)` z zakresu dat. Wyjście `PeriodFacts` z identyfikatorami: liczba biegów i km, biegi z glukozą vs bez (z pokryciem), liczba biegów z odczytem < 70 w trakcie, mediana minuty pierwszego odczytu < 90 (tylko dla biegów z pokryciem ≥ 60%), rozkład czynników współwystępujących w momentach problemowych (ile razy `low_glucose_nearby`, ile `uphill`, ile nierozdzielnych), mocne strony powtarzalne, `unknowns` per bieg, dla glukometru: zestawienie „przed / po" per bieg jako obserwacje.

### 9.5 `observations.py` — obserwacje do zebrania (zamiast eksperymentów)
Jedna propozycja na bieg, z zamkniętej listy, wybrana po tym, czego **brakowało** w danych, nigdy interwencja:

- „Zapisz godzinę, o której zjadłeś coś przed startem." (gdy brak znacznika posiłku i glukoza spada od początku)
- „Zaznacz w notatce, kiedy i co jadłeś na trasie." (gdy brak znaczników `carbs`, a jest odbicie glukozy)
- „Sprawdź odczyt 10 minut przed startem i zapisz go." (gdy brak odczytów w pierwszych 10 min)
- „Zaznacz postoje." (gdy klif zbiega się z brakiem ruchu)
- „Po biegu zmierz glukometrem i zapisz." (profil `glucometer`)

Po następnym biegu aplikacja pokazuje, czy luka została wypełniona („dane są / nadal brak"). Zero porad żywieniowych, zero porad o lekach.

### 9.6 `weather.py` (opcjonalne)
Open-Meteo archive API po czasie startu i lokalizacji zaokrąglonej do 0,1° (nieprzechowywanej). Daje temperaturę do czynnika `heat`. Bez tego `heat` nie występuje.

### 9.7 Warstwa językowa (LLM) — dodatkowa, nieblokująca
- UI renderuje **wszystkie liczby i etykiety czynników z faktów** (9.2–9.4) i **zdania z szablonów** (9.3). To działa bez modelu.
- Model dostaje: fakty z identyfikatorami, `MomentContext[]`, `unknowns`, profil, cel, ogrodzoną notatkę, zasady językowe i listę zakazanych wzorców. Zwraca ścisły JSON: `headline` (jedno zdanie), `narrative[]` (każdy element: `text` + `fact_ids[]`, do których się odnosi), `ask_your_doctor[]`, `strengths_text[]`. **Model nie przepisuje liczb** — w tekście odwołuje się do faktów przez identyfikator (`{g.min}`), a UI podstawia wartość z faktów.
- Walidacja: JSON parsowalny (tolerancja na opakowanie w markdown); każde `fact_ids` istnieje; brak surowych liczb w `text` poza placeholderami; regex zakazanych wzorców i fraz o dawkach; cytaty z notatki są podciągiem oryginału. Niezaliczone → jedna ponowna próba z krytyką → fallback: ekran bez narracji modelu, z szablonami. Awaria modelu nigdy nie blokuje analizy ani briefu.
- Dostawca: decyzja Grega. Jeśli Anthropic Claude: thinking domyślnie włączone i dzieli `max_tokens` z odpowiedzią (przy budżecie < 4000 ustawić `thinking` jawnie), brak `temperature`, `stop_reason: "refusal"` jako HTTP 200, dodać blok o zwięzłości. Jeśli OpenAI: structured outputs ze schematem JSON. Jedna funkcja `phrase(facts) -> Narrative | None`.

---

## 10. Cel użytkownika jako soczewka

Te same fakty, inny wybór i ton. Żadna soczewka nie generuje zaleceń żywieniowych ani lekowych.

- **`start_running`.** Headline to mocna strona, jeśli jakakolwiek jest. Fakty: czy glukoza spada przy krótkich biegach, zestawienie przed/po jako obserwacja („po biegu niżej o 18 niż przed; co to znaczy, omów z lekarzem"). Obserwacje do zebrania o minimalnym koszcie. Widok okresu: regularność („biegasz 2 z 3 zaplanowanych dni").
- **`improve`.** Headline to lead moment i jego czynniki. Widok okresu: rozkład czynników współwystępujących, trend minuty pierwszego spadku, czy luki w danych się domykają.
- **`race` (nazwa, dystans, data).** Fakty z najdłuższych biegów: mediana minuty pierwszego odczytu < 90, najdłuższy bieg jako procent dystansu zawodów, stabilność kadencji. Wyjście: **lista pytań do lekarza przed startem** („jak zabezpieczyć odcinek po 60. minucie, w którym w 4 z 5 długich biegów glukoza spadła poniżej 90") i **lista braków** („najdłuższy bieg to 55% dystansu zawodów, dane o drugiej połowie nie istnieją"). Bez planu jedzenia na trasę.

---

## 11. Ekrany (web, responsywny, mobile-first, ciemny motyw)

Oznaczenie: **[MVP]** musi być w pionowym plastrze; **[2]** po MVP.

1. **[MVP] Onboarding** — typ (na MVP tylko typ 1 aktywny, pozostałe „wkrótce" do bloku 5), leczenie, pomiar, cel, zgoda. Jedno pytanie na ekran.
2. **[MVP] Źródła** — karty „Wgraj FIT", „Glukoza (CSV Dexcom)", **[2]** „Połącz Garmin", **[2]** „Wpis z glukometru", **[2]** „CSV Libre". Każda karta ma stan pusty, ładowanie, błąd z konkretną akcją.
3. **[MVP] Biegi** — lista z kropką `run_dot`, datą, dystansem, czasem, ikoną pokrycia glukozy (procent). Badge „DANE SYNTETYCZNE" gdy dotyczy.
4. **[MVP] Bieg** — ekran kluczowy. Góra: headline (z szablonu lub modelu). Wykres: tempo lub GAP (przełącznik), tętno, wysokość w tle, **glukoza z pasmem 70–180 i zaznaczonymi lukami pokrycia**, znaczniki momentów klikalne, znaczniki `carbs` / obserwacji usera, odczyty `Low`/`High` jako znaczniki przy krawędzi. Klik w moment → karta: liczby z faktów, **lista obecnych czynników z dowodem**, zdanie z szablonu, adnotacja „okno ±10 min". Pod wykresem trzy kolumny: **Co widać · Czego nie wiemy · O co spytać lekarza**. Niżej: mocne strony. Niżej: „Jedna obserwacja do zebrania na następny bieg". Pole notatki i obserwacji strukturalnych. Disclaimer.
5. **[MVP] Brief dla lekarza** — strona A4, `@media print`, „Drukuj / zapisz PDF". Na MVP z jednego biegu; **[2]** z okresu. Zawiera: profil, zakres, biegi i km, pokrycie glukozy, epizody < 70 i < 54 z datami, minutą i podstawą (`basis`), momenty z czynnikami współwystępującymi, mediana minuty pierwszego spadku (gdy okres), biegi bez danych, pytania pacjenta, obserwacje zebrane, badge syntetyczne, disclaimer. Zero interpretacji dawek.
6. **[2] Okres** — zakres 2/4/6/12 tygodni lub własny. Duża liczba pierwsza zależna od soczewki. Kropki biegów na osi, wykres minuty pierwszego spadku, rozkład czynników, unknowns.
7. **[2] Cel** — dla `race`: pytania do lekarza i braki; dla innych: obserwacje i regularność.
8. **[2] Ustawienia** — jednostki, strefa, odłącz Garmin, usuń wszystko, informacja o źródłach i AI.

Wymagania UI: każde wywołanie modelu ma **skeleton screen** w kształcie wyniku, nie spinner; tekst body ≥ 16 px; akcje destrukcyjne z potwierdzeniem nazywającym skutek; każdy punkt wywołania API ma stan błędu z „Spróbuj ponownie". Estetyka: ciemny motyw, kolory ziemi plus jeden akcent dla glukozy, duża liczba pierwsza, bez stockowych biegaczy i haseł motywacyjnych.

---

## 12. Architektura

```
Przeglądarka (Next.js 16, React 19, TS, CSS; repo hackyeah-2026; Vercel)
   │  same-origin Route Handlers (/api/*) — cienkie proxy, auth, walidacja
   ▼
Serwis "engine" (Python 3.12, FastAPI; długożyjący proces: Railway / Fly / Render)
   ├─ /parse/fit        FIT → strumienie (fit_parser + fit_adapter)         [Background IP + adapt]
   ├─ /signals          strumienie → RunSignals (run_signal_extractor)       [Background IP]
   ├─ /glucose/parse    CSV → GlucoseReading[]                               [nowe]
   ├─ /analyze/run      → GlucoseFacts + MomentContext[] + observation + narracja? [nowe]
   ├─ /analyze/period   → PeriodFacts + narracja?                            [nowe, blok 4]
   ├─ /garmin/login /mfa /sync /disconnect  (aktor MFA w pamięci)            [nowe, blok 6]
   └─ /brief            → JSON do renderu A4                                 [nowe]
   ▼
Supabase Postgres (projekt hackyeah-2026 istnieje, schemat pusty, RLS włączone)
```

- **Python osobno**, bo silnik i parser są w Pythonie z testami; port do TS to strata czasu. Garmin wymaga jednego długożyjącego procesu.
- **Nie Vercel Python functions dla engine**: aktor MFA nie przeżyje serverless.
- **Auth usera:** Supabase Auth magic link (e-mail), RLS po `user_id`. Fallback przy braku czasu: profil demo w cookie z adnotacją na slajdzie.
- **Schemat minimalny:**
  - `profiles(user_id PK, diabetes_type, therapy, glucose_source, goal, race_name, race_distance_km, race_date, max_hr, age, sex, units, tz, health_data_consent_at)`
  - `activities(id, user_id, source: fit_upload|garmin, external_id, start_utc, duration_s, distance_m, sport, device, streams JSONB, run_signals JSONB, weather JSONB null, note TEXT, observations JSONB, created_at)` — bez GPS
  - `glucose_readings(id, user_id, ts_utc, value_mgdl int null, range_flag, source, kind)` — tylko gdy `health_data_consent_at` nie jest null
  - `analyses(id, user_id, activity_id null, period_from, period_to, kind: run|period|brief, facts JSONB, contexts JSONB, narrative JSONB null, model null, created_at)`
  - `observations(id, user_id, created_from_analysis_id, target_activity_id null, kind, status: pending|collected|still_missing)`
  - `garmin_sessions(user_id PK, encrypted_session BYTEA, garmin_account_id, connected_at, last_sync_at)`
- **Sekrety:** `ENGINE_URL`, `ENGINE_SHARED_SECRET`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (tylko server), `SUPABASE_ANON_KEY`, `LLM_API_KEY`, `SESSION_ENCRYPTION_KEY`. Nic wrażliwego z prefiksem `NEXT_PUBLIC_`.
- **Przepływ FIT:** przeglądarka → Next route → engine `/parse/fit` (multipart) → strumienie JSON → zapis `activities` → `/signals` → zapis `run_signals`. Plik nigdzie nie jest zapisywany.
- **Deploy na początku pracy** (blok 1): pusty engine z `/health` na hostingu i Next na Vercelu, zanim powstanie logika. Każdy kolejny blok wypycha na działający adres.

---

## 13. Dane do demo

- **Biegi: prawdziwe pliki FIT Grega**, 3–6, w tym jeden długi z wyraźnym załamaniem tempa i jeden z podbiegiem tłumaczącym spadek tempa.
- **Glukoza: syntetyczna**, skrypt `scripts/synth_glucose.py`, oznaczona na ekranie i w repo. Wejście: czas startu i trwania z FIT-a, scenariusz, seed. Wyjście: CSV w formacie Dexcom Clarity (i Libre po MVP). Deterministyczny seed. `data/README.md` opisuje każdy plik i stwierdza, że nie pochodzi od pacjenta.
- **Cztery scenariusze, bo kontrast i sprzeczność są sercem demo:**
  - **A — niska glukoza, płasko.** Start 120–140; od 30.–40. minuty spadek 1,5–2,5 mg/dL/min; minimum 60–68 w oknie klifu wykrytego przez silnik, na płaskim odcinku; po znaczniku `Carbs` odbicie do 100–115 w 15–20 min. Oczekiwany kontekst: tylko `low_glucose_nearby`.
  - **B — podbieg, glukoza w zakresie.** Linia 110–125 z szumem ±5, bez `Carbs`. Oczekiwany kontekst: tylko `uphill`.
  - **C — sprzeczny: niska glukoza NA podbiegu.** Minimum 65 dokładnie w oknie momentu `grade_adjustment`. Oczekiwany kontekst: `low_glucose_nearby` + `uphill`, `separable = false`. To slajd o uczciwości.
  - **D — luka w danych.** Brak odczytów między 30. a 50. minutą (sensor odpięty), klif w 40. minucie. Oczekiwany kontekst: `no_glucose_data`, pokrycie < 60%, fakty czasowe na odcinkach pokrytych.
- Szum gaussowski ±4, zaokrąglenie do całości, odczyty poza 40–400 jako `Low`/`High`.
- **[2] Glukometr:** 2 punkty na dobę biegu (przed 130–160, po 95–120), brak odczytów w trakcie.
- Prawdziwy eksport CSV od biegacza z T1D (za zgodą, zanonimizowany) zastąpiłby scenariusz A i byłby argumentem na pitchu. Nie jest warunkiem.

---

## 14. Bezpieczeństwo, prawo, uczciwość

- Disclaimer (max 2 zdania) na każdym ekranie z glukozą i w briefie.
- Zero zaleceń o lekach i jedzeniu; regex serwerowy na frazy o dawkach i porcjach w tekście modelu.
- Zgoda na dane zdrowotne przed zapisem glukozy; „Usuń wszystkie dane" kasuje profil, aktywności, glukozę, analizy, obserwacje, sesję Garmina.
- Hasło Garmina tylko w pamięci procesu na czas logowania; sesja zaszyfrowana; brak w logach.
- Brak GPS i plików binarnych w bazie.
- Dane syntetyczne podpisane na ekranie, w slajdach i w `data/README.md`.
- Rejestry aktualne: `BACKGROUND_IP.md` (trzy pliki + testy, SHA, sumy kontrolne), `THIRD_PARTY.md` (Next, React, FastAPI, pydantic, garmin-fit-sdk, garminconnect z notą o szarej strefie, Supabase, Open-Meteo, dostawca LLM), `AI_USAGE.md` (asystenci per sesja + model w aplikacji), `DECISIONS.md` (timestampy ze strefą).

---

## 15. Weryfikacja (uruchomione, nie zadeklarowane)

- Testy przeniesione z UltraSoul przechodzą w nowym repo (`pytest` w `engine/`), najpierw na imporcie bajt w bajt (z pominięciem testów wymagających FastAPI), potem po adaptacji.
- Nowe testy, każdy pokazany jako FAIL na zepsutym wejściu, potem PASS: parser Dexcom (w tym `Low`/`High` jako flagi), wyrównanie czasu z luką > 15 min (brak interpolacji, `basis` zapisany), pokrycie < 60% ogranicza fakty czasowe do odcinków pokrytych, kontekst momentu dla scenariuszy A/B/C/D (C daje dwa czynniki i `separable=false`), walidator narracji (odrzuca nieistniejący `fact_id` i surową liczbę w tekście), regex zakazanych wzorców i fraz o dawkach, fallback bez modelu renderuje pełny ekran.
- `curl` na każdy endpoint engine z realnym FIT-em i CSV ze scenariuszy, output wklejony do `docs/VERIFICATION.md`.
- Ścieżka w przeglądarce na adresie produkcyjnym: onboarding → upload 2 FIT → upload CSV → bieg A pokazuje `low_glucose_nearby`, bieg B `uphill`, bieg C oba z „nie da się rozdzielić", bieg D „brak danych" → brief drukuje się do PDF. Zrzuty do slajdów.
- **[blok 6]** Garmin: login + MFA + pobranie ≥ 3 biegów na koncie Grega, zrzut postępu.
- `npm run check` i `npm run build` zielone; adres Vercela otwiera się z telefonu.

---

## 16. Plan na pozostały czas (checkpoint 20:00, oddanie przed 11:00)

| Blok | Czas | Wynik widoczny |
|---|---|---|
| 0. Wpis reveal + tag `task-reveal-2026`; commit `import(background-ip)` bajt w bajt z rejestrem; commit `adapt(background-ip)` | 0,5 h | `pytest` zielone w nowym repo |
| 1. Deploy szkieletu: engine z `/health` na hostingu, Next na Vercelu, Supabase schemat + RLS, generator glukozy ze scenariuszami A–D, dane demo w repo | 1,5 h | Adres produkcyjny działa, CSV w repo |
| 2. Pionowy plaster MVP (typ 1 + CGM): onboarding → upload FIT + CSV Dexcom → engine → ekran biegu z wykresem, czynnikami, trzema kolumnami, obserwacją → brief A4 z jednego biegu | 4 h | Scenariusze A–D online, brief drukuje się |
| **Checkpoint 20:00** | | Draft zgłoszenia z linkiem i 3 zrzutami |
| 3. Warstwa modelu (9.7) jako dodatek z fallbackiem | 1 h | Headline i narracja z `fact_ids`, ekran działa też bez modelu |
| 4. Okres: agregator + ekran + brief z okresu | 2 h | Widok 6 tygodni |
| 5. Profile typ 2 i stan przedcukrzycowy: wpisy z glukometru, „trasa nieobserwowana", soczewki celu, pytania przed zawodami | 1,5 h | Trzy profile działają |
| 6. Garmin: login, MFA, lista, pobranie, dedup, postęp, odłącz. **Twardy budżet 2 h; po przekroczeniu stop i „w budowie"** | 2 h | Biegi Grega z konta |
| 7. Polish: skeletony, stany błędów, druk, responsywność, disclaimer, badge | 1,5 h | Działa z telefonu |
| 8. Slajdy (10), opis zgłoszenia, rejestry, `docs/VERIFICATION.md`, upload na platformę | 2,5 h | Zgłoszenie wysłane przed 11:00 |

Razem ~16,5 h roboty. Kolejność cięć, jeśli brakuje czasu: pogoda (9.6) → CSV Libre → mmol/L → soczewka `race` → blok 5 w całości → Garmin po przekroczeniu budżetu. **Nigdy nie cięte:** bloki 0–2, disclaimer, badge syntetyczne, rejestry, fallback bez modelu.

---

## 17. Zgłoszenie — szkic

- **Tytuł:** Cukier w biegu (robocze).
- **Opis (akapit):** Biegacze z cukrzycą typu 1 (a docelowo także typu 2 i ze stanem przedcukrzycowym) mają dane z zegarka i z sensora glukozy, których po biegu nikt nie czyta razem. Nasze narzędzie kładzie je na jednej osi czasu, deterministycznym silnikiem wykrywa momenty, w których bieg kosztował (załamanie tempa, dryf tętna, spadek kadencji), odczytuje glukozę w oknie każdego z nich i uczciwie pokazuje, co współwystąpiło, czego dane nie rozstrzygają i o co zapytać lekarza. Generuje jednostronicowy brief do rozmowy z diabetologiem. Źródła: pliki FIT (i konto Garmin Connect), CSV z Dexcom (i Libre), wpisy z glukometru. Zero zaleceń o lekach i jedzeniu. Dane glukozy w demo są syntetyczne i tak oznaczone.
- **10 slajdów:** (1) problem: dwa wykresy, których nikt nie czyta razem; (2) dla kogo i dlaczego teraz; (3) jak to działa: fakty liczy kod, model pisze, UI pokazuje liczby z faktów; (4) bieg A: „zbiegło się z niskim odczytem"; (5) bieg B: „to był podbieg, glukoza w zakresie"; (6) bieg C: „nie da się rozdzielić" i bieg D: „brak danych", czyli uczciwość jako cecha; (7) brief dla lekarza; (8) architektura i źródła (FIT, Garmin, CSV), co jest Background IP, co powstało na hackathonie, z komendą `git log task-reveal-2026..HEAD`; (9) bezpieczeństwo i prawo: zero zaleceń, zgoda, syntetyczne dane, szara strefa Garmina i plan migracji; (10) następny krok: pilot z poradnią diabetologiczną, oficjalne API Garmina, prawdziwe dane CGM za zgodą, mobile.
- **Ujawnienia:** AI do kodowania (asystenci, bez promptów), model LLM w aplikacji (dostawca, wersja), biblioteki, Background IP z UltraSoul (trzy pliki, SHA, sumy kontrolne, data), dane syntetyczne, materiały koncepcyjne sprzed hackathonu (starter z 1–2.10, zgodnie z `BACKGROUND_IP.md`).

---

## 18. Decyzje

**Podjęte:**
- Web tylko, responsywny; mobile po hackathonie.
- MVP = typ 1 + CGM; typ 2 i stan przedcukrzycowy jako blok 5.
- Współwystępowanie zamiast przyczyny; zero zaleceń żywieniowych i lekowych; obserwacje do zebrania zamiast eksperymentów.
- Garmin przez login i hasło zostaje w planie, po MVP online, z twardym budżetem 2 h.
- Liczby na ekranie wyłącznie z faktów; model odwołuje się do `fact_ids`; fallback bez modelu.
- Import Background IP bajt w bajt, adaptacja osobnym commitem.

**Do podjęcia przez Grega przed startem:**
1. Nazwa produktu.
2. Dostawca i wersja modelu językowego (Anthropic vs OpenAI) → klucz w env.
3. Auth: Supabase magic link czy profil demo w cookie.
4. Hosting engine: Railway (znany z UltraSoul), Fly czy Render.

---

## 19. Dyscyplina Git i granica Background IP (obowiązkowe)

Jury ocenia tylko to, co powstało w czasie hackathonu. Historia Gita jest głównym śladem pochodzenia, a rejestry (`BACKGROUND_IP.md`, `AI_USAGE.md`, `THIRD_PARTY.md`) uzupełniają ją o to, czego Git nie pokaże: wcześniejsze koncepcje, prompty, materiały. Kolejność:

1. **Commit ujawnienia.** Zapisać realny czas ujawnienia zadania (ze strefą) i linki do PDF-ów w `docs/HACKATHON.md` („Actual reveal record"), zacommitować, założyć tag `task-reveal-2026` na tym commicie i wypchnąć. Nie nadpisywać istniejącego tagu. Nie backdatować.
2. **`import(background-ip):` — pliki bajt w bajt.** Trzy pliki z `szmefo/UltraSoulAI` (`run_signal_extractor.py`, `fit_parser.py`, `fit_adapter.py`) plus ich testy i fixture'y, **bez jakiejkolwiek zmiany treści**, także bez poprawek importów. W tym samym commicie wpis w `BACKGROUND_IP.md`: repo źródłowe, ścieżka źródłowa, SHA commitu źródłowego, **suma SHA-256 każdego pliku** (identyczna w źródle i w docelowym repo), data importu ze strefą, ścieżka docelowa, rola w demo.
3. **`adapt(background-ip):` — dopiero tu zmiany.** Usunięcie zależności od `fastapi.HTTPException` w `fit_parser.py`, poprawki ścieżek importów, ewentualne drobne dostosowania. Każda zmiana dopisana do kolumny „Modyfikacje" w rejestrze. Nigdy nie mieszać adaptacji importowanego pliku z nowym modułem w jednym commicie.
4. **Nowa implementacja** w osobnych, tematycznych commitach: `feat:` / `fix:` / `test:` / `docs:`.
5. **Każda nowa biblioteka** ma wpis w `THIRD_PARTY.md` w tym samym commicie, w którym trafia do `requirements.txt` / `package.json`.
6. **Każda sesja z asystentem AI** ma wiersz w `AI_USAGE.md`: narzędzie, model jeśli znany, timestamp ze strefą, co wygenerował, ścieżki/commity, kto zdecydował, jak zweryfikowano.
7. **Przed każdym commitem** `git status` i `git diff --cached --stat`; stage tylko plików bieżącego zadania. Zero `git add -A`.
8. **Na koniec** sekcja „Built during HackYeah" w README: `git log --reverse --oneline task-reveal-2026..HEAD`, `git diff --stat task-reveal-2026..HEAD`, i jedno zdanie: które commity to import, które adaptacja, które nowa praca, plus odesłanie do rejestrów.
