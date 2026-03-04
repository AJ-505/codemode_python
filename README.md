# Code Mode Benchmark

Benchmark framework for comparing:
- traditional tool/function calling agents
- Code Mode agents that generate code and execute it in a sandbox

This repo is set up for research workflows where you want reproducible runs across multiple model providers, validation checks, sandbox security checks, and machine-readable result files.

## What Is Included

- `regular` vs `codemode` agent comparison on business workflow scenarios
- multi-provider model support, including latest suite keys
- restricted sandbox with timeout, memory cap, import allowlist, and tool-call audit log
- MCP tool schema translation helpers for compatibility experiments
- JSON output files suitable for downstream analysis

## Supported Model Keys

| Model Key | Provider Path | Default Model ID | Required Env Var |
|---|---|---|---|
| `claude` | Anthropic native | `claude-3-haiku-20240307` | `ANTHROPIC_API_KEY` |
| `gemini` | Google native SDK | `gemini-2.0-flash-exp` | `GOOGLE_API_KEY` |
| `opus_4_6` | Anthropic native | `claude-opus-4-6` | `ANTHROPIC_API_KEY` |
| `sonnet_4_6` | Anthropic native | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` |
| `gpt_5_1` | OpenAI API | `gpt-5.1` | `OPENAI_API_KEY` |
| `gpt_5_2` | OpenAI API | `gpt-5.2` | `OPENAI_API_KEY` |
| `gpt_5_3_codex` | OpenAI API | `gpt-5.3-codex` | `OPENAI_API_KEY` |
| `glm_5` | OpenRouter default; Zhipu direct override | `z-ai/glm-5` | `OPENROUTER_API_KEY` (or `ZHIPU_API_KEY`) |
| `minimax_m2_5` | OpenRouter default; MiniMax direct override | `minimax/minimax-m2.5` | `OPENROUTER_API_KEY` (or `MINIMAX_API_KEY`) |
| `kimi_2_5` | OpenRouter default; Moonshot direct override | `moonshotai/kimi-k2` | `OPENROUTER_API_KEY` (or `MOONSHOT_API_KEY`) |
| `gemini_3_pro` | Google OpenAI-compatible | `gemini-3-pro-preview` | `GOOGLE_API_KEY` |
| `openrouter` | OpenRouter generic route | `openrouter/auto` | `OPENROUTER_API_KEY` |

## New Dev Setup

1. Clone and enter repo.
```bash
git clone <repo-url>
cd codemode_python_benchmark
```

2. Create virtualenv and install deps.
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

3. Create env file.
```bash
cp .env.example .env
```

4. Add API key(s) in `.env`.
```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
ZHIPU_API_KEY=...
OPENROUTER_API_KEY=...
MINIMAX_API_KEY=...
MOONSHOT_API_KEY=...
GOOGLE_API_KEY=...
```

5. Smoke test one short run.
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --limit 1
```

## Primary Commands

Complete implementation run (recommended):
```bash
# Runs the full latest-model suite:
# gpt_5_1 + gpt_5_2 + glm_5 + minimax_m2_5 + kimi_2_5 + gemini_3_pro
.venv/bin/python benchmark.py --run-latest

# Include Opus 4.6 only when explicitly needed
.venv/bin/python benchmark.py --run-latest --include-opus
```

To ensure it runs all latest models, set the provider keys in `.env`:
```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
ZHIPU_API_KEY=...
OPENROUTER_API_KEY=...
MINIMAX_API_KEY=...
MOONSHOT_API_KEY=...
GOOGLE_API_KEY=...
```

Run single model:
```bash
.venv/bin/python benchmark.py --model claude
.venv/bin/python benchmark.py --model gemini
.venv/bin/python benchmark.py --model opus_4_6
.venv/bin/python benchmark.py --model sonnet_4_6
.venv/bin/python benchmark.py --model gpt_5_1
.venv/bin/python benchmark.py --model gpt_5_2
.venv/bin/python benchmark.py --model gpt_5_3_codex
.venv/bin/python benchmark.py --model glm_5
.venv/bin/python benchmark.py --model minimax_m2_5
.venv/bin/python benchmark.py --model kimi_2_5
.venv/bin/python benchmark.py --model gemini_3_pro
```

