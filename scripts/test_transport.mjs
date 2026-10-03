import { test } from "node:test";
import assert from "node:assert/strict";
import { getAIConfig } from "../src/lib/server/provider-config.ts";
import {
  callStructured,
  ProviderError,
} from "../src/lib/server/llm-transport.ts";

// Deliberately fake credentials; no environment reads or real HTTP requests.
const openAIKey = "fake-openai-transport-test";
const anthropicKey = "sk-ant-fake-transport-test";
const schema = {
  type: "object",
  additionalProperties: false,
  properties: { ok: { type: "boolean" } },
  required: ["ok"],
};
const responseFor = (provider, overrides = {}) =>
  provider === "Anthropic"
    ? Response.json({
        stop_reason: "end_turn",
        content: [{ type: "text", text: '{"ok":true}' }],
        ...overrides,
      })
    : Response.json({
        status: "completed",
        output: [{ content: [{ type: "output_text", text: '{"ok":true}' }] }],
        ...overrides,
      });

async function mockedFetch(mock, action) {
  const original = globalThis.fetch;
  globalThis.fetch = mock;
  try {
    return await action();
  } finally {
    globalThis.fetch = original;
  }
}

test("explicit Anthropic key takes precedence and provider uses its own model", () => {
  const config = getAIConfig({
    ANTHROPIC_API_KEY: anthropicKey,
    OPENAI_API_KEY: openAIKey,
    ANTHROPIC_MODEL: "anthropic-test-model",
    OPENAI_MODEL: "openai-test-model",
  });
  assert.equal(config.provider, "Anthropic");
  assert.equal(config.key, anthropicKey);
  assert.equal(config.model, "anthropic-test-model");
  assert.equal(config.configured, true);
});

test("legacy Anthropic credential under OPENAI_API_KEY routes only to Anthropic", async () => {
  const config = getAIConfig({
    OPENAI_API_KEY: ` ${anthropicKey} `,
    OPENAI_MODEL: "wrong-provider-model",
  });
  assert.equal(config.provider, "Anthropic");
  assert.equal(config.model, "claude-sonnet-4-6");
  await mockedFetch(
    async (url, options) => {
      assert.equal(url, "https://api.anthropic.com/v1/messages");
      assert.equal(options.headers["x-api-key"], anthropicKey);
      assert.equal(Object.hasOwn(options.headers, "Authorization"), false);
      return responseFor("Anthropic");
    },
    () => callStructured(config, "system", {}, schema, "test"),
  );
});

test("OpenAI configuration keeps OpenAI model and default", () => {
  assert.equal(
    getAIConfig({ OPENAI_API_KEY: openAIKey }).model,
    "gpt-4.1-2025-04-14",
  );
  assert.equal(
    getAIConfig({ OPENAI_API_KEY: openAIKey, OPENAI_MODEL: "test-model" })
      .model,
    "test-model",
  );
  assert.equal(getAIConfig({ OPENAI_API_KEY: openAIKey }).provider, "OpenAI");
});

test("missing and whitespace keys do not count as configuration", async () => {
  for (const env of [{}, { OPENAI_API_KEY: "   ", ANTHROPIC_API_KEY: " " }]) {
    const config = getAIConfig(env);
    assert.equal(config.configured, false);
    await mockedFetch(
      () => assert.fail("Missing key must not trigger HTTP"),
      () =>
        assert.rejects(
          callStructured(config, "system", {}, schema, "test"),
          /provider_not_configured/,
        ),
    );
  }
});

test("OpenAI request is strict Responses JSON with store false and bounded tokens", async () => {
  const config = getAIConfig({ OPENAI_API_KEY: openAIKey });
  await mockedFetch(
    async (url, options) => {
      const body = JSON.parse(options.body);
      assert.equal(url, "https://api.openai.com/v1/responses");
      assert.equal(options.headers.Authorization, `Bearer ${openAIKey}`);
      assert.equal(Object.hasOwn(options.headers, "x-api-key"), false);
      assert.equal(body.store, false);
      assert.deepEqual(body.text.format, {
        type: "json_schema",
        name: "run",
        schema,
        strict: true,
      });
      assert.equal(body.max_output_tokens, 1800);
      assert.equal(body.instructions, "system");
      assert.equal(body.input[0].content[0].text, '{"facts":{"pace":5}}');
      assert.equal(options.cache, "no-store");
      assert.ok(options.signal instanceof AbortSignal);
      return responseFor("OpenAI");
    },
    async () =>
      assert.deepEqual(
        await callStructured(
          config,
          "system",
          { facts: { pace: 5 } },
          schema,
          "run",
        ),
        { ok: true },
      ),
  );
});

