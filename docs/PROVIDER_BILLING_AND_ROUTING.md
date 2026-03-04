# Provider Billing and Routing Research

Last verified: **March 4, 2026 (UTC)**

## Scope

This note covers:
- GLM (Z.ai / Zhipu)
- MiniMax
- Kimi (Moonshot)
- OpenRouter

Primary goals:
- check account funding/deposit expectations
- check free-tier/free-credit posture
- decide routing strategy for this benchmark

## Findings (Current Best-Effort)

### 1) OpenRouter
- Billing model: pay-as-you-go with self-funded credits.
- No mandatory monthly commitment found.
- Platform fee and minimum recharge details are documented.
- Model IDs used in this benchmark:
  - `z-ai/glm-5`
  - `minimax/minimax-m2.5`
  - `moonshotai/kimi-k2`

Operational implication:
- Fastest onboarding path for GLM/MiniMax/Kimi in a unified OpenAI-compatible API.

### 2) GLM (Zhipu / Z.ai direct)
- Official docs show free models / promotions.
- Publicly indexed docs do not clearly expose one global minimum deposit requirement for all accounts/workloads.

Operational implication:
- Keep direct-provider support optional.
- Prefer OpenRouter default for easier onboarding unless direct key is provided.

### 3) MiniMax (direct)
- Official docs show pricing and mention free quota in onboarding.
- Public docs reviewed did not show a universally enforced minimum initial deposit value for all accounts.

Operational implication:
- Keep direct-provider support optional behind `MINIMAX_API_KEY`.
- OpenRouter default remains simpler and lower-friction.

### 4) Kimi / Moonshot (direct)
- Changelog references recharge threshold changes and voucher mechanics.
- Public docs do not cleanly present one stable universal minimum pre-deposit statement for all account states.

Operational implication:
- Keep direct-provider support optional behind `MOONSHOT_API_KEY`.
- OpenRouter default remains the predictable path.

## Architecture Decision

Chosen: **Hybrid (OpenRouter default + direct override)**.

Rules:
1. If direct provider key exists for model, use direct provider route.
2. Else use OpenRouter route.

Why:
- reduces setup complexity and time-to-first-run
- preserves direct-path comparability for latency/cost studies
- limits refactor effort because benchmark already uses OpenAI-compatible clients

## Refactor Impact Estimate

- Added complexity: low to medium.
  - Runtime provider resolution in `AgentFactory`.
  - New env var options and docs.
- Added simplicity:
  - one fallback path (`OPENROUTER_API_KEY`) for multi-provider onboarding
  - less per-provider plumbing for initial experiments

## Source Links

- OpenRouter pricing: https://openrouter.ai/pricing
- OpenRouter FAQ: https://openrouter.ai/docs/faq
- OpenRouter quickstart: https://openrouter.ai/docs/quickstart
- OpenRouter authentication: https://openrouter.ai/docs/api-reference/authentication
- OpenRouter GLM-5 page: https://openrouter.ai/z-ai/glm-5/pricing
- OpenRouter MiniMax M2.5 page: https://openrouter.ai/minimax/minimax-m2.5/pricing
- OpenRouter Moonshot/Kimi listing example: https://openrouter.ai/moonshotai/kimi-k2-thinking-20251106%3Anitro/benchmarks
- MiniMax pricing docs: https://platform.minimax.io/docs/pricing/pay-as-you-go
- MiniMax pricing page: https://www.minimax.io/pricing
- Zhipu/GLM free model docs: https://docs.bigmodel.cn/cn/guide/models/free/glm-4.5-flash
- Zhipu promotion update: https://docs.bigmodel.cn/cn/update/promotion
- Moonshot changelog: https://platform.moonshot.ai/blog/posts/changelog

## Confidence / Caveat

Provider deposit and free-credit policies are highly time-sensitive and can vary by region/account tier.
Before funding production accounts, re-check provider billing consoles directly on the same day as purchase.
