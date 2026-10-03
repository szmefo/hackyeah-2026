import Link from "next/link";
import { AppShell, SyntheticBadge } from "@/components/app-shell";
import { Icon } from "@/components/icons";
import { demo } from "@/lib/demo";
export default function Sources() {
  return <AppShell active="sources"><div className="listing-intro"><span className="eyebrow">Skąd jest ta historia</span><h1>Dwa źródła.<br />Jedna oś czasu.</h1><p>W tej wersji używamy wyłącznie przykładowych danych. Import Twoich plików FIT i CSV będzie następnym etapem.</p></div><section className="sources-grid"><article className="source-card"><Icon name="clock" size={32} /><h2>Dane biegu</h2><p>Tempo, tętno i profil wysokości na wspólnej osi czasu.</p><SyntheticBadge /><div className="source-status"><Icon name="check" />Przykładowy bieg jest gotowy</div></article><article className="source-card"><Icon name="drop" size={32} /><h2>Odczyty glukozy</h2><p>{demo.facts.readingCount} przykładowych odczytów. Przerwa w danych jest widoczna na wykresie.</p><SyntheticBadge /><a className="text-link" href="/demo-glucose.csv" download>Pobierz przykładowy CSV<Icon name="arrow" size={17} /></a></article></section><Link href="/" className="button primary sources-cta">Przejdź do przykładowego biegu<Icon name="arrow" /></Link></AppShell>;
}
