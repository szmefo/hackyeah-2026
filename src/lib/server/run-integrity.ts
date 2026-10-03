import { createHmac, timingSafeEqual } from "node:crypto";

export function canonical(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  return `{${Object.entries(value as Record<string, unknown>)
    .filter(([key]) => key !== "analysisToken")
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, item]) => `${JSON.stringify(key)}:${canonical(item)}`)
    .join(",")}}`;
}

export function signRun(run: unknown, secret: string): string {
  return createHmac("sha256", secret).update(canonical(run)).digest("hex");
}

export function verifyRun(run: unknown, secret: string): boolean {
  if (!run || typeof run !== "object" || !secret) return false;
  const token = (run as { analysisToken?: unknown }).analysisToken;
  if (typeof token !== "string" || !/^[a-f0-9]{64}$/.test(token)) return false;
  return timingSafeEqual(
    Buffer.from(token, "hex"),
    Buffer.from(signRun(run, secret), "hex"),
  );
}