test("Anthropic uses Messages schema with correct headers and no OpenAI-only fields", async () => {
  const config = getAIConfig({ ANTHROPIC_API_KEY: anthropicKey });
  await mockedFetch(
    async (url, options) => {
      const body = JSON.parse(options.body);
      assert.equal(url, "https://api.anthropic.com/v1/messages");
      assert.equal(options.headers["anthropic-version"], "2023-06-01");
      assert.equal(options.headers["x-api-key"], anthropicKey);
      assert.equal(Object.hasOwn(options.headers, "Authorization"), false);
      assert.deepEqual(body.output_config, {
        format: { type: "json_schema", schema },
      });
      assert.equal(body.max_tokens, 1800);
      assert.equal(body.system, "system");
      assert.deepEqual(body.messages, [
        { role: "user", content: '{"facts":{"pace":5}}' },
      ]);
      for (const field of [
        "store",
        "instructions",
        "input",
        "max_output_tokens",
        "text",
      ])
        assert.equal(Object.hasOwn(body, field), false);
      return responseFor("Anthropic");
    },
    async () =>
      assert.deepEqual(
        await callStructured(
          config,
          "system",
          { facts: { pace: 5 } },
          schema,
          "run",
        ),
        { ok: true },
      ),
  );
});

test("transport rejects a manually mismatched Anthropic key before OpenAI HTTP", async () => {
  await mockedFetch(
    () => assert.fail("Mismatched secret must not be forwarded"),
    () =>
      assert.rejects(
        callStructured(
          {
            provider: "OpenAI",
            key: anthropicKey,
            model: "test",
            configured: true,
          },
          "system",
          {},
          schema,
          "test",
        ),
        /provider_config_invalid/,
      ),
  );
});

test("provider incomplete and refusal outputs cannot pass as structured results", async () => {
  const cases = [
    ["Anthropic", { stop_reason: "max_tokens" }, "provider_incomplete"],
    ["Anthropic", { stop_reason: "tool_use" }, "provider_incomplete"],
    ["Anthropic", { stop_reason: "refusal" }, "provider_refusal"],
    [
      "Anthropic",
      { content: [{ type: "refusal", text: "refused" }] },
      "provider_refusal",
    ],
    ["OpenAI", { status: "incomplete" }, "provider_incomplete"],
    [
      "OpenAI",
      { output: [{ content: [{ type: "refusal", refusal: "refused" }] }] },
      "provider_refusal",
    ],
  ];
  for (const [provider, override, code] of cases) {
    const config = getAIConfig(
      provider === "Anthropic"
        ? { ANTHROPIC_API_KEY: anthropicKey }
        : { OPENAI_API_KEY: openAIKey },
    );
    await mockedFetch(
      async () => responseFor(provider, override),
      () =>
        assert.rejects(
          callStructured(config, "system", {}, schema, "test"),
          new RegExp(code),
        ),
    );
  }
});

test("HTTP errors retain safe status but never raw provider body or credential", async () => {
  const config = getAIConfig({ ANTHROPIC_API_KEY: anthropicKey });
  await mockedFetch(
    async () =>
      new Response(`secret ${anthropicKey} patient-information`, {
        status: 401,
      }),
    async () => {
      await assert.rejects(
        callStructured(config, "system", {}, schema, "test"),
        (error) => {
          assert.ok(error instanceof ProviderError);
          assert.equal(error.code, "provider_unavailable");
          assert.equal(error.status, 401);
          assert.equal(error.provider, "Anthropic");
          const exposed = String(error) + JSON.stringify(error);
          assert.equal(exposed.includes(anthropicKey), false);
          assert.equal(exposed.includes("patient-information"), false);
          assert.equal(Object.hasOwn(error, "cause"), false);
          return true;
        },
      );
    },
  );
});

test("network exceptions and malformed provider JSON have safe errors", async () => {
  const config = getAIConfig({ OPENAI_API_KEY: openAIKey });
  await mockedFetch(
    async () => {
      throw new Error(`secret ${openAIKey}`);
    },
    () =>
      assert.rejects(
        callStructured(config, "system", {}, schema, "test"),
        (error) =>
          error.code === "provider_unavailable" &&
          !String(error).includes(openAIKey),
      ),
  );
  await mockedFetch(
    async () => new Response("private invalid payload"),
    () =>
      assert.rejects(
        callStructured(config, "system", {}, schema, "test"),
        /provider_invalid_response/,
      ),
  );
  await mockedFetch(
    async () =>
      responseFor("OpenAI", {
        output: [
          { content: [{ type: "output_text", text: "private not JSON" }] },
        ],
      }),
    () =>
      assert.rejects(
        callStructured(config, "system", {}, schema, "test"),
        /provider_invalid_json/,
      ),
  );
});
