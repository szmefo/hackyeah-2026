export const dynamic = "force-dynamic";

export function GET() {
  return Response.json(
    { status: "ok", service: "cukier-w-biegu", phase: "phase-1-synthetic-demo" },
    { headers: { "Cache-Control": "no-store" } },
  );
}
