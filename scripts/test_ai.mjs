import { test } from "node:test";
import assert from "node:assert/strict";
import { validateAnalysis, interpret } from "../src/lib/server/ai.ts";
import { signRun, verifyRun } from "../src/lib/server/run-integrity.ts";

const context = {
  facts: {
    "m.glucose.minimum": {
      value: 65,
      unit: "mg/dL",
      description: "Odczyt glukozy w oknie",
    },
    "m.altitude.change": {
      value: 34,
      unit: "m",
      description: "Zmiana wysokości terenu",
    },
    "m.pace": { value: 7.2, unit: "min/km", description: "Tempo biegu" },
  },
  moment: {
    id: "m",
    minGlucose: 65,
    readingCount: 4,
    altitudeChange: 34,
    separable: false,
  },
  unknowns: ["Brak kontekstu"],
  observations: [],
};
const valid = () => ({
  claims: [
    {
      text: "Niższy odczyt glukozy współwystąpił ze zmianą tempa.",
      factIds: ["m.glucose.minimum", "m.pace"],
    },
  ],
  alternatives: [
    {
      text: "W tym oknie wzrosła też wysokość terenu.",
      factIds: ["m.altitude.change"],
    },
  ],
  unknowns: [
    "Dane nie pozwalają rozdzielić wpływu tych czynników ani ustalić przyczyny.",
  ],
  questions: ["Jak omówić ten odcinek w kontekście ograniczeń sensora?"],
});

test("accepts cautious evidence-linked interpretation", () =>
  assert.equal(validateAnalysis(valid(), context), true));
test("rejects fabricated IDs and valid but unrelated measurement references", () => {
  const a = valid();
  a.claims[0].factIds = ["invented"];
  assert.equal(validateAnalysis(a, context), false);
  a.claims[0].factIds = ["m.pace"];
  assert.equal(validateAnalysis(a, context), false);
});
test("rejects model numbers, medication/food directives, causal certainty and fake quotes", () => {
  for (const text of [
    "Glukoza wynosiła 65 mg/dL.",
    "Zmniejsz dawkę insuliny.",
    "Zjedz żel wcześniej.",
    "Niska glukoza spowodowała spadek tempa.",
    "Weź więcej leku.",
    'Biegacz powiedział "wszystko dobrze".',
    "Masz hipoglikemię.",
    "Glukoza odpowiada za spadek tempa.",
    "Niska glukoza wynika z podbiegu.",
  ]) {
    const a = valid();
    a.claims[0].text = text;
    assert.equal(validateAnalysis(a, context), false, text);
  }
});
test("rejects invented low glucose when the window is empty", () => {
  const a = valid();
  a.claims[0].text = "Niski odczyt glukozy współwystąpił ze zmianą tempa.";
  assert.equal(
    validateAnalysis(a, {
      ...context,
      moment: { ...context.moment, readingCount: 0, minGlucose: null },
    }),
    false,
  );
  a.claims[0].text = "Niższy odczyt glukozy wystąpił w tym oknie.";
  assert.equal(
    validateAnalysis(a, {
      ...context,
      moment: { ...context.moment, readingCount: 0, minGlucose: null },
    }),
    false,
  );
});
test("rejects invented uphill with zero or missing terrain change", () => {
  const a = valid();
  a.alternatives[0].text = "Był podbieg w tym samym oknie.";
  for (const change of [null, 0])
    assert.equal(
      validateAnalysis(a, {
        ...context,
        moment: { ...context.moment, altitudeChange: change },
      }),
      false,
    );
});
test("safe negation of causal certainty is accepted", () => {
  const a = valid();
  a.unknowns = [
    "Współwystępowanie nie dowodzi przyczyny i nie pozwala rozdzielić wpływu czynników.",
  ];
  assert.equal(validateAnalysis(a, context), true);
});
test("requires uncertainty and competing-factor limitation", () => {
  const a = valid();
  a.unknowns = ["Wszystko jest jasne i znane."];
  assert.equal(validateAnalysis(a, context), false);
  a.unknowns = ["Dane nie pozwalają ustalić przyczyny."];
  assert.equal(validateAnalysis(a, context), false);
});
test("signature survives key ordering but rejects tampered measurement", () => {
  const a = { facts: { minimum: 65 }, title: "run" };
  const token = signRun(a, "test-only-secret");
  assert.equal(
    verifyRun(
      { title: "run", facts: { minimum: 65 }, analysisToken: token },
      "test-only-secret",
    ),
    true,
  );
  assert.equal(
    verifyRun(
      { ...a, facts: { minimum: 66 }, analysisToken: token },
      "test-only-secret",
    ),
    false,
  );
});
test("two separate Responses calls, minimized context, no state storage, review gate", async () => {
  const original = globalThis.fetch;
  const requests = [];
  globalThis.fetch = async (_url, options) => {
    const body = JSON.parse(options.body);
    requests.push(body);
    return Response.json({
      status: "completed",
      output: [
        {
          content: [
            {
              type: "output_text",
              text: JSON.stringify(
                requests.length === 1 ? valid() : { passed: true, issues: [] },
              ),
            },
          ],
        },
      ],
    });
  };
  try {
    const result = await interpret(
      context,
      "test-key-never-sent",
      "test-model",
    );
    assert.equal(result.status, "ai");
    assert.equal(requests.length, 2);
    assert.ok(requests.every((request) => request.store === false));
    assert.equal(requests[0].text.format.type, "json_schema");
    assert.notEqual(requests[0].instructions, requests[1].instructions);
    assert.equal(JSON.stringify(requests).includes("GPS"), false);
  } finally {
    globalThis.fetch = original;
  }
});
test("rejected independent AI review never releases a draft", async () => {
  const original = globalThis.fetch;
  let count = 0;
  globalThis.fetch = async () =>
    Response.json({
      status: "completed",
      output: [
        {
          content: [
            {
              type: "output_text",
              text: JSON.stringify(
                ++count === 1
                  ? valid()
                  : { passed: false, issues: ["unsupported"] },
              ),
            },
          ],
        },
      ],
    });
  try {
    await assert.rejects(
      interpret(context, "test-key", "test-model"),
      /review_rejected/,
    );
  } finally {
    globalThis.fetch = original;
  }
});
test("provider outage cannot return invented interpretation", async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async () => new Response("unavailable", { status: 503 });
  try {
    await assert.rejects(
      interpret(context, "test-key", "test-model"),
      /provider_unavailable/,
    );
  } finally {
    globalThis.fetch = original;
  }
});

