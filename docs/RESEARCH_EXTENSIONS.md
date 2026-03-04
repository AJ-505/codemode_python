# Research Extensions Implemented

This project now includes the proposal-driven additions for evaluating Code Mode vs standard tool calling.

## 1) Latest Model Support

Supported benchmark model keys:
- `opus_4_6` (Anthropic Opus 4.6)
- `sonnet_4_6` (Anthropic Sonnet 4.6)
- `gpt_5_1` (OpenAI GPT-5.1)
- `gpt_5_2` (OpenAI GPT-5.2)
- `gpt_5_3_codex` (OpenAI GPT-5.3 Codex)
- `glm_5` (ZhipuAI GLM-5 via OpenAI-compatible endpoint)
- `minimax_m2_5` (MiniMax M2.5; OpenRouter default, direct override optional)
- `kimi_2_5` (Moonshot Kimi 2.5; OpenRouter default, direct override optional)
- `gemini_3_pro` (Gemini 3 Pro via Google OpenAI-compatible endpoint)

Also kept:
- `claude`
- `gemini`

Run all latest models in one command:

```bash
python benchmark.py --run-latest
```

Include Opus 4.6 explicitly:

```bash
python benchmark.py --run-latest --include-opus
```

## 2) Hardened Sandbox Wrapper

`sandbox/executor.py` now enforces:
- Import allow-list
- Timeout guard (runaway loop protection)
- Best-effort memory cap
- Tool call interception and audit logs
- Built-in security/jailbreak checks

Run security checks:

```bash
python benchmark.py --model gpt_5_2 --security-eval --limit 1
```

## 3) MCP Backward-Compatibility Bridge

`tools/mcp_adapter.py` adds:
- MCP tools JSON -> regular agent tool schemas
- MCP tools JSON -> Code Mode API prompt definitions

Preview translated Code Mode API:

```bash
python benchmark.py --mcp-tools-file path/to/mcp_tools.json --print-translated-api
```

## 4) Expanded Benchmark Instrumentation

Benchmark outputs now include:
- Token economy proxy (`prompt_footprint`) for regular tool schemas vs Code Mode API prompts
- Reliability metrics (success + validation pass rates)
- Latency metrics
- Code Mode sandbox overhead metrics (compile/exec times)
- Optional security evaluation results

Results are written to `results/`.
