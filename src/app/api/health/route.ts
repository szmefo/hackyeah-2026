export const dynamic = "force-dynamic";

export function GET() {
  return Response.json(
    {
      status: "ok",
      service: "cukier-w-biegu",
      phase: "phase-2-fit-cgm-import",
      storage: "none",
    },
    { headers: { "Cache-Control": "no-store" } },
  );
}
