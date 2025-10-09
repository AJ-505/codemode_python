# Code Mode Benchmark - Project Summary

## What This Project Does

This benchmark tests **Cloudflare's Code Mode approach** (where LLMs write code to call tools) against **traditional function calling** (where LLMs directly invoke tools via API) using realistic business scenarios.

### The Key Innovation

Instead of simple toy examples, this benchmark uses:

1. **Stateful Tools**: Real business operations that modify state (create transactions, manage invoices, transfer money)
2. **Complex Scenarios**: Multi-step workflows like "process quarterly financials" or "manage client invoices"
3. **Automatic Validation**: Each scenario validates the final state to ensure correctness, not just plausible-sounding output

## Architecture

### Two Agent Types

#### Regular Agent (Traditional Approach)
- LLM uses Claude's native tool calling
- Each tool call is a separate API request/response cycle
- LLM → Tool Call → Execute → Return → LLM → Next Tool Call...

#### Code Mode Agent (New Approach)
- LLM writes Python code that calls tools
- Code executes in a sandbox with access to all tools
- LLM → Generate Code → Execute All Operations → Return Final Result
- Can chain operations, use loops, variables, error handling naturally

### Shared Components

Both agents use:
- **Same tools**: 11 business/accounting tools
- **Same state**: Shared AccountingState that tracks everything
- **Same scenarios**: 8 realistic business workflows
- **Same validation**: Checks final state correctness

## The Tools

All tools maintain shared state:

**State Management:**
- 3 accounts (checking, savings, business_credit) with balances
- Transaction history (income, expense, transfer)
- Invoice tracking with status and payments

**Key Tools:**
- `create_transaction` - Record income/expenses
- `create_invoice` - Generate client invoices
- `update_invoice_status` - Manage invoice lifecycle
- `record_partial_payment` - Process payments
- `get_transactions` - Query transaction history
- `get_invoices` - Query invoices
- `get_financial_summary` - Generate reports
- `transfer_between_accounts` - Move money
- `get_account_balance` - Check balances
- `get_state_summary` - Full state snapshot
- `reset_state` - Reset for testing

## The Test Scenarios

8 realistic business scenarios with increasing complexity:

1. **Monthly Expense Recording** (Simple)
   - Record 4 expense categories
   - Validate totals and balance

2. **Client Invoicing Workflow** (Medium)
   - Create 2 invoices with line items
   - Update statuses
   - Validate invoice tracking

3. **Payment Processing** (Medium)
   - Create invoice
   - Process 2 partial payments
   - Validate payment recording

4. **Mixed Income/Expense** (Medium)
   - 3 income sources, 4 expenses
   - Generate financial summary
   - Validate net income

5. **Multi-Account Management** (Medium-High)
   - Transfers between accounts
   - Income and expenses
   - Validate all account balances

6. **Quarter-End Analysis** (High)
   - Simulate 3 months of activity
   - Multiple transactions per month
   - Create and pay invoices
   - Generate comprehensive report

7. **Multi-Client Invoices** (High)
   - 3 clients with different invoices
   - Various payment statuses
   - Track outstanding receivables

8. **Budget Category Analysis** (High)
   - 14 expenses across categories
   - Group by major categories
   - Identify top expenses

## What Gets Measured

For each scenario and agent:

### Performance Metrics
- **Execution time**: How long did it take?
- **Iterations**: How many LLM calls?
- **Token usage**: Input/output tokens

### Correctness Metrics
- **Success rate**: Did it complete without errors?
- **Validation rate**: Did the final state match expectations?
- **Check details**: Which specific validations passed/failed

### State Validation
Each scenario checks:
- Transaction counts (total, by type, by category)
- Invoice counts and statuses
- Account balances
- Total income/expenses
- Net income
- Outstanding receivables

## Expected Insights

This benchmark should reveal:

1. **Efficiency**: Does Code Mode require fewer iterations?
2. **Token Usage**: Does writing code use fewer tokens than multiple tool calls?
3. **Correctness**: Do both approaches correctly handle complex stateful operations?
4. **Complexity Handling**: Which approach handles complex multi-step scenarios better?
5. **Error Handling**: How do they handle edge cases and errors?

## Running the Benchmark

### Quick Test
```bash
make setup
source venv/bin/activate
# Add ANTHROPIC_API_KEY to .env
make run-quick  # First 2 scenarios
```

### Full Benchmark
```bash
make run  # All 8 scenarios
```

### Specific Scenario
```bash
make run-scenario SCENARIO=3
```

## Project Files

**Core Components:**
- `agents/regular_agent.py` - Traditional tool calling
- `agents/codemode_agent.py` - Code generation approach
- `tools/accounting_tools.py` - Stateful business tools
- `tools/business_tools.py` - Tool registry and schemas
- `sandbox/executor.py` - Safe code execution

**Testing:**
- `test_scenarios.py` - 8 business scenarios with validation
- `benchmark.py` - Main benchmark runner

**Documentation:**
- `README.md` - Setup and usage
- `TOOLS.md` - Complete tool reference
- `SUMMARY.md` - This file
- `Makefile` - Convenient commands

## Key Differences from Typical Benchmarks

### What This Has
✅ Stateful operations with real consequences
✅ Complex multi-step workflows
✅ Automatic correctness validation
✅ Realistic business scenarios
✅ Both approaches use same tools/state

### What This Doesn't Have
❌ Toy examples like "what's 2+2"
❌ Simple one-shot queries
❌ Manual result inspection
❌ Different tools for different agents
❌ Subjective quality assessment

## Why This Matters

Traditional benchmarks test if LLMs can call tools correctly. This benchmark tests if different architectures can **solve complex, realistic problems correctly**.

The stateful nature means:
- Wrong operations have visible consequences
- You can't fake correctness with good prose
- Final state must match mathematical expectations
- Both approaches face the same challenges

This is closer to real-world usage where:
- Operations have side effects
- Order matters
- State must be managed correctly
- Multiple operations must compose correctly

## Future Extensions

Potential additions:
- More scenario types (e.g., payroll, taxes, budgeting)
- Time-series analysis scenarios
- Error recovery scenarios
- Concurrent operation handling
- Performance under token limits
- Different LLM models comparison
- MCP integration for tool serving
