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
| `gpt_5_2` | OpenAI API | `gpt-5.2` | `OPENAI_API_KEY` |
| `glm_5` | Zhipu OpenAI-compatible | `glm-5` | `ZHIPU_API_KEY` |
| `gemini_3_pro` | Google OpenAI-compatible | `gemini-3-pro-preview` | `GOOGLE_API_KEY` |

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
GOOGLE_API_KEY=...
```

5. Smoke test one short run.
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --limit 1
```

## Primary Commands

Run single model:
```bash
.venv/bin/python benchmark.py --model claude
.venv/bin/python benchmark.py --model gemini
.venv/bin/python benchmark.py --model opus_4_6
.venv/bin/python benchmark.py --model gpt_5_2
.venv/bin/python benchmark.py --model glm_5
.venv/bin/python benchmark.py --model gemini_3_pro
```

Run latest suite (all configured latest keys):
```bash
.venv/bin/python benchmark.py --run-latest
```

Run one scenario:
```bash
.venv/bin/python benchmark.py --model gpt_5_2 --scenario 3
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

Each result file includes:
- per-scenario outcomes for `regular_agent` and `codemode_agent`
- validation stats
- token usage totals
- timing/iteration metrics
- prompt footprint estimates
- optional security evaluation section

## Repository Map

- `benchmark.py`: CLI entrypoint and orchestration
- `agents/agent_factory.py`: model registry and provider wiring
- `agents/*.py`: provider-specific regular/code-mode agents
- `sandbox/executor.py`: restricted code execution + jailbreak checks
- `tools/business_tools.py`: benchmark toolset and schemas
- `tools/mcp_adapter.py`: MCP conversion helpers
- `tests/test_scenarios.py`: scenarios and validation logic
- `docs/RESEARCH_EXTENSIONS.md`: summary of proposal-driven additions

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
make run-gpt
make run-glm
make run-gemini3
make run-latest
```

## Benchmark Design Notes

- Scenarios are stateful accounting/business workflows in `tests/test_scenarios.py`.
- Before each scenario run, state is reset.
- Results are validated against expected end-state checks.
- Code Mode agent writes Python, then sandbox executes it against tool API.

## Cost Estimation Formula

Use result token counts to estimate cost per run:

```text
cost = (input_tokens / 1_000_000) * input_rate
     + (output_tokens / 1_000_000) * output_rate
```

You can apply this to each model or across the suite by summing token totals from JSON outputs.

## Troubleshooting

Missing key error:
- confirm `.env` exists
- confirm variable name matches required env var for the model key

Model not found error:
- model access may not be enabled on your account yet
- keep model key but update model ID in `agents/agent_factory.py` if provider changed naming

Rate limits:
- use `--limit 1` or `--limit 2` for debugging
- space runs out over time

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

