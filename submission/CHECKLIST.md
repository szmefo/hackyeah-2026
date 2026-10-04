# Poranna checklista Grega — 4 października

Przygotował Claude Code (Anthropic) 2026-10-04 ok. 02:25 (Europe/Warsaw). W nocy
pracowałem tylko lokalnie (opcja B): nic nie zostało wdrożone, wypchnięte ani
scalone, a produkcyjne AI nie było wywoływane. Wszystko poniżej wymaga Twojej
decyzji. Polecenia są dla **PowerShell** na tym komputerze.

Stan na noc:
- gałąź lokalna `overnight/phase-3` w worktree `C:\hackyeah-2026-p3`, oparta na
  `origin/main` = `3e62471`;
- produkcja nadal działa na starym UI: https://cukier-w-biegu.vercel.app, gdzie
  `/scenarios/...` i `/icon.svg` zwracają 404 (sprawdzone GET-em o 02:15);
- co zmieniono w nocy i jak to sprawdzono: `docs/PHASE_3_REVIEW.md`.

## Proponowany plan czasu

| Do godziny | Krok |
| --- | --- |
| 08:30 | 1–2: przegląd i decyzja, potem deploy silnika i webu |
| 09:15 | 3: kontrole produkcji, w tym Claude na 4 scenariuszach |
| 09:45 | 4–5: zapis wdrożenia, merge do `main` i push |
| 10:15 | 6: wklejenie pól, PDF i wysłanie zgłoszenia |
| **10:30** | **Zgłoszenie wysłane** (bufor do 11:00) |

---

## 0. Termin i platforma — rozstrzygnij na początku

- **Rozbieżność:** agenda HackYeah podaje termin oddania **4.10, godz. 11:00**
  (`docs/HACKATHON.md`). Regulamin zadania (pkt 5, `Rules - SPORT & HEALTHCARE.pdf`)
  mówi „no later than **11:00PM on October 4th**”. Ten sam punkt podaje start „no
  earlier than 11:00 PM on October 3rd”, a to na pewno błąd, bo zadanie ogłoszono
  o 11:00 rano. Zapis „PM” jest więc najpewniej pomyłką.
- **Decyzja:** traktuj **11:00 jako twardy termin** i wyślij do 10:30. Finaliści są
  ogłaszani o 15:00, więc 23:00 nie ma sensu. Jeśli chcesz potwierdzenia, zapytaj
  organizatorów na Discordzie HackYeah albo w punkcie informacyjnym i sprawdź termin
  pokazany na platformie przy zadaniu. Nie planuj niczego po 11:00.
- **Platforma:** regulamin wskazuje **HackTribe**, a opis zadania (Details, s. 4) mówi
  o „Challenge Rocket”. Szkic zgłoszenia już jest na HackTribe, więc użyj HackTribe.
  Jeśli organizatorzy wskażą inaczej, zrób, jak powiedzą.
- **Regulamin pkt 13:** zmiany po terminie nie są brane pod uwagę. Deploy, merge
  i push zrób **przed** wysłaniem zgłoszenia. Po 11:00 nie wdrażaj i nie pushuj
  niczego aż do wyników (17:45).
- **Nazwa zespołu:** nie ma jej w repo ani w szkicu. Ustal ją i wpisz identycznie
  jak na HackTribe. Propozycja w `SUBMISSION.md`: „Cukier w biegu”. Zmień też
  komentarz `TO CONFIRM` w tym pliku albo po prostu wklej właściwą nazwę.

## 1. Przegląd i decyzja (10 min)

```powershell
cd C:\hackyeah-2026-p3
git status --short
git log --oneline origin/main..overnight/phase-3
```

Przeczytaj `docs/PHASE_3_REVIEW.md` (sekcje „What changed” i „Review findings”).
Opcjonalnie powtórz testy lokalne (ok. 2 min):

```powershell
cd C:\hackyeah-2026-p3
npm run check
node --experimental-strip-types --test scripts/test_ai.mjs scripts/test_transport.mjs   # 29 pass
cd engine; C:\hackyeah-2026\engine\.venv\Scripts\python.exe -m pytest tests -q; cd ..    # 103 passed
```

