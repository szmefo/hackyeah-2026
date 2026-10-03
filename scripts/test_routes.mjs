// Integration tests against the real local Next proxy and Python engine.
// Uses only the public synthetic pair. Does not read credentials or call AI.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const base = process.env.QA_BASE_URL ?? "http://127.0.0.1:3000";
const fit = await readFile(new URL("../public/demo-run.fit", import.meta.url));
const glucose = await readFile(
  new URL("../public/demo-glucose.csv", import.meta.url),
);
let imported;

function form({
  consent = "true",
  synthetic = "false",
  fitBytes = fit,
  csvBytes = glucose,
  timezone = "Europe/Warsaw",
} = {}) {
  const data = new FormData();
  data.set("fit", new Blob([fitBytes]), "QA_ORIGINAL_FIT_NAME.fit");
  data.set("glucose", new Blob([csvBytes]), "QA_ORIGINAL_CSV_NAME.csv");
  data.set("timezone", timezone);
  data.set("consent", consent);
  data.set("synthetic", synthetic);
  return data;
}

async function upload(options) {
  const response = await fetch(`${base}/api/import`, {
    method: "POST",
    body: form(options),
  });
  return { response, body: await response.json() };
}

test("public health and synthetic downloads are available", async () => {
  const response = await fetch(`${base}/api/health`);
  assert.equal(response.status, 200);
  assert.equal((await response.json()).service, "cukier-w-biegu");
  assert.equal(response.headers.get("cache-control"), "no-store");
  for (const [filename, expected] of [
    ["demo-run.fit", fit],
    ["demo-glucose.csv", glucose],
  ]) {
    const file = await fetch(`${base}/${filename}`);
    assert.equal(file.status, 200);
    assert.deepEqual(Buffer.from(await file.arrayBuffer()), expected);
  }
});

test("actual Next-to-Python synthetic golden path returns computed signed facts", async () => {
  const { response, body } = await upload({ synthetic: "true" });
  assert.equal(response.status, 200, JSON.stringify(body));
  assert.equal(response.headers.get("cache-control"), "no-store");
  imported = body.run;
  assert.equal(imported.provenance.engineUsed, true);
  assert.equal(imported.synthetic, true);
  assert.equal(imported.facts.coveragePct, 73);
  assert.equal(imported.facts.minGlucose, 65);
  assert.equal(imported.facts.below70Count, 2);
  assert.equal(imported.start, "2026-10-03T08:30:00+02:00");
  assert.match(imported.analysisToken, /^[a-f0-9]{64}$/);
  assert.ok(imported.moments.length >= 1);
  const text = JSON.stringify(body);
  assert.ok(
    !text.includes("QA_ORIGINAL") &&
      !text.includes("position_lat") &&
      !text.includes("position_long"),
  );
});

test("ordinary upload is labelled uploaded without synthetic checkbox", async () => {
  const { response, body } = await upload();
  assert.equal(response.status, 200);
  assert.equal(body.run.synthetic, false);
  assert.equal(body.run.provenance.kind, "uploaded");
});

test("upload without literal processing consent is rejected", async () => {
  const { response, body } = await upload({ consent: "false" });
  assert.equal(response.status, 400);
  assert.equal(body.code, "consent_required");
});

test("synthetic checkbox cannot mislabel changed files", async () => {
  const { response, body } = await upload({
    synthetic: "true",
    csvBytes: Buffer.concat([glucose, Buffer.from("\n")]),
  });
  assert.equal(response.status, 422);
  assert.equal(body.code, "synthetic_mismatch");
});

test("malformed CSV, no time overlap and invalid zone are actionable failures", async () => {
  for (const [options, code] of [
    [{ csvBytes: Buffer.from("random,columns\n1,2\n") }, "csv_header"],
    [
      {
        csvBytes: Buffer.from(
          "Timestamp (YYYY-MM-DDThh:mm:ss),Event Type,Glucose Value (mg/dL)\n2025-01-01T08:30:00,EGV,130\n",
        ),
      },
      "no_glucose_overlap",
    ],
    [{ timezone: "Not/AZone" }, "invalid_timezone"],
  ]) {
    const { response, body } = await upload(options);
    assert.equal(response.status, 422, JSON.stringify(body));
    assert.equal(body.code, code);
    assert.equal(typeof body.error, "string");
  }
});

test("corrupt FIT does not expose content or decoder errors", async () => {
  const marker = "QA_PRIVATE_CONTENT_MARKER";
  const { response, body } = await upload({ fitBytes: Buffer.from(marker) });
  assert.equal(response.status, 422);
  const text = JSON.stringify(body);
  assert.ok(
    !text.includes(marker) &&
      !text.includes("Traceback") &&
      !text.includes("QA_ORIGINAL"),
  );
});

test("empty, missing and oversized uploads are rejected", async () => {
  assert.equal(
    (await upload({ fitBytes: Buffer.alloc(0) })).response.status,
    422,
  );
  assert.equal(
    (await upload({ fitBytes: Buffer.alloc(2 * 1024 * 1024 + 1) })).response
      .status,
    413,
  );
  const data = new FormData();
  data.set("consent", "true");
  const missing = await fetch(`${base}/api/import`, {
    method: "POST",
    body: data,
  });
  assert.equal(missing.status, 422);
});

test("incorrect import content type is rejected", async () => {
  const response = await fetch(`${base}/api/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });
  assert.equal(response.status, 400);
});

test("AI requires separate literal consent and returns safe fallback", async () => {
  const status = await fetch(`${base}/api/ai-status`);
  assert.equal(status.status, 200);
  const config = await status.json();
  assert.equal(typeof config.configured, "boolean");
  assert.ok(!JSON.stringify(config).includes("API_KEY"));
  const denied = await fetch(`${base}/api/interpret`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      run: imported,
      momentId: imported.moments[0].id,
      observations: [],
      consent: false,
    }),
  });
  assert.equal(denied.status, 400);
  assert.equal((await denied.json()).status, "fallback");
  // Only exercise the no-provider path. Never spend money/send data during QA.
  if (config.configured === false) {
    const unavailable = await fetch(`${base}/api/interpret`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        run: imported,
        momentId: imported.moments[0].id,
        observations: [],
        consent: true,
      }),
    });
    assert.equal(unavailable.status, 200);
    assert.equal(unavailable.headers.get("cache-control"), "no-store");
    const result = await unavailable.json();
    assert.equal(result.status, "fallback");
    assert.equal(typeof result.reason, "string");
    assert.ok(!Object.hasOwn(result, "claims"));
  }
});
