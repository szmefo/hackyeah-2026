"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell, DataBadge, SyntheticBadge } from "@/components/app-shell";
import { Icon } from "@/components/icons";
import { useDemo } from "@/components/demo-context";
import type { RunStory } from "@/lib/run-story";
import { builtInPair, demoScenarios, type SyntheticPair } from "@/lib/demo";
import "../scenarios.css";
export default function Sources() {
  const router = useRouter();
  const { currentRun, loadRun, resetRun, revision } = useDemo();
  const [fit, setFit] = useState<File | null>(null);
  const [glucose, setGlucose] = useState<File | null>(null);
  const [timezone, setTimezone] = useState("Europe/Warsaw");
  const [consent, setConsent] = useState(false);
  // A demo pair chosen with one click; the server re-checks its bytes.
  const [chosenPair, setChosenPair] = useState<SyntheticPair | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inflight = useRef<AbortController | null>(null);
  const form = useRef<HTMLFormElement>(null);
  const consentBox = useRef<HTMLInputElement>(null);
  // After a one-click pair load, move focus to the next required step.
  const focusConsent = useRef(false);
  useEffect(() => () => inflight.current?.abort(), [revision]);
  useEffect(() => {
    if (loading || !focusConsent.current) return;
    focusConsent.current = false;
    consentBox.current?.scrollIntoView({ block: "center" });
    consentBox.current?.focus({ preventScroll: true });
  }, [loading]);
  function cancel() {
    inflight.current?.abort();
    inflight.current = null;
    setLoading(false);
  }
  async function loadPair(pair: SyntheticPair) {
    cancel();
    const controller = new AbortController();
    inflight.current = controller;
    setLoading(true);
    setError("");
    try {
      const responses = await Promise.all([
        fetch(`/${pair.fit}`, { signal: controller.signal }),
        fetch(`/${pair.csv}`, { signal: controller.signal }),
      ]);
      if (responses.some((r) => !r.ok))
        throw new Error("Nie udało się pobrać przykładowych plików.");
      const [fitData, csvData] = await Promise.all(
        responses.map((r) => r.blob()),
      );
      if (controller.signal.aborted) return;
      form.current?.reset();
      setFit(new File([fitData], pair.fit.split("/").pop()!));
      setGlucose(new File([csvData], pair.csv.split("/").pop()!));
      setChosenPair(pair);
      setTimezone("Europe/Warsaw");
      focusConsent.current = true;
    } catch (e) {
      if (!controller.signal.aborted)
        setError(
          e instanceof Error ? e.message : "Nie udało się pobrać plików.",
        );
    } finally {
      if (inflight.current === controller) {
        inflight.current = null;
        setLoading(false);
      }
    }
  }
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!fit || !glucose || !consent || loading) return;
    setError("");
    if (fit.size > 2 * 1024 * 1024 || glucose.size > 2 * 1024 * 1024) {
      setError(
        "Każdy plik może mieć maksymalnie 2 MB. Wybierz pojedynczy bieg i krótszy eksport CSV.",
      );
      return;
    }
    const controller = new AbortController();
    inflight.current = controller;
    setLoading(true);
    const body = new FormData();
    body.set("fit", fit);
    body.set("glucose", glucose);
    body.set("timezone", timezone);
    body.set("consent", "true");
    body.set("synthetic", chosenPair ? "true" : "false");
    try {
      const response = await fetch("/api/import", {
        method: "POST",
        body,
        signal: controller.signal,
      });
      const result = await response.json();
      if (controller.signal.aborted) return;
      if (!response.ok)
        throw new Error(
          result.error ??
            "Nie udało się połączyć plików. Sprawdź ich format i spróbuj ponownie.",
        );
      const run = result.run as RunStory;
      if (!run?.moments?.length || !Number.isFinite(run.durationMinutes))
        throw new Error("W odpowiedzi brakuje danych biegu.");
      loadRun(run);
      router.push("/");
    } catch (e) {
      if (!controller.signal.aborted)
        setError(
          e instanceof Error
            ? e.message
            : "Połączenie przerwane. Spróbuj ponownie.",
        );
    } finally {
      if (inflight.current === controller) {
        inflight.current = null;
        setLoading(false);
      }
    }
  }
  function clearData() {
    cancel();
    resetRun();
    setFit(null);
    setGlucose(null);
    setConsent(false);
    setChosenPair(null);
    setError("");
    form.current?.reset();
  }
  return (
    <AppShell active="sources">
      <div className="listing-intro">
        <span className="eyebrow">Skąd jest ta historia</span>
        <h1>
          Dwa źródła.
          <br />
          Jedna oś czasu.
        </h1>
        <p>
          Dodaj jeden bieg z zegarka i eksport odczytów glukozy. Pokażemy ich
          wspólny przebieg, wraz z brakami danych.
        </p>
      </div>
      <section className="demo-scenarios" aria-labelledby="scenarios-title">
        <div className="demo-scenarios-head">
          <span className="eyebrow">Wypróbuj jednym kliknięciem</span>
          <h2 id="scenarios-title">Scenariusze demo</h2>
          <p>
            Cztery pary plików FIT i CSV wygenerowane skryptem. Żadna nie
            pochodzi od pacjenta. Kliknięcie wczytuje parę do formularza
            poniżej. Potem zaznacz zgodę i połącz pliki.
          </p>
          <SyntheticBadge />
        </div>
        <ul className="scenario-grid">
          {demoScenarios.map((pair) => {
            const active = chosenPair?.id === pair.id;
            return (
              <li
                key={pair.id}
                className={`scenario-card${active ? " is-active" : ""}`}
              >
                <span className="eyebrow">Scenariusz {pair.number}</span>
                <h3>{pair.name}</h3>
                <p>{pair.hint}</p>
                <button
                  type="button"
                  className="button secondary"
                  onClick={() => loadPair(pair)}
                  disabled={loading}
                  aria-pressed={active}
                  aria-label={`Wczytaj scenariusz ${pair.number}: ${pair.name}`}
                >
                  {active ? "Wczytany" : "Wczytaj scenariusz"}
                  <Icon name={active ? "check" : "arrow"} />
                </button>
                <div className="scenario-downloads">
                  <a
                    className="text-link"
                    href={`/${pair.fit}`}
                    download={`${pair.id}-bieg.fit`}
                    aria-label={`Pobierz plik FIT, scenariusz ${pair.number}`}
                  >
                    Pobierz FIT
                  </a>
                  <a
                    className="text-link"
                    href={`/${pair.csv}`}
                    download={`${pair.id}-glukoza.csv`}
                    aria-label={`Pobierz plik CSV, scenariusz ${pair.number}`}
                  >
                    Pobierz CSV
                  </a>
                </div>
              </li>
            );
          })}
        </ul>
      </section>
      <form ref={form} className="upload-form" onSubmit={submit}>
        <div className="sources-grid">
          <article className="source-card">
            <Icon name="clock" size={32} />
            <h2>Dane biegu</h2>
            <p>
              Plik FIT z jednego biegu: tempo, tętno i wysokość, jeśli zegarek
              je zapisał.
            </p>
            <label className="file-label">
              Wybierz plik FIT
              <input
                type="file"
                accept=".fit"
                disabled={loading}
                onChange={(e) => {
                  setFit(e.target.files?.[0] ?? null);
                  setChosenPair(null);
                  setError("");
                }}
              />
            </label>
            <span className="chosen-file">
              {fit ? fit.name : "Nie wybrano pliku"}
            </span>
            <small>Maksymalnie 2 MB. GPS nie trafi do wyniku.</small>
          </article>
          <article className="source-card">
            <Icon name="drop" size={32} />
            <h2>Odczyty glukozy</h2>
            <p>
              CSV z Dexcom Clarity obejmujący czas tego samego biegu. Nie
              uzupełniamy luk w odczytach.
            </p>
            <label className="file-label">
              Wybierz CSV
              <input
                type="file"
                accept=".csv,text/csv"
                disabled={loading}
                onChange={(e) => {
                  setGlucose(e.target.files?.[0] ?? null);
                  setChosenPair(null);
                  setError("");
                }}
              />
            </label>
            <span className="chosen-file">
              {glucose ? glucose.name : "Nie wybrano pliku"}
            </span>
            <small>Maksymalnie 2 MB. Używamy odczytów EGV.</small>
          </article>
        </div>
        <div className="upload-settings">
          <label>
            Strefa czasowa eksportu CSV
            <select
              value={timezone}
              disabled={loading}
              onChange={(e) => setTimezone(e.target.value)}
            >
              <option value="Europe/Warsaw">Polska — Europe/Warsaw</option>
              <option value="UTC">UTC</option>
              <option value="Europe/London">
                Wielka Brytania — Europe/London
              </option>
              <option value="Europe/Berlin">Niemcy — Europe/Berlin</option>
              <option value="America/New_York">USA — America/New_York</option>
            </select>
          </label>
          <p>
            Wybierz strefę, w której zapisano godziny w CSV. Czas z zegarka
            dopasujemy do niej.
          </p>
        </div>
        <p className="chosen-pair" role="status">
          {chosenPair ? (
            <>
              <SyntheticBadge />
              <span>
                Wczytano:{" "}
                <strong>
                  {chosenPair.number
                    ? chosenPair.runTitle
                    : "przykładową parę plików"}
                </strong>
                . Zaznacz zgodę i połącz pliki.
              </span>
            </>
          ) : (
            <span>
              Własne pliki zostaną oznaczone jako wgrane dane. Niezmienione
              pliki demo z tej strony oznaczymy jako dane syntetyczne.
            </span>
          )}
        </p>
        <label className="consent-label">
          <input
            ref={consentBox}
            type="checkbox"
            checked={consent}
            disabled={loading}
            onChange={(e) => setConsent(e.target.checked)}
          />
          <span>
            Zgadzam się na przesłanie plików do serwera aplikacji w celu
            jednorazowego połączenia i analizy danych zdrowotnych. Wynik
            pozostanie w pamięci tej karty. Pliki i wynik nie są zapisywane w
            bazie.
          </span>
        </label>
        <p className="privacy-note">
          Przetwarzanie odbywa się na serwerze aplikacji w Vercel. Odświeżenie
          strony usuwa wgrany wynik i obserwacje. Analiza AI wymaga osobnej
          zgody — ten import nie wysyła danych do dostawcy AI.
        </p>
        <div className="upload-actions">
          <button
            className="button primary"
            type="submit"
            disabled={!fit || !glucose || !consent || loading}
          >
            {loading ? "Łączę dane…" : "Połącz pliki i zobacz bieg"}
            <Icon name="arrow" />
          </button>
          {loading && (
            <button type="button" className="button secondary" onClick={cancel}>
              Anuluj
            </button>
          )}
        </div>
        {error && (
          <p className="upload-message error-message" role="alert">
            {error}
          </p>
        )}
      </form>
      <section className="sample-files">
        <div>
          <span className="eyebrow">Najpierw możesz spróbować</span>
          <h2>Gotowa para przykładowych plików.</h2>
          <p>
            Całkowicie syntetyczny bieg i glukoza, dopasowane czasowo. Użyjesz
            tej samej ścieżki importu co dla własnych plików.
          </p>
        </div>
        <div className="sample-actions">
          <button
            className="button secondary"
            type="button"
            onClick={() => loadPair(builtInPair)}
            disabled={loading}
          >
            Wybierz przykładową parę
            <Icon name="arrow" />
          </button>
          <a className="text-link" href={`/${builtInPair.fit}`} download>
            Pobierz FIT
          </a>
          <a className="text-link" href={`/${builtInPair.csv}`} download>
            Pobierz CSV
          </a>
        </div>
      </section>
      <section className="current-data">
        <DataBadge synthetic={currentRun.synthetic} />
        <p>
          Obecnie: <strong>{currentRun.title}</strong>.{" "}
          {currentRun.provenance.engineUsed
            ? "Wynik przetworzenia plików."
            : "Gotowy przykład demonstracyjny."}
        </p>
        <div>
          <Link className="text-link" href="/">
            Otwórz bieżący bieg
            <Icon name="arrow" />
          </Link>
          <button className="text-link" onClick={clearData}>
            Usuń wgrane dane i wróć do demo
          </button>
        </div>
      </section>
    </AppShell>
  );
}
