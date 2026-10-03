import { NextResponse } from "next/server";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { signRun } from "@/lib/server/run-integrity";

export const runtime = "nodejs";
export const maxDuration = 60;
const MAX_FILE = 2 * 1024 * 1024;
const MAX_BODY = 4 * 1024 * 1024 + 32 * 1024;
const headers = { "Cache-Control": "no-store" };
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
    if (form.get("synthetic") === "true") {
      const [knownFit, knownCsv] = await Promise.all([
        readFile(join(process.cwd(), "public", "demo-run.fit")),
        readFile(join(process.cwd(), "public", "demo-glucose.csv")),
      ]);
      const fitBytes = Buffer.from(
        await (form.get("fit") as File).arrayBuffer(),
      );
      const csvBytes = Buffer.from(
        await (form.get("glucose") as File).arrayBuffer(),
      );
      if (!knownFit.equals(fitBytes) || !knownCsv.equals(csvBytes))
        return fail(
          422,
          "synthetic_mismatch",
          "Opcja danych syntetycznych dotyczy wyłącznie pobranej pary przykładowych plików.",
        );
    }
    const forwarded = new FormData();
    // Generic names avoid transmitting the owner's original filenames.
    forwarded.set("fit", form.get("fit") as File, "run.fit");
    forwarded.set("glucose", form.get("glucose") as File, "glucose.csv");
    forwarded.set("timezone", timezone);
    forwarded.set("consent", "true");
    forwarded.set(
      "synthetic",
      form.get("synthetic") === "true" ? "true" : "false",
    );
    const response = await fetch(`${engine.replace(/\/$/, "")}/analyze`, {
      method: "POST",
      headers: { "X-Engine-Secret": secret },
      body: forwarded,
      cache: "no-store",
      signal: AbortSignal.timeout(45000),
    });
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
