"use client";
import Link from "next/link";
import { AppShell, DataBadge } from "@/components/app-shell";
import { Icon } from "@/components/icons";
import { useDemo } from "@/components/demo-context";
import { decimal, dateLabel, durationLabel } from "@/lib/demo";
export default function Runs() {
  const { currentRun: run, resetRun } = useDemo();
  return (
    <AppShell>
      <div className="listing-intro">
        <span className="eyebrow">Twoje biegi</span>
        <h1>
          Każdy bieg
          <br />
          ma swoją historię.
        </h1>
        <p>
          Zobacz, co mówią dane z zegarka i sensora, gdy położysz je obok
          siebie.
        </p>
      </div>
      <Link href="/" className="run-list-card">
        <div>
          <span className="eyebrow">{dateLabel(run)}</span>
          <h2>{run.title}</h2>
          <DataBadge synthetic={run.synthetic} />
        </div>
        <div className="list-metrics">
          <span>
            {run.distanceKm === null
              ? "Brak dystansu"
              : `${decimal(run.distanceKm)} km`}
          </span>
          <span>{durationLabel(run.durationMinutes)}</span>
          <span>
            {run.facts.coveragePct}%<small> pokrycia glukozy</small>
          </span>
        </div>
        <span className="button primary">
          Otwórz bieg
          <Icon name="arrow" />
        </span>
      </Link>
      <p className="listing-note">
        Jeden bieg naraz. Dane i obserwacje pozostają tylko w pamięci tej karty;
        odświeżenie strony je usuwa.
      </p>
      <div className="upload-actions">
        <Link className="button primary" href="/sources">
          Dodaj FIT i CSV
          <Icon name="arrow" />
        </Link>
        {run.provenance.engineUsed && (
          <button className="button secondary" onClick={resetRun}>
            Usuń dane i wróć do demo
          </button>
        )}
      </div>
    </AppShell>
  );
}
