import { NextResponse } from "next/server";
export const dynamic = "force-dynamic";
export async function GET() {
  return NextResponse.json(
    { configured: Boolean(process.env.OPENAI_API_KEY), provider: "OpenAI" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
