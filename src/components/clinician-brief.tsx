"use client";
import Link from "next/link";
import { AppShell, DataBadge } from "./app-shell";
import { Icon, Logo } from "./icons";
import { useDemo } from "./demo-context";
import {
  decimal,
  disclaimer,
  paceLabel,
  momentUnknowns,
  dateLabel,
  durationLabel,
  readingTime,
  minuteLabel,
  factReferenceLabel,
} from "@/lib/demo";
export function ClinicianBrief() {
  const { selectedId, observations, currentRun: run, aiResult } = useDemo();
  const selected =
    run.moments.find((m) => m.id === selectedId) ?? run.moments[0];
  const lowReadings = run.glucose.filter((p) => p.value < 70);
  return (
    <AppShell active="brief">
      <div className="brief-toolbar no-print">
        <Link href="/" className="back-link">
          <Icon name="back" />
          Wróć do biegu
        </Link>
        <div>
          <span>Podsumowanie do rozmowy</span>
          <button className="button primary" onClick={() => window.print()}>
            <Icon name="file" />
            Drukuj / zapisz PDF
          </button>
        </div>
      </div>
      <article className="brief-paper" aria-label="Brief dla lekarza">
        <header className="paper-header">
          <span className="paper-brand">
            <Logo />
            Cukier w biegu
          </span>
          <DataBadge synthetic={run.synthetic} />
        </header>
        <div className="paper-title">
          <p className="eyebrow">Do rozmowy z diabetologiem</p>
          <h1>
            Jeden bieg.
            <br />
            Konkretny kontekst.
          </h1>
          <p>
            Podsumowanie {run.synthetic ? "przykładowego" : "wgranego"} biegu i
            pytania do specjalisty.
          </p>
        </div>
        <section className="paper-profile">
          <div>
            <span>Źródła</span>
            <strong>
              {run.synthetic
                ? "Syntetyczny bieg i CGM"
                : "FIT z zegarka · CSV z CGM"}
            </strong>
          </div>
          <div>
            <span>Zakres</span>
            <strong>
              {dateLabel(run)} · {run.title}
            </strong>
          </div>
        </section>
        <dl className="brief-metrics">
          <div>
            <dt>Dystans</dt>
            <dd>
              {decimal(run.distanceKm)}
              {run.distanceKm !== null && <small> km</small>}
            </dd>
          </div>
          <div>
            <dt>Czas</dt>
            <dd>{durationLabel(run.durationMinutes)}</dd>
          </div>
          <div>
            <dt>Pokrycie glukozy</dt>
            <dd>
              {run.facts.coveragePct}
              <small>%</small>
            </dd>
          </div>
          <div>
            <dt>Najniższy odczyt</dt>
            <dd>
              {run.facts.minGlucose ?? "—"}
              {run.facts.minGlucose !== null && <small> mg/dL</small>}
            </dd>
          </div>
        </dl>
        <section className="paper-section">
          <h2>01 / Co widać w danych</h2>
          <p>
            <strong>{selected.title}</strong> {selected.narrative}
          </p>
          <div className="brief-window">
            <span>
              {minuteLabel(selected.minute)}. minuta
              {selected.distanceKm !== null
                ? ` · ${decimal(selected.distanceKm)} km`
                : ""}{" "}
              · okno ±10 min
            </span>
            <span>
              Tempo w momencie: {paceLabel(selected.pace)}
              {selected.pace !== null ? " min/km" : ""}
            </span>
          </div>
          <ul>
            {selected.factors.map((f) => (
              <li key={f.id}>
                {f.label}: {f.evidence}
              </li>
            ))}
          </ul>
          <p>
            Odczyty poniżej 70 mg/dL: <strong>{run.facts.below70Count}</strong>.
            Poniżej 54 mg/dL: <strong>{run.facts.below54Count}</strong>. To
            liczba punktowych odczytów, a nie czas epizodów.
          </p>
          {lowReadings.length > 0 && (
            <table>
              <caption>
                Odczyty poniżej 70 mg/dL
                {run.synthetic ? " — dane syntetyczne" : ""} · {run.timezone}
              </caption>
              <thead>
                <tr>
                  <th>Data / czas lokalny</th>
                  <th>Minuta biegu</th>
                  <th>Odczyt</th>
                  <th>Podstawa</th>
                </tr>
              </thead>
              <tbody>
                {lowReadings.slice(0, 12).map((p) => (
                  <tr key={p.minute}>
                    <td>{readingTime(run, p.minute)}</td>
                    <td>{minuteLabel(p.minute)}</td>
                    <td>{p.value} mg/dL</td>
                    <td>Pojedynczy odczyt CGM</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {lowReadings.length > 12 && (
            <p>
              W tabeli pierwsze 12 z {lowReadings.length} odczytów. Liczby
              powyżej obejmują cały bieg.
            </p>
          )}
          {!!run.glucoseFlags?.length && (
            <p>
              Sensor zapisał również {run.glucoseFlags.length} oznaczeń
              Low/High. Nie zamieniono ich na wymyślone wartości liczbowe.
            </p>
          )}
        </section>
        <section className="paper-section">
          <h2>02 / Czego dane nie rozstrzygają</h2>
          <ul>
            {run.gaps.map((gap) => (
              <li key={`${gap.start}-${gap.end}`}>
                Brak obserwacji glukozy między {minuteLabel(gap.start)}. a{" "}
                {minuteLabel(gap.end)}. minutą; tej przerwy nie uzupełniono.
              </li>
            ))}
            {momentUnknowns(selected, observations).map((u) => (
              <li key={u}>{u}</li>
            ))}
            {run.warnings?.map((w, i) => (
              <li key={`warning-${i}`}>{w}</li>
            ))}
          </ul>
          <p className="basis-note">{run.facts.basis}</p>
        </section>
        <section className="paper-section">
          <h2>03 / Pytania na wizytę</h2>
          <p className="paper-question">{selected.question}</p>
          <p>
            Jakie dodatkowe obserwacje warto zapisać, żeby lepiej omówić podobny
            bieg?
          </p>
        </section>
        <section className="paper-section paper-observations">
          <h2>04 / Obserwacje biegacza</h2>
          {observations.length ? (
            <ul>
              {observations.map((o, i) => (
                <li key={i}>
                  {minuteLabel(o.minute)}. minuta · {o.kind}: {o.text}
                </li>
              ))}
            </ul>
          ) : (
            <p>
              Nie dodano obserwacji. Warto zanotować odczucia i przybliżony czas
              ich wystąpienia.
            </p>
          )}
        </section>
        {aiResult?.status === "ai" && (
          <section className="paper-section">
            <h2>05 / Interpretacja AI wybranego momentu</h2>
            <ul>
              {aiResult.claims.map((c, i) => (
                <li key={i}>
                  {c.text}{" "}
                  <small>Podstawa: {factReferenceLabel(run, c.factIds)}</small>
                </li>
              ))}
            </ul>
            {aiResult.alternatives.length > 0 && (
              <>
                <strong>Możliwe wyjaśnienia</strong>
                <ul>
                  {aiResult.alternatives.map((c, i) => (
                    <li key={i}>{c.text}</li>
                  ))}
                </ul>
              </>
            )}
            <strong>Niepewność i pytania</strong>
            <ul>
              {[...aiResult.unknowns, ...aiResult.questions].map((text, i) => (
                <li key={i}>{text}</li>
              ))}
            </ul>
            <p className="basis-note">
              {aiResult.provider} · {aiResult.model}. Drugi przegląd AI i
              kontrola odwołań do faktów nie są niezależną weryfikacją medyczną.
            </p>
          </section>
        )}
        <footer className="paper-footer">
          <strong>
            {run.synthetic ? "Dane syntetyczne" : "Dane z wgranych plików"} ·
            prototyp HackYeah 2026
          </strong>
          <p>{disclaimer}</p>
          <p>
            {run.synthetic
              ? "Wszystkie liczby pochodzą z przykładowego zestawu danych."
              : "Fakty obliczono z pomiarów; brakujących wartości nie uzupełniono."}{" "}
            {aiResult?.status === "ai"
              ? "Sekcja AI jest interpretacją, a nie pomiarem."
              : "Podsumowanie faktów nie korzysta z modelu AI."}
          </p>
        </footer>
      </article>
    </AppShell>
  );
}