test("invalid evidence gets one bounded correction and a separate review", async () => {
  const original = globalThis.fetch;
  let count = 0;
  const bad = valid();
  bad.claims[0].factIds = ["m.pace"];
  globalThis.fetch = async () =>
    Response.json({
      status: "completed",
      output: [
        {
          content: [
            {
              type: "output_text",
              text: JSON.stringify(
                ++count === 1
                  ? bad
                  : count === 2
                    ? valid()
                    : { passed: true, issues: [] },
              ),
            },
          ],
        },
      ],
    });
  try {
    const result = await interpret(context, "test-key", "test-model");
    assert.equal(result.status, "ai");
    assert.equal(count, 3);
  } finally {
    globalThis.fetch = original;
  }
});
test("repeated invalid evidence is rejected without unbounded retry or review", async () => {
  const original = globalThis.fetch;
  let count = 0;
  const bad = valid();
  bad.claims[0].factIds = ["invented"];
  globalThis.fetch = async () => {
    count++;
    return Response.json({
      status: "completed",
      output: [
        { content: [{ type: "output_text", text: JSON.stringify(bad) }] },
      ],
    });
  };
  try {
    await assert.rejects(
      interpret(context, "test-key", "test-model"),
      /analysis_rejected/,
    );
    assert.equal(count, 2);
  } finally {
    globalThis.fetch = original;
  }
});

test("higher glucose endpoints cannot establish that every reading stayed above threshold", () => {
  const a = valid();
  a.claims[0] = {
    text: "Odczyty glukozy zarejestrowane przez sensor w oknie utrzymywały się powyżej progu.",
    factIds: ["m.glucose.minimum"],
  };
  assert.equal(validateAnalysis(a, context), false);
  a.claims[0].text = "W oknie nie odnotowano niskich odczytów glukozy.";
  assert.equal(validateAnalysis(a, context), false);
});
