# Changelog

## Version 2.0 - Multi-Model Support (Current)

### Added
- **Gemini Support**: Full support for Google's Gemini model
  - `agents/gemini_regular_agent.py` - Gemini with traditional function calling
  - `agents/gemini_codemode_agent.py` - Gemini with Code Mode
  - Automatic schema conversion from Anthropic to Gemini format

- **Agent Factory**: Unified interface for creating agents
  - `agents/agent_factory.py` - Factory pattern for agent creation
  - Easy model switching via command line
  - Supports both Claude and Gemini

- **Enhanced Benchmark**:
  - `--model` flag to choose between Claude and Gemini
  - Model-specific result files (`benchmark_results_claude.json`, `benchmark_results_gemini.json`)
  - Model name displayed in benchmark output

- **New Makefile Targets**:
  - `make run-gemini` - Run full benchmark with Gemini
  - `make run-gemini-quick` - Quick test with Gemini

- **Documentation**:
  - `GEMINI.md` - Complete Gemini setup guide
  - Updated `README.md` with multi-model instructions
  - Updated `QUICKSTART.md` with Gemini examples

### Changed
- `requirements.txt` - Added `google-generativeai>=0.3.0`
- `.env.example` - Added `GOOGLE_API_KEY` example
- `agents/__init__.py` - Exports new Gemini agents and factory
- `benchmark.py` - Refactored to use AgentFactory
- Makefile `check-env` - Now checks for either API key

### Technical Details
- Both models use the same sandbox executor
- Both models use the same stateful tools
- Schema conversion happens automatically for Gemini
- Token counting may differ between models
- Results are isolated by model name

## Version 1.0 - Stateful Tools with Validation

### Added
- **Stateful Business Tools**: 11 accounting/business tools
  - `tools/accounting_tools.py` - State management with AccountingState
  - `tools/business_tools.py` - Tool registry and schemas
  - Shared state across tool calls within scenarios

- **8 Realistic Business Scenarios**:
  1. Monthly Expense Recording
  2. Client Invoicing Workflow
  3. Payment Processing
  4. Mixed Income/Expense Tracking
  5. Multi-Account Fund Management
  6. Quarter-End Financial Analysis
  7. Multi-Client Invoice Management
  8. Budget Tracking

- **Automatic State Validation**:
  - `test_scenarios.py` - Scenario definitions with expected outcomes
  - Validates transaction counts, balances, invoice statuses
  - Shows ✓ PASS / ✗ FAIL for each scenario

- **Enhanced Agents**:
  - `agents/regular_agent.py` - Claude with traditional function calling
  - `agents/codemode_agent.py` - Claude with Code Mode
  - Both agents reset state before each test

- **Comprehensive Documentation**:
  - `TOOLS.md` - Complete tool reference
  - `SUMMARY.md` - Project architecture and design
  - `QUICKSTART.md` - 5-minute getting started guide

- **Makefile**:
  - `make setup` - One-command setup
  - `make run-quick` - Quick 2-scenario test
  - `make run-scenario SCENARIO=<id>` - Run specific scenario
  - `make test-*` - Test individual components

### Changed
- Replaced simple example tools with stateful business tools
- Added state tracking for all operations
- Added validation framework for correctness checking
- Enhanced benchmark output with validation results

### Technical Details
- Uses RestrictedPython for safe code execution
- State persists during scenario, resets between scenarios
- Validation checks mathematical correctness of final state
- Tools return JSON strings that must be parsed

## Version 0.1 - Initial Release

### Added
- Basic benchmark structure
- Claude agent with traditional function calling
- Claude agent with Code Mode
- Simple example tools (weather, calculator, etc.)
- Basic benchmark runner
- README and requirements.txt

### Features
- Compare regular vs code mode approaches
- Track execution time and token usage
- Simple tool calling examples

---

## Migration Notes

### From v1.0 to v2.0

No breaking changes. To use Gemini:

1. Install new dependency: `pip install google-generativeai>=0.3.0`
2. Add `GOOGLE_API_KEY` to `.env`
3. Run with `--model gemini` flag

Existing Claude workflows remain unchanged.

### From v0.1 to v1.0

**Breaking changes:**
- Tool interface changed from simple functions to stateful operations
- Benchmark now expects scenarios instead of simple queries
- Results format includes validation data

**Migration:**
- Update any custom tools to return JSON strings
- Rewrite test queries as full scenarios
- Update result processing to handle validation data

---

## Roadmap

### Planned Features
- **More Models**: GPT-4, Claude 3 Opus, etc.
- **Model Comparison**: Run same scenarios across all models
- **More Scenarios**: Payroll, taxes, budgeting, time-series
- **Error Recovery**: Test how agents handle failures
- **MCP Integration**: Use Model Context Protocol for tool serving
- **Visualization**: Charts comparing model performance
- **Web UI**: Interactive benchmark results viewer

### Ideas for Contribution
- Add support for your favorite LLM
- Create industry-specific scenario sets
- Add more sophisticated validation rules
- Build analysis tools for results
- Create comparison dashboards

---

## Contributing

To add support for a new model:

1. Create `agents/yourmodel_regular_agent.py`
2. Create `agents/yourmodel_codemode_agent.py`
3. Update `agents/agent_factory.py` to register the model
4. Update `benchmark.py` to handle the API key
5. Add documentation in `YOUR_MODEL.md`
6. Update `README.md` and `QUICKSTART.md`
7. Test with `python agents/agent_factory.py`

See `GEMINI.md` for a complete example of model integration.
