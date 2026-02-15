# Code Mode Benchmark

> **"LLMs are better at writing code to call tools than at calling tools directly."**
> — [Cloudflare Code Mode Research](https://blog.cloudflare.com/code-mode/)

A comprehensive benchmark comparing **Code Mode** (code generation) vs **Traditional Function Calling** for LLM tool interactions. Demonstrates that Code Mode achieves **60% faster execution**, **68% fewer tokens**, and **88% fewer API round trips** while maintaining equal accuracy.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Key Results

| Metric | Regular Agent | Code Mode | Improvement |
|--------|---------------|-----------|-------------|
| **Average Latency** | 11.88s | 4.71s | **60.4% faster** ⚡ |
| **API Round Trips** | 8.0 iterations | 1.0 iteration | **87.5% reduction** 🔄 |
| **Token Usage** | 144,250 tokens | 45,741 tokens | **68.3% savings** 💰 |
| **Success Rate** | 6/8 (75%) | 7/8 (88%) | **+13% higher** ✅ |
| **Validation Accuracy** | 100% | 100% | **Equal accuracy** |

**Annual Cost Savings**: $9,536/year at 1,000 scenarios/day (Claude Haiku pricing)

📊 [View Full Results](docs/BENCHMARK_SUMMARY.md) | 📈 [Raw Data Tables](docs/RESULTS_DATA.md)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- API key(s) for the model(s) you want to run:
  - `ANTHROPIC_API_KEY` (Claude / Opus)
  - `OPENAI_API_KEY` (GPT-5.2)
  - `ZHIPU_API_KEY` (GLM-5)
  - `GOOGLE_API_KEY` (Gemini)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd codemode_benchmark

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Run the Benchmark

```bash
# Run full benchmark with Claude
make run

# Run with Gemini
python benchmark.py --model gemini

# Run with latest Anthropic model
python benchmark.py --model opus_4_6

# Run with GPT-5.2
python benchmark.py --model gpt_5_2

# Run with GLM-5
python benchmark.py --model glm_5

# Run with Gemini 3 Pro
python benchmark.py --model gemini_3_pro

# Run the full latest-model suite in one command
python benchmark.py --run-latest

# Run specific scenario
python benchmark.py --scenario 1

# Run limited scenarios
python benchmark.py --limit 3

# Run benchmark + sandbox security eval
python benchmark.py --model gpt_5_2 --security-eval
```

---

## 📁 Repository Structure

```
codemode_benchmark/
├── README.md                 # This file
├── benchmark.py             # Main benchmark runner
├── requirements.txt         # Python dependencies
├── Makefile                 # Convenient commands
│
├── agents/                  # Agent implementations
│   ├── __init__.py
│   ├── codemode_agent.py           # Code Mode (code generation)
│   ├── regular_agent.py            # Traditional function calling
│   ├── gemini_codemode_agent.py    # Gemini Code Mode
│   ├── gemini_regular_agent.py     # Gemini function calling
│   ├── openai_compatible_codemode_agent.py
│   └── openai_compatible_regular_agent.py
│
├── tools/                   # Tool definitions
│   ├── __init__.py
│   ├── business_tools.py           # Accounting/invoicing tools
│   ├── accounting_tools.py         # Core accounting logic
│   ├── example_tools.py            # Simple example tools
│   └── mcp_adapter.py              # MCP -> Code Mode compatibility helpers
│
├── sandbox/                 # Secure code execution
│   ├── __init__.py
│   └── executor.py                 # RestrictedPython sandbox
│
├── tests/                   # Test files
│   ├── test_api.py
│   ├── test_scenarios.py           # Scenario definitions
│   └── ...
│
├── debug/                   # Debug scripts (development)
│   └── debug_*.py
│
├── docs/                    # Documentation
│   ├── BENCHMARK_SUMMARY.md        # Comprehensive analysis
│   ├── RESULTS_DATA.md             # Raw data tables
│   ├── QUICKSTART.md               # Quick start guide
│   ├── TOOLS.md                    # Tool API documentation
│   ├── CHANGELOG.md                # Version history
│   └── GEMINI.md                   # Gemini-specific notes
│
└── results/                 # Benchmark results
    ├── benchmark_results_claude.json
    ├── benchmark_results_gemini.json
    ├── results.log
    └── results-gemini.log
```

---

## 🔬 What is Code Mode?

### Traditional Function Calling (Regular Agent)

```
User Query → LLM → Tool Call #1 → Execute → Result
          ↓
       LLM processes result → Tool Call #2 → Execute → Result
          ↓
       [Repeat 5-16 times...]
          ↓
       Final Response
```

**Problems:**
- Multiple API round trips
- Neural network processing between each tool call
- Context grows with each iteration
- High latency and token costs

### Code Mode

```
User Query → LLM generates complete code → Executes all tools → Final Response
```

**Advantages:**
- Single code generation pass
- Batch multiple operations
- No context re-processing
- Natural programming constructs (loops, variables, conditionals)

**Example:**

Regular Agent sees this as 3 separate tool calls:
```json
{"name": "create_transaction", "input": {"amount": 2500, ...}}
{"name": "create_transaction", "input": {"amount": 150, ...}}
{"name": "get_financial_summary", "input": {}}
```

Code Mode generates efficient code:
```python
expenses = [
    ("rent", 2500, "Monthly rent"),
    ("utilities", 150, "Electricity")
]
for category, amount, desc in expenses:
    tools.create_transaction("expense", category, amount, desc)

summary = json.loads(tools.get_financial_summary())
result = f"Total: ${summary['summary']['total_expenses']}"
```

---

## 🎯 Test Scenarios

The benchmark includes 8 realistic business scenarios:

1. **Monthly Expense Recording** - Record 4 expenses and generate summary
2. **Client Invoicing Workflow** - Create 2 invoices, update status, summarize
3. **Payment Processing** - Create invoice, process partial payments
4. **Mixed Income/Expense Tracking** - 7 transactions with financial analysis
5. **Multi-Account Management** - Complex transfers between 3 accounts
6. **Quarter-End Analysis** - Simulate 3 months of business activity
7. **Complex Multi-Client Invoicing** - 3 invoices with partial payments (16 operations)
8. **Budget Tracking** - 14 categorized expenses with analysis

Each scenario includes automated validation to ensure correctness.

---

## 🛠️ Implementation Details

### Code Mode Architecture

```python
class CodeModeAgent:
    def run(self, user_message: str) -> Dict[str, Any]:
        # 1. Send message with tools API documentation
        response = self.client.messages.create(
            system=self._create_system_prompt(),  # Contains tools API
            messages=[{"role": "user", "content": user_message}]
        )

        # 2. Extract generated code
        code = extract_code_from_response(response)

        # 3. Execute in sandbox
        result = self.executor.execute(code)

        return result
```

### Tools API with TypedDict

```python
from typing import TypedDict, Literal

class TransactionResponse(TypedDict):
    status: Literal["success"]
    transaction: TransactionDict
    new_balance: float

def create_transaction(
    transaction_type: Literal["income", "expense", "transfer"],
    category: str,
    amount: float,
    description: str,
    account: str = "checking"
) -> str:
    """
    Create a new transaction.

    Returns: JSON string with TransactionResponse structure

    Example:
        result = tools.create_transaction("expense", "rent", 2500.0, "Monthly rent")
        data = json.loads(result)
        print(data["new_balance"])  # 7500.0
    """
    # Implementation...
```

### Security with RestrictedPython

Code execution uses RestrictedPython with additional hard-wrap controls:
- Import allow-list (blocks `os`, `socket`, `subprocess`, etc.)
- Timeout guard to stop runaway loops
- Best-effort memory limits
- Tool-call interception log for sandbox auditing
- Built-in jailbreak/security evaluation scenarios (`--security-eval`)

---

## 📊 Performance Breakdown

### By Scenario Complexity

| Complexity | Scenarios | Avg Speedup | Avg Token Savings |
|------------|-----------|-------------|-------------------|
| **High** (10+ ops) | 2 | 79.2% | 36,389 tokens |
| **Medium** (5-9 ops) | 3 | 47.5% | 8,774 tokens |
| **Low** (3-4 ops) | 1 | 45.3% | 6,209 tokens |

**Key Insight:** Code Mode advantage scales with complexity, but even simple tasks benefit significantly.

### Cost Analysis at Scale

| Daily Volume | Regular Annual | Code Mode Annual | Annual Savings |
|--------------|----------------|------------------|----------------|
| 100 | $252 | $77 | $175 |
| 1,000 | $2,519 | $766 | $1,753 |
| 10,000 | $25,185 | $7,665 | **$17,520** |
| 100,000 | $251,850 | $76,650 | **$175,200** |

*(Based on Claude Haiku pricing: $0.25/1M input, $1.25/1M output)*

---

## 🤖 Supported Models

- `claude` (Claude 3 Haiku)
- `gemini` (Gemini 2.0 Flash)
- `opus_4_6` (Claude Opus 4.6)
- `gpt_5_2` (OpenAI GPT-5.2)
- `glm_5` (ZhipuAI GLM-5 via OpenAI-compatible endpoint)
- `gemini_3_pro` (Gemini 3 Pro via Google OpenAI-compatible endpoint)

---

## 🧪 Running Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_scenarios.py

# Test Code Mode agent directly
python agents/codemode_agent.py

# Test Regular Agent directly
python agents/regular_agent.py

# Test sandbox execution
python sandbox/executor.py
```

---

## 📚 Documentation

- **[Benchmark Summary](docs/BENCHMARK_SUMMARY.md)** - Comprehensive analysis with insights
- **[Results Data](docs/RESULTS_DATA.md)** - Raw performance tables
- **[Quick Start Guide](docs/QUICKSTART.md)** - Step-by-step setup
- **[Tools Documentation](docs/TOOLS.md)** - Available tools and API
- **[Research Extensions](docs/RESEARCH_EXTENSIONS.md)** - Proposal integrations and latest-model support
- **[Changelog](docs/CHANGELOG.md)** - Version history
- **[Gemini Notes](docs/GEMINI.md)** - Gemini-specific information

---

## 💡 Key Learnings

### Why Code Mode Wins

1. **Batching Advantage**
   - Single code block replaces multiple API calls
   - No neural network processing between operations
   - Example: 16 iterations → 1 iteration (Scenario 7)

2. **Cognitive Efficiency**
   - LLMs have extensive training on code generation
   - Natural programming constructs (loops, variables, conditionals)
   - TypedDict provides clear type contracts

3. **Computational Efficiency**
   - No context re-processing between tool calls
   - Direct code execution in sandbox
   - Reduced token overhead

### When to Use Code Mode

✅ **Multi-step workflows** - Greatest benefit with many operations
✅ **Complex business logic** - Invoicing, accounting, data processing
✅ **Batch operations** - Similar actions on multiple items
✅ **Cost-sensitive workloads** - Production at scale
✅ **Latency-critical applications** - User-facing systems

### Best Practices

1. **Use TypedDict for response types** - Provides clear structure to LLM
2. **Include examples in docstrings** - Shows correct usage patterns
3. **Batch similar operations** - Leverage loops in code
4. **Validate results** - Automated checks ensure correctness
5. **Handle errors gracefully** - Try-except in generated code

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📖 References

- [Cloudflare Code Mode Blog Post](https://blog.cloudflare.com/code-mode/)
- [Anthropic Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Claude API Documentation](https://docs.anthropic.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Gemini API Documentation](https://ai.google.dev/)
- [ZhipuAI Model API Documentation](https://docs.bigmodel.cn/)
- [RestrictedPython Documentation](https://restrictedpython.readthedocs.io/)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Inspired by [Cloudflare's Code Mode research](https://blog.cloudflare.com/code-mode/)
- Built on [Anthropic's Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) framework
- Uses [RestrictedPython](https://github.com/zopefoundation/RestrictedPython) for secure code execution

---

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

**Benchmark Date**: January 2025
**Models Tested**: See `python benchmark.py --run-latest` outputs in `results/`
**Test Scenarios**: 8 realistic business workflows
**Result**: Code Mode is 60% faster, uses 68% fewer tokens, with equal accuracy
