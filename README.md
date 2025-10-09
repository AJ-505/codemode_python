# Code Mode Benchmark

A comparative benchmark testing Cloudflare's Code Mode approach vs traditional LLM tool calling using **realistic business scenarios with state validation**.

## Overview

This project implements two agent architectures:
1. **Regular Agent**: Traditional LLM with function/tool calling
2. **Code Mode Agent**: LLM generates Python code that calls tools

Both agents use the same API interface and tools to enable fair comparison.

### Supported Models

- **Claude (Anthropic)**: Claude 3.5 Sonnet
- **Gemini (Google)**: Gemini 1.5 Pro

Both models support both agent modes (regular and code mode).

### Key Features

- **Stateful Operations**: Tools maintain state (transactions, invoices, account balances)
- **Realistic Scenarios**: 8 business scenarios from simple expenses to quarter-end reports
- **Automatic Validation**: Each scenario validates the final state against expected outcomes
- **Comprehensive Metrics**: Track execution time, token usage, iterations, and correctness

## Project Structure

```
codemode_benchmark/
├── agents/
│   ├── regular_agent.py      # Traditional tool calling agent
│   └── codemode_agent.py     # Code Mode agent
├── tools/
│   ├── __init__.py
│   ├── accounting_tools.py   # Stateful business tools
│   ├── business_tools.py     # Tool registry and schemas
│   └── example_tools.py      # (Legacy) Simple tools
├── sandbox/
│   └── executor.py           # Safe code execution environment
├── test_scenarios.py         # Business scenarios with validation
├── benchmark.py              # Benchmark runner
├── Makefile                  # Convenient commands
├── requirements.txt
└── README.md
```

## Installation

### Quick Start
```bash
make setup                  # Create venv, install deps, create .env
source venv/bin/activate   # Activate virtual environment
# Edit .env to add your API key (ANTHROPIC_API_KEY or GOOGLE_API_KEY)
```

### Manual Installation
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add your API key(s):
# - ANTHROPIC_API_KEY for Claude
# - GOOGLE_API_KEY for Gemini
```

## Usage

### Run Benchmark

```bash
# Run full benchmark (all 8 scenarios)
make run                         # Uses Claude by default

# Run with Gemini
python benchmark.py --model gemini

# Run quick test (first 2 scenarios)
make run-quick

# Run specific scenario
make run-scenario SCENARIO=1

# With Python directly
python benchmark.py                      # All scenarios (Claude)
python benchmark.py --limit 2            # First 2 scenarios
python benchmark.py --scenario 3         # Scenario 3 only
python benchmark.py --model gemini       # Use Gemini instead
python benchmark.py --model gemini --limit 2  # Gemini, 2 scenarios
```

### Test Individual Components

```bash
# Test sandbox executor
make test-sandbox

# Test regular agent
make test-regular

# Test code mode agent
make test-codemode

# Run all tests
make test
```

### Other Commands

```bash
make help           # Show all available commands
make clean          # Clean cache files
make show-results   # Display last benchmark results
```

## Test Scenarios

The benchmark includes 8 realistic business scenarios:

1. **Monthly Expense Recording** - Record multiple expense categories
2. **Client Invoicing Workflow** - Create and manage invoices
3. **Payment Processing** - Handle partial and full payments
4. **Mixed Income/Expense Tracking** - Complex cash flow analysis
5. **Multi-Account Fund Management** - Transfer between accounts
6. **Quarter-End Financial Analysis** - Comprehensive reporting
7. **Multi-Client Invoice Management** - Complex invoice workflows
8. **Budget Tracking** - Category-based expense analysis

Each scenario:
- Performs multiple stateful operations
- Validates the final state (balances, counts, totals)
- Measures correctness, speed, and token usage

## Sample Output

```
Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses...
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
```
