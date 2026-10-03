"use client";
import { useEffect, useRef, useState } from "react";
import { useDemo } from "./demo-context";
import { Icon } from "./icons";
import type { AIInterpretation } from "@/lib/run-story";
import { factReferenceLabel } from "@/lib/demo";

export function AIAnalysis() {
  const {
    currentRun,
    selectedId,
    observations,
    revision,
    aiResult,
    setAIResult,
  } = useDemo();
  const [consent, setConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [configured, setConfigured] = useState<boolean | null>(null);
  const [error, setError] = useState("");
  const inflight = useRef<AbortController | null>(null);
  const revisionRef = useRef(revision);
  useEffect(() => {
    revisionRef.current = revision;
    return () => {
      inflight.current?.abort();
    };
  }, [revision]);
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/ai-status", { signal: controller.signal, cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .then((v) => {
        if (v) setConfigured(v.configured === true);
      })
      .catch(() => {});
    return () => controller.abort();
  }, []);
  async function analyze() {
    if (!consent || loading) return;
    inflight.current?.abort();
    const controller = new AbortController();
    inflight.current = controller;
    const originalRevision = revision;
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/interpret", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          run: currentRun,
          momentId: selectedId,
          observations,
          consent: true,
        }),
        signal: controller.signal,
      });
      const result = await response.json();
      if (controller.signal.aborted || revisionRef.current !== originalRevision)
        return;
      if (!response.ok)
        throw new Error(
          result.reason ??
            result.error ??
            "Nie udało się uzyskać analizy. Spróbuj ponownie.",
        );
      if (result.status !== "ai" && result.status !== "fallback")
        throw new Error("Nie udało się odczytać odpowiedzi AI.");
      setAIResult(result as AIInterpretation);
    } catch (e) {
      if (
        !controller.signal.aborted &&
        revisionRef.current === originalRevision
      )
        setError(
          e instanceof Error ? e.message : "Analiza jest chwilowo niedostępna.",
        );
    } finally {
      if (inflight.current === controller) {
        setLoading(false);
        inflight.current = null;
      }
    }
  }
  return (
    <section className="ai-section" aria-labelledby="ai-title" key={revision}>
      <div className="ai-intro">
        <span className="eyebrow">Od pomiarów do pytań</span>
        <h2 id="ai-title">Spójrzmy na ten moment razem.</h2>
        <p>
          AI porówna współwystępujące sygnały, rozważy różne wyjaśnienia i
          pomoże przygotować pytania do lekarza. Liczby nadal pochodzą z
          pomiarów.
        </p>
      </div>
      {aiResult?.status === "ai" ? (
        <div className="ai-result" aria-live="polite">
          <span className="synthetic-badge">
            Interpretacja AI · {aiResult.provider}
          </span>
          <h3>Co wynika z tego kontekstu</h3>
          <ul>
            {aiResult.claims.map((c, i) => (
              <li key={i}>
                {c.text}
                <small className="fact-references">
                  Podstawa: {factReferenceLabel(currentRun, c.factIds)}
                </small>
              </li>
            ))}
          </ul>
          {aiResult.alternatives.length > 0 && (
            <>
              <h3>Możliwe wyjaśnienia</h3>
              <ul>
                {aiResult.alternatives.map((c, i) => (
                  <li key={i}>
                    {c.text}
                    <small className="fact-references">
                      Podstawa: {factReferenceLabel(currentRun, c.factIds)}
                    </small>
                  </li>
                ))}
              </ul>
            </>
          )}
          <div className="ai-columns">
            <div>
              <h3>Co pozostaje niepewne</h3>
              <ul>
                {aiResult.unknowns.map((u, i) => (
                  <li key={i}>{u}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3>Pytania na wizytę</h3>
              <ul>
                {aiResult.questions.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>
          </div>
          <p className="privacy-note">
            Odpowiedź przeszła drugi przegląd AI i kontrolę odwołań do faktów.
            To kontrola jakości, nie niezależna weryfikacja medyczna. Model:{" "}
            {aiResult.model}.
          </p>
        </div>
      ) : (
        <>
          <label className="consent-label">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
            />
            <span>
              Zgadzam się wysłać do OpenAI obliczone fakty, kontekst wybranego
              momentu i moje obserwacje. Mogą zawierać dane zdrowotne. Pliki
              źródłowe i GPS nie są wysyłane do modelu.
            </span>
          </label>
          <p className="privacy-note">
            Nie zapisujemy analizy w bazie. OpenAI może przechowywać treść w
            logach monitorowania nadużyć do 30 dni; wyłączenie zapisu odpowiedzi
            nie usuwa tych logów.{" "}
            <a
              href="https://developers.openai.com/api/docs/guides/your-data"
              target="_blank"
              rel="noreferrer"
            >
              Zasady przetwarzania danych OpenAI
            </a>
            .
          </p>
          {configured === false && (
            <p className="upload-message">
              AI nie jest jeszcze podłączone. Wykresy, fakty i brief są dostępne
              bez niego.
            </p>
          )}
          <button
            className="button primary"
            onClick={analyze}
            disabled={!consent || loading || configured === false}
          >
            {loading ? "Analizuję kontekst…" : "Przeanalizuj ten moment z AI"}
            <Icon name="arrow" />
          </button>
          {loading && (
            <button
              className="text-link cancel-analysis"
              onClick={() => {
                inflight.current?.abort();
                setLoading(false);
              }}
            >
              Anuluj analizę
            </button>
          )}
          {(error || aiResult?.status === "fallback") && (
            <p className="upload-message" role="status">
              {error ||
                (aiResult?.status === "fallback" ? aiResult.reason : "")}{" "}
              Fakty i pytania z danych pozostają dostępne.
            </p>
          )}
        </>
      )}
    </section>
  );
}
