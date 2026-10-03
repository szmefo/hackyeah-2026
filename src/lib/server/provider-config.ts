// Server configuration only. Never import this module into client components.
export type AIProvider = "OpenAI" | "Anthropic";
export type AIConfig = {
  provider: AIProvider;
  key: string;
  model: string;
  configured: boolean;
};

export function getAIConfig(
  env: Record<string, string | undefined> = process.env,
): AIConfig {
  const anthropicKey = env.ANTHROPIC_API_KEY?.trim() ?? "";
  const legacyKey = env.OPENAI_API_KEY?.trim() ?? "";
  // The owner may have stored an Anthropic credential under the old variable.
  // Its prefix must determine the destination; never forward it to OpenAI.
  const provider =
    anthropicKey || legacyKey.startsWith("sk-ant-") ? "Anthropic" : "OpenAI";
  const key = anthropicKey || legacyKey;
  const model =
    provider === "Anthropic"
      ? env.ANTHROPIC_MODEL?.trim() || "claude-sonnet-4-6"
      : env.OPENAI_MODEL?.trim() || "gpt-4.1-2025-04-14";
  return { provider, key, model, configured: Boolean(key) };
}
