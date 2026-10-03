"use client";
import Link from "next/link";
import { AppShell, SyntheticBadge } from "./app-shell";
import { Icon, Logo } from "./icons";
import { useDemo } from "./demo-context";
import { demo, decimal, disclaimer, paceLabel, momentUnknowns } from "@/lib/demo";

export function ClinicianBrief() {
  const { selectedId, observations } = useDemo();
  const selected = demo.moments.find(m=>m.id===selectedId) ?? demo.moments[2];
  return <AppShell active="brief"><div className="brief-toolbar no-print"><Link href="/" className="back-link"><Icon name="back" />Wróć do biegu</Link><div><span>Jedna strona do rozmowy</span><button className="button primary" onClick={()=>window.print()}><Icon name="file" />Drukuj / zapisz PDF</button></div></div>
    <article className="brief-paper" aria-label="Brief dla lekarza">
      <header className="paper-header"><span className="paper-brand"><Logo />Cukier w biegu</span><SyntheticBadge /></header>
      <div className="paper-title"><p className="eyebrow">Do rozmowy z diabetologiem</p><h1>Jeden bieg.<br />Konkretny kontekst.</h1><p>Podsumowanie przykładowego biegu i pytania do specjalisty.</p></div>
      <section className="paper-profile"><div><span>Profil demonstracyjny</span><strong>Dorosły biegacz · typ 1 · CGM</strong></div><div><span>Zakres</span><strong>03.10.2026 · {demo.title}</strong></div></section>
      <dl className="brief-metrics"><div><dt>Dystans</dt><dd>{decimal(demo.distanceKm)}<small> km</small></dd></div><div><dt>Czas</dt><dd>1:34:00</dd></div><div><dt>Pokrycie glukozy</dt><dd>{demo.facts.coveragePct}<small>%</small></dd></div><div><dt>Najniższy odczyt</dt><dd>{demo.facts.minGlucose}<small> mg/dL</small></dd></div></dl>
      <section className="paper-section"><h2>01 / Co widać w danych</h2><p><strong>{selected.title}</strong> {selected.narrative}</p><div className="brief-window"><span>{selected.minute}. minuta · {decimal(selected.distanceKm)} km · okno ±10 min</span><span>Tempo w momencie: {paceLabel(selected.pace)} min/km</span></div><ul>{selected.factors.map(f=><li key={f.id}>{f.label}: {f.evidence}</li>)}</ul><p>Odczyty poniżej 70 mg/dL: <strong>{demo.facts.below70Count}</strong>. Poniżej 54 mg/dL: <strong>{demo.facts.below54Count}</strong>. To liczba punktowych odczytów, a nie czas epizodów.</p><table><caption>Odczyty poniżej 70 mg/dL — dane syntetyczne</caption><thead><tr><th>Data / czas lokalny</th><th>Minuta biegu</th><th>Odczyt</th><th>Podstawa</th></tr></thead><tbody>{demo.glucose.filter(p=>p.value<70).map(p=><tr key={p.minute}><td>03.10.2026 · {String(8+Math.floor((30+p.minute)/60)).padStart(2,'0')}:{String((30+p.minute)%60).padStart(2,'0')}</td><td>{p.minute}</td><td>{p.value} mg/dL</td><td>Pojedynczy odczyt CGM</td></tr>)}</tbody></table></section>
      <section className="paper-section"><h2>02 / Czego dane nie rozstrzygają</h2><ul><li>Glukoza nie jest obserwowana między {demo.gaps[0].start}. a {demo.gaps[0].end}. minutą; tej przerwy nie uzupełniono.</li>{momentUnknowns(selected, observations).map(u=><li key={u}>{u}</li>)}</ul><p className="basis-note">{demo.facts.basis}</p></section>
      <section className="paper-section"><h2>03 / Pytania na wizytę</h2><p className="paper-question">{selected.question}</p><p>Jakie dodatkowe obserwacje warto zapisać, żeby lepiej omówić podobny bieg?</p></section>
      <section className="paper-section paper-observations"><h2>04 / Obserwacje biegacza</h2>{observations.length ? <ul>{observations.map((o,i)=><li key={i}>{o.minute}. minuta · {o.kind}: {o.text}</li>)}</ul> : <p>Nie dodano obserwacji. Warto zanotować odczucia i przybliżony czas ich wystąpienia.</p>}</section>
      <footer className="paper-footer"><strong>Dane syntetyczne · prototyp HackYeah 2026</strong><p>{disclaimer}</p><p>Wszystkie liczby pochodzą z przykładowego zestawu danych. To nie jest analiza danych pacjenta.</p></footer>
    </article>
  </AppShell>;
}
