"use client";

import { useState } from "react";

export function HealthCheck() {
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState("API jeszcze niesprawdzone.");

  async function checkHealth() {
    setPending(true);
    setMessage("Sprawdzam API…");
    try {
      const response = await fetch("/api/health", { cache: "no-store" });
      if (!response.ok) throw new Error("API request failed");
      const data: unknown = await response.json();
      if (
        typeof data !== "object" ||
        data === null ||
        !("status" in data) || data.status !== "ok" ||
        !("service" in data) || data.service !== "hackyeah-2026" ||
        !("phase" in data) || data.phase !== "pre-hackathon-starter"
      ) throw new Error("Unexpected API response");
      setMessage("API działa. Odpowiedź serwera: ok.");
    } catch {
      setMessage("Nie udało się sprawdzić API. Spróbuj ponownie.");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="health-check">
      <button type="button" disabled={pending} onClick={checkHealth}>
        {pending ? "Sprawdzam…" : "Sprawdź API"}
      </button>
      <p role="status" aria-live="polite">{message}</p>
    </div>
  );
}
