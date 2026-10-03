import { NextResponse } from "next/server";
import { getAIConfig } from "@/lib/server/provider-config";
export const dynamic = "force-dynamic";
export async function GET() {
  const config = getAIConfig();
  return NextResponse.json(
    { configured: config.configured, provider: config.provider },
    { headers: { "Cache-Control": "no-store" } },
  );
}
