import Link from "next/link";
import { AppShell, SyntheticBadge } from "@/components/app-shell";
import { Icon } from "@/components/icons";
import { demo, decimal } from "@/lib/demo";
export default function Runs() {
  return <AppShell><div className="listing-intro"><span className="eyebrow">Twoje biegi</span><h1>Każdy bieg<br />ma swoją historię.</h1><p>Zobacz, co mówią dane z zegarka i sensora, gdy położysz je obok siebie.</p></div><Link href="/" className="run-list-card"><div><span className="eyebrow">03 października 2026</span><h2>{demo.title}</h2><SyntheticBadge /></div><div className="list-metrics"><span>{decimal(demo.distanceKm)} km</span><span>1:34:00</span><span>{demo.facts.coveragePct}%<small> pokrycia glukozy</small></span></div><span className="button primary">Otwórz bieg<Icon name="arrow" /></span></Link><p className="listing-note">Na razie jeden przykładowy bieg, gotowy do przejścia całej ścieżki demo.</p></AppShell>;
}
