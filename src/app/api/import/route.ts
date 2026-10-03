import { NextResponse } from "next/server";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { signRun } from "@/lib/server/run-integrity";
import { syntheticPairs, type SyntheticPair } from "@/lib/demo";

export const runtime = "nodejs";
export const maxDuration = 60;
const MAX_FILE = 2 * 1024 * 1024;
const MAX_BODY = 4 * 1024 * 1024 + 32 * 1024;
const headers = { "Cache-Control": "no-store" };
// Fixed files under public/ only; never a path taken from the request.
// Literal paths keep them in the traced serverless bundle.
const root = process.cwd();
const knownFiles: Record<string, [string, string]> = {
  przyklad: [
    join(root, "public", "demo-run.fit"),
    join(root, "public", "demo-glucose.csv"),
  ],
  "01-niski-cukier-na-plaskim": [
    join(root, "public", "scenarios", "01-niski-cukier-na-plaskim", "bieg.fit"),
    join(
      root,
      "public",
      "scenarios",
      "01-niski-cukier-na-plaskim",
      "glukoza.csv",
    ),
  ],
  "02-podbieg-cukier-w-normie": [
    join(root, "public", "scenarios", "02-podbieg-cukier-w-normie", "bieg.fit"),
    join(
      root,
      "public",
      "scenarios",
      "02-podbieg-cukier-w-normie",
      "glukoza.csv",
    ),
  ],
  "03-podbieg-i-niski-cukier": [
    join(root, "public", "scenarios", "03-podbieg-i-niski-cukier", "bieg.fit"),
    join(
      root,
      "public",
      "scenarios",
      "03-podbieg-i-niski-cukier",
      "glukoza.csv",
    ),
  ],
  "04-luka-w-danych": [
    join(root, "public", "scenarios", "04-luka-w-danych", "bieg.fit"),
    join(root, "public", "scenarios", "04-luka-w-danych", "glukoza.csv"),
  ],
};
type KnownPair = { pair: SyntheticPair; fit: Buffer; csv: Buffer };
let knownPairs: Promise<KnownPair[]> | null = null;
function loadKnownPairs() {
  knownPairs ??= Promise.all(
    syntheticPairs.map(async (pair) => {
      const [fit, csv] = await Promise.all(
        knownFiles[pair.id].map((path) => readFile(path)),
      );
      return { pair, fit, csv };
    }),
  ).catch((error) => {
    knownPairs = null;
    throw error;
  });
  return knownPairs;
}
/** Exact byte match against the known pairs; null when nothing matches. */
async function matchSyntheticPair(fit: Buffer, csv: Buffer) {
  try {
    const pairs = await loadKnownPairs();
    return (
      pairs.find((known) => known.fit.equals(fit) && known.csv.equals(csv))
        ?.pair ?? null
    );
  } catch {
    // Unreadable reference files: never label anything synthetic.
    return null;
  }
}
function fail(status: number, code: string, error: string) {
  return NextResponse.json({ code, error }, { status, headers });
}

export async function POST(request: Request) {
  const engine = process.env.ENGINE_URL;
  const secret = process.env.ENGINE_SHARED_SECRET;
  if (!engine || !secret)
    return fail(
      503,
      "engine_unavailable",
      "Import jest chwilowo niedostępny. Możesz otworzyć przykładowy bieg.",
    );
  if (!request.headers.get("content-type")?.startsWith("multipart/form-data"))
    return fail(400, "invalid_request", "Wybierz pliki FIT i CSV.");
  try {
    let size = 0;
    const chunks: Uint8Array[] = [];
    if (!request.body)
      return fail(400, "empty_request", "Wybierz pliki FIT i CSV.");
    const reader = request.body.getReader();
    while (true) {
      const { done, value: chunk } = await reader.read();
      if (done) break;
      size += chunk.length;
      if (size > MAX_BODY) {
        await reader.cancel();
        return fail(413, "file_too_large", "Maksymalnie 2 MB na plik.");
      }
      chunks.push(chunk);
    }
    const body = Buffer.concat(chunks);
    const bounded = new Request(request.url, {
      method: "POST",
      headers: request.headers,
      body,
    });
    const form = await bounded.formData();
    if (form.get("consent") !== "true")
      return fail(
        400,
        "consent_required",
        "Potwierdź zgodę na przetwarzanie plików.",
      );
    for (const [field, extension] of [
      ["fit", ".fit"],
      ["glucose", ".csv"],
    ]) {
      const file = form.get(field);
      if (!(file instanceof File) || !file.size)
        return fail(422, "missing_files", "Wybierz niepusty plik FIT i CSV.");
      if (file.size > MAX_FILE)
        return fail(413, "file_too_large", "Maksymalnie 2 MB na plik.");
      if (!file.name.toLowerCase().endsWith(extension))
        return fail(422, "file_type", "Potrzebujemy pliku .fit i .csv.");
    }
    const timezone = String(form.get("timezone") ?? "Europe/Warsaw");
    if (timezone.length > 64)
      return fail(422, "timezone_invalid", "Sprawdź strefę czasową.");
    const fitBytes = Buffer.from(await (form.get("fit") as File).arrayBuffer());
    const csvBytes = Buffer.from(
      await (form.get("glucose") as File).arrayBuffer(),
    );
    // Known pairs are labelled synthetic by exact byte match only, with or
    // without the client's flag. A synthetic claim for any other bytes fails.
    const known = await matchSyntheticPair(fitBytes, csvBytes);
    if (form.get("synthetic") === "true" && !known)
      return fail(
        422,
        "synthetic_mismatch",
        "Oznaczenie danych syntetycznych dotyczy wyłącznie niezmienionych par plików demo z tej strony.",
      );
    const forwarded = new FormData();
    // Generic names avoid transmitting the owner's original filenames.
    forwarded.set("fit", form.get("fit") as File, "run.fit");
    forwarded.set("glucose", form.get("glucose") as File, "glucose.csv");
    forwarded.set("timezone", timezone);
    forwarded.set("consent", "true");
    forwarded.set("synthetic", known ? "true" : "false");
    let response: Response;
    try {
      response = await fetch(`${engine.replace(/\/$/, "")}/analyze`, {
        method: "POST",
        headers: { "X-Engine-Secret": secret },
        body: forwarded,
        cache: "no-store",
        signal: AbortSignal.timeout(45000),
      });
    } catch {
      // Unreachable or timed-out engine: say so; the example run still works.
      return fail(
        503,
        "engine_unavailable",
        "Serwer analizy jest chwilowo niedostępny. Spróbuj ponownie za chwilę albo otwórz przykładowy bieg na stronie głównej.",
      );
    }
    if (!response.ok) {
      const result = await response.json().catch(() => null);
      return fail(
        response.status >= 500 ? 503 : response.status,
        typeof result?.code === "string" ? result.code : "engine_failed",
        typeof result?.error === "string"
          ? result.error
          : "Import się nie udał. Sprawdź pliki i spróbuj ponownie.",
      );
    }
    const result = await response.json();
    if (
      !result.run ||
      !Array.isArray(result.run.moments) ||
      !result.run.moments.length
    )
      return fail(
        502,
        "invalid_result",
        "Nie udało się przygotować historii biegu.",
      );
    if (known) {
      // Set before signing so the scenario name is covered by the token.
      result.run.synthetic = true;
      result.run.title = known.runTitle;
    }
    result.run.analysisToken = signRun(result.run, secret);
    return NextResponse.json(result, { headers });
  } catch {
    return fail(
      503,
      "import_failed",
      "Import się nie udał. Spróbuj ponownie lub otwórz przykładowy bieg.",
    );
  }
}