`git status` może pokazać nieśledzone pliki innych agentów, np. `submission/screenshots/`.
Deployowi to nie przeszkadza, bo `git archive` bierze tylko zatwierdzone pliki z `HEAD`.

## 2. Deploy — najpierw silnik, potem web (przepływ artefaktów z `docs/CLOUD.md`)

Sprawdź konto: `vercel whoami` powinno pokazać konto właściciela workspace `hack-yeah1`.
Zmienne środowiskowe są już ustawione w obu projektach, więc **nie zmieniaj env**.
Przygotowanie artefaktów przetestowałem w nocy na sucho, w katalogu tymczasowym,
bez deployu.

### 2a. Silnik (`cukier-w-biegu-engine`)

```powershell
$repo = "C:\hackyeah-2026-p3"
$sha  = (git -C $repo rev-parse --short HEAD).Trim()
$eng  = "C:\_HackYeah2026\deploy\phase3-engine-$sha"
New-Item -ItemType Directory -Force $eng | Out-Null
git -C $repo archive -o "$eng.tar" HEAD engine/main.py engine/requirements.txt engine/vercel.json engine/.python-version engine/.vercelignore engine/app
tar -xf "$eng.tar" -C $eng --strip-components=1
Copy-Item -Recurse "C:\_HackYeah2026\deploy\phase2-engine\.vercel" "$eng\.vercel"
Get-Content "$eng\.vercel\project.json"    # oczekiwane "projectName":"cukier-w-biegu-engine"
Set-Location $eng
vercel deploy --prod --scope hack-yeah1
```

Zanotuj URL i ID wdrożenia z wyjścia, a potem:

```powershell
curl.exe -s https://cukier-w-biegu-engine.vercel.app/health
# {"status":"ok","service":"cukier-w-biegu-engine","storage":"none"}
```

### 2b. Web (`cukier-w-biegu`)

```powershell
$web = "C:\_HackYeah2026\deploy\phase3-web-$sha"
New-Item -ItemType Directory -Force $web | Out-Null
git -C $repo archive -o "$web.tar" HEAD src data public package.json package-lock.json next.config.ts tsconfig.json .gitignore .vercelignore
tar -xf "$web.tar" -C $web
Copy-Item -Recurse "C:\_HackYeah2026\deploy\cream-lavender-a86ea60\.vercel" "$web\.vercel"
Get-Content "$web\.vercel\project.json"    # oczekiwane "projectName":"cukier-w-biegu"
Set-Location $web
vercel deploy --prod --scope hack-yeah1
```

Archiwum zachowuje pliki demo bajt w bajt. Sprawdziłem SHA-256 pliku CSV i FIT ze
scenariusza 03: są identyczne z repo. Ma to znaczenie, bo oznaczenie „Dane
syntetyczne” zależy od porównania bajtów.

### 2c. Wycofanie, jeśli coś pójdzie źle

