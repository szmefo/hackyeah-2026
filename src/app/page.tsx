import { HealthCheck } from "@/components/health-check";

export default function Home() {
  return (
    <main>
      <p className="eyebrow">PRE-HACKATHON STARTER · 2026</p>
      <h1>HackYeah 2026</h1>
      <p className="intro">
        Środowisko gotowe. Rozwiązanie zaczniemy budować po ujawnieniu zadania.
      </p>
      <section aria-labelledby="workspace-title">
        <h2 id="workspace-title">Czysty punkt startu</h2>
        <p>
          Ten ekran sprawdza wyłącznie działanie startera. Problem, rozwiązanie
          i demo pozostają do ustalenia podczas hackathonu.
        </p>
        <HealthCheck />
        <a href="/api/health">Otwórz odpowiedź API</a>
      </section>
      <footer>Bez kodu UltraSoul · Bez integracji AI · Bez danych zdrowotnych</footer>
    </main>
  );
}
