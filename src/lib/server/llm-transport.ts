// Provider HTTP boundaries: no logs, persistence, provider bodies or secrets in errors.
import type { AIConfig } from "./provider-config";

export class ProviderError extends Error {
  readonly code: string;
  readonly provider: AIConfig["provider"];
  readonly status?: number;

  constructor(code: string, provider: AIConfig["provider"], status?: number) {
    super(code);
    this.name = "ProviderError";
    this.code = code;
    this.provider = provider;
    this.status = status;
  }
}

function object(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export async function callStructured(
  config: AIConfig,
  system: string,
  data: unknown,
  schema: object,
  name: string,
): Promise<unknown> {
  const { provider, key, model } = config;
  const failure = (code: string, status?: number) =>
    new ProviderError(code, provider, status);
  if (!config.configured || !key.trim())
    throw failure("provider_not_configured");
  if (provider === "OpenAI" && key.trim().startsWith("sk-ant-"))
    throw failure("provider_config_invalid");

  let response: Response;
  try {
    const userData = JSON.stringify(data);
    const anthropic = provider === "Anthropic";
    response = await fetch(
      anthropic
        ? "https://api.anthropic.com/v1/messages"
        : "https://api.openai.com/v1/responses",
      {
        method: "POST",
        headers: anthropic
          ? {
              "x-api-key": key,
              "anthropic-version": "2023-06-01",
              "Content-Type": "application/json",
            }
          : {
              Authorization: `Bearer ${key}`,
              "Content-Type": "application/json",
            },
        body: JSON.stringify(
          anthropic
            ? {
                model,
                max_tokens: 1800,
                system,
                messages: [{ role: "user", content: userData }],
                output_config: { format: { type: "json_schema", schema } },
              }
            : {
                model,
                store: false,
                instructions: system,
                input: [
                  {
                    role: "user",
                    content: [{ type: "input_text", text: userData }],
                  },
                ],
                text: {
                  format: { type: "json_schema", name, schema, strict: true },
                },
                max_output_tokens: 1800,
              },
        ),
        signal: AbortSignal.timeout(22000),
        cache: "no-store",
      },
    );
  } catch {
    // A thrown fetch error can include request details. Never carry its message,
    // stack, cause, headers or body into our public/safe diagnostic error.
    throw failure("provider_unavailable");
  }
  if (!response.ok) throw failure("provider_unavailable", response.status);
  let output: unknown;
  try {
    output = await response.json();
  } catch {
    throw failure("provider_invalid_response");
  }
  if (!object(output)) throw failure("provider_invalid_response");
  let parts: unknown[];
  let textType: string;
  if (provider === "Anthropic") {
    if (output.stop_reason === "refusal") throw failure("provider_refusal");
    if (output.stop_reason !== "end_turn") throw failure("provider_incomplete");
    if (!Array.isArray(output.content))
      throw failure("provider_invalid_response");
    parts = output.content;
    textType = "text";
  } else {
    if (output.status !== "completed") throw failure("provider_incomplete");
    if (!Array.isArray(output.output))
      throw failure("provider_invalid_response");
    parts = output.output.flatMap((item: unknown) =>
      object(item) && Array.isArray(item.content) ? item.content : [],
    );
    textType = "output_text";
  }
  if (parts.some((part) => object(part) && part.type === "refusal"))
    throw failure("provider_refusal");
  const text = parts
    .filter((part) => object(part) && part.type === textType)
    .map((part) =>
      object(part) && typeof part.text === "string" ? part.text : "",
    )
    .join("");
  if (!text || text.length > 100_000)
    throw failure("provider_invalid_response");
  try {
    return JSON.parse(text);
  } catch {
    throw failure("provider_invalid_json");
  }
}
