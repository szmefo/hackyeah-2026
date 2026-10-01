export const dynamic = "force-dynamic";

export function GET() {
  return Response.json(
    { status: "ok", service: "hackyeah-2026", phase: "pre-hackathon-starter" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