Poprzednie produkcyjne wdrożenia: web `dpl_7Jxhr3PrMdAGTbCAN3Sc1sfsm2Xr`
(https://cukier-w-biegu-ec4av15y9-hack-yeah1.vercel.app), silnik
`dpl_5vHuojkv9sFRdUqGXX6Zx779jUTQ`.

```powershell
Set-Location $web; vercel rollback https://cukier-w-biegu-ec4av15y9-hack-yeah1.vercel.app --scope hack-yeah1
Set-Location $eng; vercel rollback dpl_5vHuojkv9sFRdUqGXX6Zx779jUTQ --scope hack-yeah1
```

Wycofaj **oba** projekty razem. Po rollbacku zgłoszenie musi opisywać stary stan:
patrz uwaga na górze `SUBMISSION.md`, czyli krok 2 instrukcji i brak kart scenariuszy.

## 3. Kontrole produkcji (ok. 25 min)

### 3a. Automatyczne (bez wywołania modelu)

```powershell
curl.exe -s https://cukier-w-biegu.vercel.app/api/ai-status
# {"configured":true,"provider":"Anthropic"}
curl.exe -s -o NUL -w "%{http_code}`n" https://cukier-w-biegu.vercel.app/scenarios/03-podbieg-i-niski-cukier/glukoza.csv   # 200 (w nocy 404)
curl.exe -s -o NUL -w "%{http_code}`n" https://cukier-w-biegu.vercel.app/icon.svg                                         # 200
cd C:\hackyeah-2026-p3
$env:QA_BASE_URL = "https://cukier-w-biegu.vercel.app"
node --test scripts/test_routes.mjs      # oczekiwane: 13 pass, 0 fail
Remove-Item Env:QA_BASE_URL
```

Testy tras używają tylko danych syntetycznych. Przy skonfigurowanym AI wysyłają
jedynie żądanie **bez zgody**, na które serwer odpowiada 400. Nie wydają więc
pieniędzy na model i nie zużywają limitu.

### 3b. Przeglądarka — 4 scenariusze

Chrome: https://cukier-w-biegu.vercel.app/sources. Na każdej karcie kliknij
**Wczytaj scenariusz**, zaznacz zgodę i kliknij **Połącz pliki i zobacz bieg**.
Oczekiwany wynik (sprawdzony lokalnie w nocy):

| Scenariusz | Moment | Do sprawdzenia |
| --- | --- | --- |
| 1 Niski cukier na płaskim | „Odczyt do omówienia · 50. min · 9,0 km” | jest sekcja „Co poszło dobrze” (równe tempo); teren na wykresie płaski |
| 2 Podbieg, glukoza w zakresie | „Podbieg, glukoza w zakresie · 84. min · 15,0 km” | najniższa glukoza w oknie 119 mg/dL; **brak** sekcji „Co poszło dobrze”. Ta etykieta pochodzi z nowego silnika, więc potwierdza deploy silnika |
| 3 Podbieg i niski cukier naraz | „Dwa sygnały · 85. min · 15,1 km” | 62 mg/dL; „Dane nie pozwalają rozdzielić wpływu współwystępujących czynników.” |
| 4 Luka w danych sensora | „Luka w danych · 84. min · 15,0 km” | „W całym biegu brakuje glukozy między 55. a 94. minutą.” |

Na każdym ekranie powinna być plakietka **DANE SYNTETYCZNE** na wykresie glukozy
i tytuł scenariusza.

### 3c. Claude na 4 scenariuszach

Limit wynosi **2 analizy na minutę i 8 na godzinę** z jednego adresu sieciowego
(liczony w pamięci jednej instancji serwera). Rób **jedną analizę, potem odczekaj
co najmniej 35 s**. Cztery analizy zużyją połowę godzinnego limitu, więc zrób je
rano, a nie tuż przed pitchem.

Dla każdego scenariusza: po imporcie zaznacz zgodę Anthropic w sekcji **Spójrzmy na
ten moment razem** i kliknij **Przeanalizuj ten moment z AI**. Odpowiedź może
przyjść nawet po ok. 55 s. Sprawdź:

- [ ] plakietka „Interpretacja AI · Anthropic”, pod każdym zdaniem „Podstawa: …”,
      a na dole linia „Model: …”;
- [ ] brak dawek insuliny, zaleceń jedzenia i diagnozy, brak „spowodował/przez cukier”;
- [ ] sc. 2: AI nie przypisuje zwolnienia glukozie (wszystkie odczyty 70–180);
- [ ] sc. 3: AI wymienia oba sygnały i nie wybiera jednej przyczyny;
- [ ] sc. 4: AI nie podaje żadnej wartości glukozy w oknie luki;
- [ ] sc. 1: AI mówi o niskim odczycie i braku podbiegu bez twierdzenia o przyczynie.

Jeśli pojawi się komunikat zakończony „Fakty i pytania z danych pozostają
dostępne.”, zapisz jego treść i spróbuj raz po 60 s. Jeśli błąd się powtórzy, aplikacja
działa zgodnie z projektem (deterministyczna ścieżka), ale zanotuj to do zapisu
wdrożenia. Taki wynik nie blokuje zgłoszenia.

### 3d. Brief i druk

- [ ] Po sc. 3 z jedną obserwacją otwórz **Brief dla lekarza**, kliknij **Drukuj / zapisz PDF**
      i w podglądzie Chrome (Zapisz jako PDF) sprawdź, czy jest **1 strona**.
      Natywnego okna druku nie sprawdzaliśmy w nocy.
- [ ] Zrób to samo z briefem zawierającym sekcję AI („05 / Interpretacja AI…”).
      Tego wariantu nie dało się zmierzyć lokalnie i może wyjść na 2 strony.
      To znany limit, nie blocker.
- [ ] Telefon (albo DevTools, 390 px): brak poziomego przewijania na ekranie biegu.

## 4. Zapis wdrożenia (przed merge)

Poproś agenta (Claude Code albo Codex) w `C:\hackyeah-2026-p3` o:

- `docs/phase-3-deployment.json`: commit źródłowy `$sha`, ID i URL obu wdrożeń,
  ścieżki artefaktów i SHA-256 plików (jak w `phase-2-deployment.json`);
- dopisanie wyników kroku 3 do `docs/PHASE_3_REVIEW.md` i `docs/CLOUD.md`,
  z prawdziwymi znacznikami czasu;
- aktualizację sekcji „Deployment” i „Verification” w `README.md`, bo dziś mówią
  o `a86ea60`;
- osobny commit `docs:` na `overnight/phase-3`.

## 5. Merge do `main` i push

`main` jest wybrany w `C:\hackyeah-2026`, z którego mógł korzystać Codex. Najbezpieczniej
zrobić fast-forward z worktree p3:

```powershell
cd C:\hackyeah-2026-p3
git status --short
git fetch origin
git rev-parse --short origin/main                                 # oczekiwane 3e62471
git merge-base --is-ancestor origin/main overnight/phase-3; $?    # True = fast-forward możliwy
git push origin overnight/phase-3:main
git push origin overnight/phase-3                                 # opcjonalnie: gałąź jako ślad
git ls-remote origin main                                         # SHA = git rev-parse HEAD
```

- Jeśli push zostanie **odrzucony** (ktoś zmienił `origin/main`), **nie używaj force**.
  Zrób `git merge origin/main` na `overnight/phase-3`, rozwiąż konflikty, powtórz
  `npm run check` i testy, a potem pushuj ponownie.
- Lokalny `main` w `C:\hackyeah-2026` zaktualizuj dopiero wtedy, gdy Codex tam nie pracuje:
  `git -C C:\hackyeah-2026 status --short`, a potem
  `git -C C:\hackyeah-2026 merge --ff-only origin/main`.
- Sprawdź https://github.com/szmefo/hackyeah-2026: README i `submission/SUBMISSION.md`
  są widoczne bez logowania.

## 6. HackTribe — wklejenie i wysłanie

Pola są w `submission/SUBMISSION.md`, gotowe do wklejenia po angielsku.

- [ ] **Project title:** Glucose on the Run (Cukier w biegu)
- [ ] **Team name:** ustalona w kroku 0
- [ ] **Team members:** Grzegorz Walencik
- [ ] **Project description:** sekcje PROBLEM / SOLUTION / PROGRESS / SKILLS /
      REPOSITORY / INSTRUCTIONS / AI & EXTERNAL RESOURCES. Nadpisz nimi szkic,
      który był pisany w czasie przyszłym.
- [ ] **PDF prezentacji, maks. 10 slajdów:** plik z osobnego zadania, w nocy pojawił
      się jako `submission/Glucose-on-the-Run.pdf` (źródła w `submission/slides/`).
      Przed wysłaniem
      otwórz go i policz strony (≤10). Sprawdź też, że nie twierdzi niczego, czego
      nie ma w `SUBMISSION.md`, np. walidacji klinicznej.
- [ ] **Demo link:** https://cukier-w-biegu.vercel.app/ (tylko po udanym kroku 2–3)
- [ ] **Repo:** https://github.com/szmefo/hackyeah-2026 (po kroku 5)
- [ ] **Zrzuty (opcjonalnie):** 3–5 plików z `submission/screenshots/`, np. sc. 2,
      sc. 3 i brief
- [ ] Kliknij wyślij/zapisz i zrób zrzut ekranu potwierdzenia z godziną.

## 7. Po wysłaniu

- Niczego nie wdrażaj ani nie pushuj do wyników (pkt 13 regulaminu).
- 15:00 ogłoszenie finalistów, 16:00 pitching. Scenariusz pitchu jest w
  `submission/DEMO_SCRIPT.md`. Przygotuj kartę z wynikiem AI ok. 15 min przed
  wyjściem i nie klikaj AI na próbę na wspólnym Wi-Fi.
