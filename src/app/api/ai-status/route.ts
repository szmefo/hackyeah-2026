import { NextResponse } from "next/server";
import { getAIConfig } from "@/lib/server/provider-config";
export const dynamic = "force-dynamic";
export async function GET() {
  const config = getAIConfig();
  return NextResponse.json(
    // Name a provider only when one is configured; an unconfigured server
    // must not suggest where data would go.
    {
      configured: config.configured,
      provider: config.configured ? config.provider : null,
    },
    { headers: { "Cache-Control": "no-store" } },
  );
}
