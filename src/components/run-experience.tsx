"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { AppShell, BriefLink, DataBadge } from "./app-shell";
import { AIAnalysis } from "./ai-analysis";
import { Icon } from "./icons";
import { useDemo } from "./demo-context";
import { Timeline } from "./timeline";
import {
  decimal,
  momentUnknowns,
  durationLabel,
  dateLabel,
  minuteLabel,
} from "@/lib/demo";

function ObservationDialog({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const { addObservation, selectedId, currentRun: demo } = useDemo();
  const [text, setText] = useState("");
  const [minute, setMinute] = useState(
    () => demo.moments.find((m) => m.id === selectedId)?.minute ?? 0,
  );
  const [kind, setKind] = useState("Odczucia");
  useEffect(() => {
    dialog.current?.showModal();
  }, []);
  function submit(event: FormEvent) {
    event.preventDefault();
    if (!text.trim() || minute < 0 || minute > demo.durationMinutes) return;
    addObservation({ text: text.trim(), minute, kind });
    onClose();
  }
  return (
    <dialog
      ref={dialog}
      className="observation-dialog"
      onCancel={onClose}
      aria-labelledby="observation-title"
    >
      <button
        className="icon-button dialog-close"
        onClick={onClose}
        aria-label="Zamknij obserwację"
      >
        <Icon name="close" />
      </button>
      <span className="eyebrow">Dopisz swój kontekst</span>
      <h2 id="observation-title">
        Co pamiętasz
        <br />z tego momentu?
      </h2>
      <p>
        Obserwacja uzupełni brief z tego biegu. Pozostaje tylko w pamięci tej
        karty i znika po odświeżeniu strony.
      </p>
      <form onSubmit={submit}>
        <div className="form-row">
          <label>
            Rodzaj obserwacji
            <select value={kind} onChange={(e) => setKind(e.target.value)}>
              <option>Odczucia</option>
              <option>Postój</option>
              <option>Posiłek</option>
              <option>Warunki na trasie</option>
            </select>
          </label>
          <label>
            Minuta biegu
            <input
              type="number"
              step="0.1"
              min={0}
              max={demo.durationMinutes}
              required
              value={minute}
              onChange={(e) => setMinute(Number(e.target.value))}
            />
          </label>
        </div>
        <label>
          Twoja obserwacja
          <textarea
            autoFocus
            maxLength={500}
            rows={4}
            placeholder="Np. zatrzymałem się na chwilę przy podbiegu."
            value={text}
            onChange={(e) => setText(e.target.value)}
            required
          />
        </label>
        <div className="dialog-actions">
          <button type="button" className="button secondary" onClick={onClose}>
            Anuluj
          </button>
          <button
            className="button primary"
            disabled={!text.trim()}
            type="submit"
          >
            Dodaj do briefu
            <Icon name="check" />
          </button>
        </div>
      </form>
    </dialog>
  );
}

export function RunExperience() {
  const {
    selectedId,
    setSelectedId,
    observations,
    currentRun: demo,
    revision,
  } = useDemo();
  const [showObservation, setShowObservation] = useState(false);
  const selected =
    demo.moments.find((m) => m.id === selectedId) ?? demo.moments[0];
  return (
    <AppShell>
      <div className="run-topbar">
        <Link href="/runs" className="back-link">
          <Icon name="back" size={16} />
          Wróć do biegów
        </Link>
        <span>
          {dateLabel(demo)} <span className="topbar-separator">/</span>{" "}
          {demo.synthetic
            ? "Analiza przykładowego biegu"
            : "Analiza wgranego biegu"}
        </span>
      </div>
      <div className="run-layout">
        <section className="story-panel" aria-labelledby="story-title">
          <div className="run-identity">
            <p className="eyebrow">Twój bieg, opowiedziany razem</p>
            <h2>{demo.title}</h2>
            <div className="run-stats">
              <span>
                <Icon name="location" size={17} />
                {demo.distanceKm === null
                  ? "Dystans nieznany"
                  : `${decimal(demo.distanceKm)} km`}
              </span>
              <span>
                <Icon name="clock" size={17} />
                {durationLabel(demo.durationMinutes)}
              </span>
            </div>
          </div>
          <div className="selected-distance">
            <span className="eyebrow">Wybrany moment</span>
            <p>
              {decimal(selected.distanceKm)}
              <span>
                {selected.distanceKm === null ? "brak dystansu" : "km"}
              </span>
            </p>
            <small>
              {minuteLabel(selected.minute)}. minuta <span>·</span> Okno ±10 min
            </small>
          </div>
          <h1 id="story-title" aria-live="polite">
            {selected.title}
          </h1>
          <div className="factor-list">
            {selected.factors.length ? (
              selected.factors.map((f) => (
                <span key={f.id}>
                  <Icon
                    name={
                      f.id === "uphill"
                        ? "hill"
                        : f.id === "no_glucose_data"
                          ? "question"
                          : "drop"
                    }
                    size={25}
                  />
                  {f.label}
                </span>
              ))
            ) : (
              <span>
                <Icon name="check" size={25} />
                Dostępny kontekst
              </span>
            )}
          </div>
          <p className="story-context" aria-live="polite">
            {selected.narrative}
          </p>
          <div className="story-actions">
            <BriefLink />
            <button
              className="button secondary"
              onClick={() => setShowObservation(true)}
            >
              <Icon name="pen" />
              Dodaj obserwację
            </button>
          </div>
          <p className="story-footnote">
            Współwystępowanie pokazuje kontekst.
            <br />
            Same dane nie rozstrzygają przyczyny.
          </p>
        </section>
        <Timeline selected={selected} onSelect={setSelectedId} />
      </div>
      <section
        className="insights-grid"
        aria-label="Co wynika z wybranego momentu"
      >
        <article className="insight-card">
          <h2>
            <Icon name="eye" size={25} />
            Co widać
          </h2>
          <span className="eyebrow">Fakty z wybranego okna</span>
          {selected.factors.length ? (
            <ul>
              {selected.factors.map((f) => (
                <li key={f.id}>{f.evidence}</li>
              ))}
              <li>
                Pomiarów z zegarka i sensora szukamy w tym samym oknie czasu.
              </li>
            </ul>
          ) : (
            <ul>
              <li>Odczyty glukozy w oknie: {selected.readingCount}.</li>
              <li>
                {selected.minGlucose === null
                  ? "Brak liczbowego odczytu glukozy w oknie."
                  : `Najniższy odczyt w oknie: ${selected.minGlucose} mg/dL.`}
              </li>
            </ul>
          )}
        </article>
        <article className="insight-card">
          <h2>
            <Icon name="question" size={25} />
            Czego nie wiemy
          </h2>
          <span className="eyebrow">Granice tych danych</span>
          <ul>
            {momentUnknowns(selected, observations).map((u) => (
              <li key={u}>{u}</li>
            ))}
            {demo.gaps.map((gap) => (
              <li key={`${gap.start}-${gap.end}`}>
                W całym biegu brakuje glukozy między {minuteLabel(gap.start)}. a{" "}
                {minuteLabel(gap.end)}. minutą.
              </li>
            ))}
          </ul>
        </article>
        <article className="insight-card question-card">
          <h2>
            <Icon name="chat" size={25} />O co spytać lekarza
          </h2>
          <span className="eyebrow">Początek dobrej rozmowy</span>
          <p className="doctor-question">„{selected.question}”</p>
          <Link href="/brief" className="text-link">
            Zabierz pytania na wizytę
            <Icon name="arrow" size={17} />
          </Link>
        </article>
      </section>
      {demo.warnings?.length ? (
        <div className="run-warnings" role="status">
          <strong>Ważne dla interpretacji</strong>
          <ul>
            {demo.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <AIAnalysis key={revision} />
      <section className="next-step-section">
        <div className="next-observation">
          <span className="eyebrow">Jedna rzecz do zapisania</span>
          <h2>
            Twój kontekst
            <br />
            domyka historię.
          </h2>
          <p>
            Przy kolejnym biegu zanotuj, co czułeś i kiedy. Tego zegarek ani
            sensor nie zapiszą za Ciebie.
          </p>
          <button
            className="text-link"
            onClick={() => setShowObservation(true)}
          >
            Dodaj obserwację do biegu
            <Icon name="pen" size={17} />
          </button>
          {observations.length > 0 && (
            <div className="saved-observations" role="status">
              {observations.map((o, i) => (
                <p key={i}>
                  <Icon name="check" size={16} />
                  <span>
                    <strong>
                      {minuteLabel(o.minute)}. minuta · {o.kind}
                    </strong>
                    {o.text}
                  </span>
                </p>
              ))}
            </div>
          )}
        </div>
        <Link
          href="/brief"
          className="brief-preview"
          aria-label="Otwórz brief dla lekarza"
        >
          <div>
            <span className="eyebrow">Z biegu na wizytę</span>
            <h2>
              Jedna strona.
              <br />
              Lepsza rozmowa.
            </h2>
            <p>Fakty, braki danych i Twoje pytania — w jednym miejscu.</p>
            <span className="text-link">
              Zobacz brief
              <Icon name="arrow" size={17} />
            </span>
          </div>
          <div className="mini-paper" aria-hidden="true">
            <span>Cukier w biegu</span>
            <h3>
              Do rozmowy
              <br />z diabetologiem
            </h3>
            <div className="paper-rule" />
            <small>{demo.title}</small>
            <div className="mini-bars">
              <i />
              <i />
              <i />
            </div>
            <div className="paper-rule" />
            <div className="paper-lines">
              <i />
              <i />
              <i />
              <i />
              <i />
            </div>
            <span className="paper-bottom">Fakty. Kontekst. Pytania.</span>
          </div>
        </Link>
      </section>
      <div className="demo-disclosure">
        <DataBadge synthetic={demo.synthetic} />
        <p>
          {demo.synthetic
            ? "Cały bieg i wszystkie odczyty są przykładowe."
            : "Wykresy i fakty pochodzą z Twoich wgranych plików."}{" "}
          Dane pozostają w pamięci karty; odświeżenie strony je usuwa.{" "}
          <Link href="/sources">Zmień lub usuń dane</Link>.
        </p>
      </div>
      {showObservation && (
        <ObservationDialog onClose={() => setShowObservation(false)} />
      )}
    </AppShell>
  );
}
