import { createHash } from "node:crypto";
import { NextResponse } from "next/server";
import fixture from "../../../../data/demo-run.json";
import { canonical, verifyRun } from "@/lib/server/run-integrity";
import { interpret, type InterpretationContext } from "@/lib/server/ai";
import { getAIConfig } from "@/lib/server/provider-config";
import { ProviderError } from "@/lib/server/llm-transport";

export const runtime = "nodejs";
export const maxDuration = 60;
const headers = { "Cache-Control": "no-store" };
const rates = new Map<string, number[]>();
let active = 0;
function fallback(reason: string, status = 200) {
  return NextResponse.json({ status: "fallback", reason }, { status, headers });
}

export async function POST(request: Request) {
  let data;
  try {
    if (
      !request.headers.get("content-type")?.startsWith("application/json") ||
      !request.body
    )
      return fallback("Nieprawidłowe żądanie analizy.", 400);
    let size = 0;
    const chunks: Uint8Array[] = [];
    const reader = request.body.getReader();
    while (true) {
      const { done, value: chunk } = await reader.read();
      if (done) break;
      size += chunk.length;
      if (size > 512 * 1024) {
        await reader.cancel();
        return fallback("Dane analizy są zbyt duże.", 413);
      }
      chunks.push(chunk);
    }
    data = JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    return fallback("Nieprawidłowe dane analizy.", 400);
  }
  if (!data || typeof data !== "object" || Array.isArray(data))
    return fallback("Nieprawidłowe dane analizy.", 400);
  if (data.consent !== true)
    return fallback(
      "Analiza AI wymaga osobnej zgody na przesłanie danych do wskazanego dostawcy.",
      400,
    );
  const config = getAIConfig();
  if (!config.configured)
    return fallback(
      "AI nie jest jeszcze podłączone. Fakty i podsumowanie nadal są dostępne.",
    );
  if (data.provider !== config.provider)
    return fallback(
      "Dostawca AI się zmienił. Odśwież stronę i sprawdź zgodę na analizę.",
      400,
    );
  const run = data.run;
  if (
    !run ||
    typeof run !== "object" ||
    !Array.isArray(run.moments) ||
    !run.facts
  )
    return fallback("Najpierw otwórz bieg.", 400);
  if (
    canonical(run) !== canonical(fixture) &&
    !verifyRun(run, process.env.ENGINE_SHARED_SECRET ?? "")
  )
    return fallback(
      "Dane biegu nie przeszły sprawdzenia. Wgraj pliki ponownie.",
      400,
    );
  const moment = run.moments.find(
    (item: { id: unknown }) => item.id === data.momentId,
  );
  if (!moment) return fallback("Wybierz moment biegu.", 400);
  const observations = data.observations ?? [];
  if (
    !Array.isArray(observations) ||
    observations.length > 20 ||
    observations.some(
      (item) =>
        !item ||
        typeof item.text !== "string" ||
        item.text.length > 500 ||
        typeof item.kind !== "string" ||
        item.kind.length > 40 ||
        !Number.isFinite(item.minute) ||
        item.minute < 0 ||
        item.minute > run.durationMinutes,
    )
  )
    return fallback("Sprawdź obserwacje biegu.", 400);

  const context: InterpretationContext = {
    facts: {},
    moment: {
      id: moment.id,
      minGlucose: moment.minGlucose,
      readingCount: moment.readingCount,
      altitudeChange: moment.altitudeChange,
      altitudeAscent: moment.altitudeAscent,
      separable: moment.separable,
    },
    unknowns: moment.unknowns,
    observations: observations
      .filter((item) => Math.abs(item.minute - moment.minute) <= 10)
      .map(({ text, minute, kind }) => ({ text, minute, kind })),
  };
  // Construct a fixed, minimized payload from signed measurements. No chart streams,
  // filenames, timestamps, GPS, device IDs, title or original uploads reach the AI provider.
  for (const [suffix, value, unit, description] of [
    [
      "glucose.minimum",
      moment.minGlucose,
      "mg/dL",
      "Najniższy odczyt glukozy w oknie wybranego momentu",
    ],
    [
      "glucose.count",
      moment.readingCount,
      "odczyty",
      "Liczba odczytów glukozy w oknie wybranego momentu",
    ],
    [
      "altitude.change",
      moment.altitudeChange,
      "m",
      "Zmiana wysokości terenu w oknie wybranego momentu",
    ],
    ["pace", moment.pace, "min/km", "Tempo biegu w wybranym momencie"],
    ["heartrate", moment.hr, "ud/min", "Tętno w wybranym momencie"],
    [
      "minute",
      moment.minute,
      "min",
      "Pozycja wybranego momentu od początku biegu",
    ],
    [
      "separable",
      moment.separable ? "yes" : "no",
      "",
      "Czy dane pozwalają rozdzielić wpływ współwystępujących czynników",
    ],
  ] as const) {
    context.facts[`${moment.id}.${suffix}`] = { value, unit, description };
  }
  for (const [suffix, value, unit, description] of [
    [
      "coverage",
      run.facts.coveragePct,
      "%",
      "Pokrycie glukozy w całym biegu; nie miara pewności w wybranym oknie",
    ],
    [
      "below70Count",
      run.facts.below70Count,
      "odczyty",
      "Liczba odczytów glukozy poniżej progu w całym biegu",
    ],
  ] as const)
    context.facts[`run.${suffix}`] = { value, unit, description };
  for (const [id, fact] of Object.entries(run.factRegistry ?? {})) {
    if (!id.startsWith(`${moment.id}.`) || Object.hasOwn(context.facts, id))
      continue;
    const item = fact as {
      value: number | string | null;
      unit: string;
      description: string;
    };
    if (
      id.length <= 100 &&
      typeof item.unit === "string" &&
      typeof item.description === "string" &&
      (item.value === null ||
        typeof item.value === "string" ||
        (typeof item.value === "number" && Number.isFinite(item.value)))
    ) {
      context.facts[id] = {
        value: item.value,
        unit: item.unit,
        description: item.description,
      };
    }
    if (Object.keys(context.facts).length >= 60) break;
  }

  const ip =
    request.headers.get("x-vercel-forwarded-for") ??
    request.headers.get("x-forwarded-for") ??
    "local";
  const bucket = createHash("sha256").update(ip).digest("hex");
  const now = Date.now();
  for (const [key, times] of rates)
    if (times.every((time) => now - time > 3600000)) rates.delete(key);
  const recent = (rates.get(bucket) ?? []).filter(
    (time) => now - time < 3600000,
  );
  if (
    recent.length >= 8 ||
    recent.filter((time) => now - time < 60000).length >= 2 ||
    active >= 3 ||
    rates.size > 1000
  )
    return fallback(
      "Osiągnięto limit analiz. Poczekaj chwilę; fakty nadal są dostępne.",
      429,
    );
  rates.set(bucket, [...recent, now]);
  active += 1;
  try {
    const result = await interpret(
      context,
      config.key,
      config.model,
      config.provider,
    );
    return NextResponse.json(result, { headers });
  } catch (error) {
    // Log only finite diagnostic labels, never request/provider content or secrets.
    if (error instanceof ProviderError)
      console.warn(
        "AI provider failure",
        error.provider,
        error.code,
        error.status ?? "network",
      );
    else if (
      error instanceof Error &&
      ["analysis_rejected", "review_rejected"].includes(error.message)
    )
      console.warn("AI quality check", error.message);
    return fallback(
      "Nie udało się uzyskać sprawdzonej interpretacji AI. Poniżej pozostają fakty i podsumowanie z danych.",
    );
  } finally {
    active -= 1;
  }
}
