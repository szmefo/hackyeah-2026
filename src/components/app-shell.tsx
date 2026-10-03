import Link from "next/link";
import { Logo, Icon } from "./icons";
import { disclaimer } from "@/lib/demo";

export function SyntheticBadge() {
  return <span className="synthetic-badge">Dane syntetyczne</span>;
}
export function DataBadge({ synthetic }: { synthetic: boolean }) {
  return synthetic ? (
    <SyntheticBadge />
  ) : (
    <span className="synthetic-badge uploaded-badge">Wgrane dane</span>
  );
}
export function AppShell({
  children,
  active = "runs",
}: {
  children: React.ReactNode;
  active?: string;
}) {
  return (
    <div className="app-shell">
      <header className="site-header">
        <Link
          href="/"
          className="brand"
          aria-label="Cukier w biegu — strona główna"
        >
          <Logo />
          <span>
            Cukier w biegu<small>Biegam. Rozumiem. Rozmawiam.</small>
          </span>
        </Link>
        <nav aria-label="Nawigacja główna">
          <Link className={active === "runs" ? "active" : ""} href="/runs">
            Biegi
          </Link>
          <Link
            className={active === "sources" ? "active" : ""}
            href="/sources"
          >
            Źródła
          </Link>
          <Link className={active === "brief" ? "active" : ""} href="/brief">
            Brief dla lekarza
          </Link>
        </nav>
        <span className="demo-pill">
          <span /> Wersja demo
        </span>
      </header>
      <main>{children}</main>
      <footer className="site-footer">
        <p>{disclaimer}</p>
        <span>Ten sam bieg. Większy kontekst.</span>
      </footer>
      <div className="brand-footer">
        <span>
          Cukier w biegu <i>— dla tych, którzy idą dalej.</i>
        </span>
        <span className="footer-line" />
        <span>HackYeah 2026</span>
      </div>
    </div>
  );
}
export function BriefLink({
  className = "button primary",
}: {
  className?: string;
}) {
  return (
    <Link href="/brief" className={className}>
      <Icon name="file" />
      Brief dla lekarza
      <Icon name="arrow" />
    </Link>
  );
}