Run latest suite (all configured latest keys; Opus excluded by default):
```bash
.venv/bin/python benchmark.py --run-latest
```

Include Opus 4.6 explicitly:
```bash
.venv/bin/python benchmark.py --run-latest --include-opus
```

Run one scenario:
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --scenario 3
```

Override model ID directly (useful for OpenRouter free-model tests):
```bash
.venv/bin/python benchmark.py --model openrouter --model-id openrouter/free --limit 1
```

Set a deterministic results filename:
```bash
.venv/bin/python benchmark.py --model openrouter --model-id z-ai/glm-5 --output-file benchmark_results_glm_5.json
```

Run limited set:
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --limit 2
```

Run with sandbox security evaluation:
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --security-eval --limit 1
```

Choose output directory:
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --output-dir results_local
```

## MCP Compatibility Mode

Use an MCP tools JSON file as input schemas/prompts:
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --mcp-tools-file path/to/mcp_tools.json
```

Preview translated Code Mode API and exit:
```bash
.venv/bin/python benchmark.py --mcp-tools-file path/to/mcp_tools.json --print-translated-api
```

## Output Files

- Per-model runs: `results/benchmark_results_<model>.json`
- Latest suite run: `results/benchmark_results_latest_suite_<timestamp>.json`
- Per-model codemode trace: `results/traces/<model>_codemode_trace.jsonl`
- Markdown reports: `results/reports/benchmark_report_<model>.md` (or timestamped on suite runs)
- Console transcripts: `logs/<model>.txt`

### Replay and Debug Artifacts

The codemode trace file is generated as JSONL and can be replayed/analyzed deterministically:
- each row contains scenario metadata
- `iteration_trace` includes model response text, generated code, sandbox outcome, tool calls, and state snapshots
- `observability` includes expected state/tool flow and discrepancy lists

Generate a report from any existing JSON result file:
```bash
.venv/bin/python benchmark.py --report-from-file results/benchmark_results_gpt_5_2.json
```

Each result file includes:
- per-scenario outcomes for `regular_agent` and `codemode_agent`
- codemode observability payloads with expected/actual/discrepancy rows
- validation stats
- token usage totals
- timing/iteration metrics
- prompt footprint estimates
- optional security evaluation section

## Repository Map

- `benchmark.py`: CLI entrypoint and orchestration
- `observability.py`: discrepancy analysis + trace/report generation
- `agents/agent_factory.py`: model registry and provider wiring
- `agents/*.py`: provider-specific regular/code-mode agents
- `sandbox/executor.py`: restricted code execution + jailbreak checks
- `tools/business_tools.py`: benchmark toolset and schemas
- `tools/mcp_adapter.py`: MCP conversion helpers
- `tests/test_scenarios.py`: scenarios and validation logic
- `docs/RESEARCH_EXTENSIONS.md`: summary of proposal-driven additions
- `docs/PROVIDER_BILLING_AND_ROUTING.md`: provider deposit/free-tier/routing research

## Local Validation Commands

Fast checks without provider calls:
```bash
python3 -m compileall agents sandbox tools benchmark.py
python3 tests/test_mcp_adapter_unit.py
python3 tests/test_sandbox_security.py
```

Makefile commands:
```bash
make run
make run-gemini
make run-opus
make run-sonnet
make run-gpt51
make run-gpt
make run-gpt53codex
make run-glm
make run-minimax
make run-kimi
make run-gemini3
make run-latest
make run-latest-opus
```

## Benchmark Design Notes

- Scenarios are stateful accounting/business workflows in `tests/test_scenarios.py`.
- Before each scenario run, state is reset.
- Results are validated against expected end-state checks.
- Code Mode agent writes Python, then sandbox executes it against a progressive-discovery tool filesystem API.

### Progressive Discovery (Code Mode Default)

Code Mode uses progressive discovery at runtime by default:

1. `tools.ls(path)` to list directories/tools
2. `tools.read(path)` to inspect schema/metadata
3. `tools.call(path, args)` to invoke a tool

Direct calls can still work when the tool name is already known.
This keeps prompt context smaller as tool count scales while preserving compatibility.

## Cost Estimation Formula

Use result token counts to estimate cost per run:

```text
cost = (input_tokens / 1_000_000) * input_rate
     + (output_tokens / 1_000_000) * output_rate
```

You can apply this to each model or across the suite by summing token totals from JSON outputs.

## Estimated Cost For Full `--run-latest`

Approximate estimate for one full run of:
- all 8 scenarios
- both agent types (`regular` + `codemode`)
- all latest models (`gpt_5_1`, `gpt_5_2`, `glm_5`, `minimax_m2_5`, `kimi_2_5`, `gemini_3_pro`)

Assumed token profile per model run (from current benchmark baseline):
- input: ~233,800 tokens
- output: ~10,816 tokens

Assumed rates (per 1M tokens, illustrative only):
- `gpt_5_1`: $1.25 input / $10 output
- `gpt_5_2`: $1.75 input / $14 output
- `glm_5`: $1.00 input / $3.20 output
- `minimax_m2_5`: $0.80 input / $3.20 output
- `kimi_2_5`: $2.00 input / $8.00 output
- `gemini_3_pro`: $2.00 input / $12 output

Estimated per-model cost:
- `gpt_5_1`: ~$0.40
- `gpt_5_2`: ~$0.56
- `glm_5`: ~$0.27
- `minimax_m2_5`: ~$0.22
- `kimi_2_5`: ~$0.55
- `gemini_3_pro`: ~$0.60

Estimated total for full `--run-latest`:
- **~$2.60 per complete suite run (without Opus 4.6)**

Estimated add-on for `--include-opus`:
- **+~$1.44 per complete suite run**

Notes:
- This is an estimate, not a fixed bill.
- Real cost varies with retries, provider rounding, and token-length differences by model.
- Recompute from actual `results/*.json` token totals for exact post-run accounting.

## Troubleshooting

Missing key error:
- confirm `.env` exists
- confirm variable name matches required env var for the model key

Model not found error:
- model access may not be enabled on your account yet
- keep model key but update model ID in `agents/agent_factory.py` if provider changed naming

Anthropic returns `Connection error.` or Cloudflare block:
- run a 1-scenario debug to capture provider diagnostics:
  - `.venv/bin/python benchmark.py --model sonnet_4_6 --limit 1 --output-file benchmark_results_sonnet_4_6_debug.json`
- inspect diagnostics in JSON:
  - `jq '.results.regular_agent[0].provider_diagnostics, .results.codemode_agent[0].provider_diagnostics' results/benchmark_results_sonnet_4_6_debug.json`
- if you see `network_edge: cloudflare_block` with `status_code: 403`, your egress IP is blocked upstream. Include the `cloudflare_ray_id` when contacting provider support.
- practical workaround for benchmark continuity: route Sonnet through OpenRouter:
  - `.venv/bin/python benchmark.py --model openrouter --model-id anthropic/claude-sonnet-4.6 --limit 1`

No output files:
- confirm command completed successfully
- check write permissions for `--output-dir`

Gemini SDK warning:
- `google-generativeai` is deprecated upstream; current code still supports it for `gemini`
- OpenAI-compatible Gemini path is available via `gemini_3_pro`

## References

- Cloudflare Code Mode: https://blog.cloudflare.com/code-mode/
- Anthropic code execution + MCP: https://www.anthropic.com/engineering/code-execution-with-mcp
- RestrictedPython docs: https://restrictedpython.readthedocs.io/
- OpenAI docs: https://platform.openai.com/docs
- Gemini API docs: https://ai.google.dev/
- Zhipu docs: https://docs.bigmodel.cn/
