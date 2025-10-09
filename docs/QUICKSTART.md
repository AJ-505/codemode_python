# Quick Start Guide

Get the benchmark running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- API key for at least one model:
  - **Claude**: Get at https://console.anthropic.com/
  - **Gemini**: Get at https://makersuite.google.com/app/apikey

## Setup (1 minute)

```bash
cd codemode_benchmark
make setup
```

This will:
1. Create a virtual environment
2. Install all dependencies
3. Create a `.env` file

## Configure (30 seconds)

```bash
# Activate virtual environment
source venv/bin/activate

# Edit .env and add your API key(s)
# Open .env in your editor and set:
# For Claude:
# ANTHROPIC_API_KEY=sk-ant-xxxxx
# For Gemini:
# GOOGLE_API_KEY=your-key-here
```

Or use one-liners:
```bash
# For Claude
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

# For Gemini
echo "GOOGLE_API_KEY=your-key-here" > .env

# For both (recommended)
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env
echo "GOOGLE_API_KEY=your-key-here" >> .env
```

## Run Quick Test (2-3 minutes)

```bash
# With Claude (default)
make run-quick

# With Gemini
make run-gemini-quick
```

This runs the first 2 scenarios to verify everything works.

## Run Full Benchmark (15-20 minutes)

```bash
# With Claude (default)
make run

# With Gemini
make run-gemini

# Or with Python directly
python benchmark.py --model claude
python benchmark.py --model gemini
```

This runs all 8 scenarios and generates a complete comparison.

## What You'll See

```
================================================================================
BENCHMARK: Regular Agent vs Code Mode Agent
================================================================================

Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses and generate a summary
Query: Record the following monthly expenses:...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 12.34s
  Iterations: 5
  Input tokens: 2500
  Output tokens: 450
  Validation: ✓ PASS (4/4 checks)

Running Code Mode Agent...
  Time: 8.76s
  Iterations: 2
  Input tokens: 2200
  Output tokens: 380
  Validation: ✓ PASS (4/4 checks)
================================================================================

... (more scenarios) ...

================================================================================
SUMMARY
================================================================================

Regular Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 11.23s
  Avg Iterations: 4.5
  Total Input Tokens: 20000
  Total Output Tokens: 3600

Code Mode Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 7.89s
  Avg Iterations: 2.1
  Total Input Tokens: 17600
  Total Output Tokens: 3040

Comparison:
  Code Mode is -29.7% vs Regular in execution time
  Token difference: -2960 (Code Mode vs Regular)
```

## View Results

```bash
# Show summary in terminal
make show-results

# Or open the full JSON
cat benchmark_results.json | python -m json.tool
```

## Run Specific Scenarios

```bash
# Run scenario 1 only (Claude)
make run-scenario SCENARIO=1

# Run scenario 3 with Gemini
python benchmark.py --model gemini --scenario 3
```

## Test Individual Components

```bash
# Test the sandbox
make test-sandbox

# Test regular agent
make test-regular

# Test code mode agent
make test-codemode
```

## Common Issues

### "API key not configured"
- Make sure `.env` file exists
- For Claude: Verify key starts with `sk-ant-`
- For Gemini: Verify you have a valid Google API key
- Check there are no extra spaces or quotes
- Make sure the key matches the model you're trying to use

### "ModuleNotFoundError"
- Activate the virtual environment: `source venv/bin/activate`
- Or reinstall dependencies: `make install`

### "Rate limit exceeded"
- You may need to wait a few seconds between runs
- Or use `--limit 1` to run one scenario at a time

### Validation failures
- This is expected sometimes - it means the agent didn't perform operations correctly
- Check the error details in the output
- Look at `benchmark_results.json` for full details

## Next Steps

1. **Read the scenarios**: Check `test_scenarios.py` to see what each test does
2. **Explore the tools**: Read `TOOLS.md` for complete tool reference
3. **Understand the project**: Read `SUMMARY.md` for architecture details
4. **Customize**: Add your own scenarios or tools
5. **Analyze**: Compare results between agents

## Quick Commands Reference

```bash
make help                # Show all commands
make setup               # Initial setup
make run                 # Full benchmark (Claude)
make run-quick           # Quick test (Claude, 2 scenarios)
make run-gemini          # Full benchmark (Gemini)
make run-gemini-quick    # Quick test (Gemini, 2 scenarios)
make run-scenario        # Run specific scenario (SCENARIO=<id>)
make test                # Test all components
make clean               # Clean cache files
make show-results        # Display last results
```

**Python Direct Commands:**
```bash
python benchmark.py                        # Claude, all scenarios
python benchmark.py --model gemini         # Gemini, all scenarios
python benchmark.py --limit 2              # Claude, 2 scenarios
python benchmark.py --model gemini --limit 2  # Gemini, 2 scenarios
python benchmark.py --scenario 3           # Claude, scenario 3
python benchmark.py --model gemini --scenario 3  # Gemini, scenario 3
```

## Troubleshooting

If something goes wrong:

1. Check you're in the virtual environment: `which python` should show the venv path
2. Verify dependencies: `pip list | grep -E "(anthropic|RestrictedPython)"`
3. Test API key: `python -c "import anthropic; print('OK')"`
4. Reset everything: `make clean-all && make setup`

## Getting Help

- Read `README.md` for detailed documentation
- Check `GEMINI.md` for Gemini-specific setup
- Check `TOOLS.md` for tool reference
- Review `SUMMARY.md` for architecture overview
- Look at `test_scenarios.py` for scenario details

## Success!

If you see validation passing and summary statistics, you're all set! 🎉

The benchmark is comparing how well each agent handles complex, stateful business operations.
