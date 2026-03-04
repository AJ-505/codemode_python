# Benchmark Report

- Model: OpenRouter (generic OpenAI-compatible route)
- Model Key: `openrouter`
- Generated (UTC): 2026-03-04T13:18:10.797541Z

## Executive Summary

- Regular validation: 7/8 (87.5%)
- Code Mode validation: 7/8 (87.5%)
- Avg execution time: Regular `77.19s` vs Code Mode `213.53s`
- Total tokens: Regular `105037` vs Code Mode `92367`
- Code Mode iteration failures: `13`
- Code Mode tool discrepancies: `8`

## Scenario Breakdown

| Scenario | Regular (time/iter/tokens) | Code Mode (time/iter/tokens) | Validation (R/C) |
|---|---|---|---|
| 1 - Monthly Expense Recording | 33.11s / 3 / 6134 | 27.23s / 1 / 1548 | PASS (2/2 checks) / PASS (2/2 checks) |
| 2 - Client Invoicing Workflow | 55.00s / 4 / 12949 | 163.60s / 3 / 8285 | PASS (1/1 checks) / PASS (1/1 checks) |
| 3 - Payment Processing and Reconciliation | 50.97s / 5 / 16799 | 51.52s / 2 / 4475 | PASS (3/3 checks) / FAIL (1/3 checks) |
| 4 - Mixed Income and Expense Tracking | 33.77s / 3 / 10448 | 33.19s / 1 / 1874 | PASS (4/4 checks) / PASS (4/4 checks) |
| 5 - Multi-Account Fund Management | 174.55s / 2 / 6608 | 37.28s / 1 / 2208 | FAIL (0/1 checks) / PASS (1/1 checks) |
| 6 - Quarter-End Financial Analysis | 86.00s / 6 / 26299 | 539.75s / 8 / 55555 | PASS (5/5 checks) / PASS (5/5 checks) |
| 7 - Complex Multi-Client Invoice Management | 50.86s / 5 / 18991 | 826.95s / 4 / 16270 | PASS (3/3 checks) / PASS (3/3 checks) |
| 8 - Budget Tracking and Category Analysis | 89.19s / 3 / 12943 | 28.69s / 1 / 2152 | PASS (2/2 checks) / PASS (2/2 checks) |

## Code Mode Observability Highlights

| Scenario | Iteration Failures | Tool Discrepancies | Missing Expected Tools |
|---|---:|---:|---:|
| 1 - Monthly Expense Recording | 0 | 0 | 0 |
| 2 - Client Invoicing Workflow | 2 | 4 | 2 |
| 3 - Payment Processing and Reconciliation | 1 | 0 | 3 |
| 4 - Mixed Income and Expense Tracking | 0 | 0 | 0 |
| 5 - Multi-Account Fund Management | 0 | 0 | 0 |
| 6 - Quarter-End Financial Analysis | 7 | 0 | 0 |
| 7 - Complex Multi-Client Invoice Management | 3 | 4 | 0 |
| 8 - Budget Tracking and Category Analysis | 0 | 0 | 0 |

## Console Transcript

```text
================================================================================
BENCHMARK: Regular Agent vs Code Mode Agent
Model: OpenRouter (generic OpenAI-compatible route)
================================================================================

Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses and generate a summary
Query: Record the following monthly expenses:
- Rent: $2,500 to checking account
- Utilities (electricity): $150 to checking ac...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 33.11s
  Iterations: 3
  Input tokens: 5763
  Output tokens: 371
  Validation: PASS (2/2 checks)
  Error: No response choices returned by model

Running Code Mode Agent...
  Time: 27.23s
  Iterations: 1
  Input tokens: 889
  Output tokens: 659
  Sandbox: 1 runs, avg compile 5.78ms, avg exec 1.50ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (2/2 checks)

================================================================================

Scenario 2: Client Invoicing Workflow
Description: Create invoices for multiple clients and track their status
Query: Create invoices for the following clients:

1. TechStart Inc:
   - Software Development: 80 hours at $150/hour
   - Code...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 55.00s
  Iterations: 4
  Input tokens: 12120
  Output tokens: 829
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 163.60s
  Iterations: 3
  Input tokens: 5467
  Output tokens: 2818
  Sandbox: 3 runs, avg compile 4.15ms, avg exec 0.24ms
  Debug: iteration_failures=2, tool_discrepancies=4
  Validation: PASS (1/1 checks)

================================================================================

Scenario 3: Payment Processing and Reconciliation
Description: Process payments for invoices and reconcile accounts
Query: First, create an invoice for 'Acme Corp' with these items:
- Consulting Services: 50 hours at $200/hour
- Project Manage...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 50.97s
  Iterations: 5
  Input tokens: 15845
  Output tokens: 954
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 51.52s
  Iterations: 2
  Input tokens: 2652
  Output tokens: 1823
  Sandbox: 2 runs, avg compile 5.97ms, avg exec 0.70ms
  Debug: iteration_failures=1, tool_discrepancies=0
  Validation: FAIL (1/3 checks)

================================================================================

Scenario 4: Mixed Income and Expense Tracking
Description: Record various income and expense transactions and analyze cash flow
Query: Record the following transactions:

Income:
- Client payment: $5,000 from 'consulting' work
- Product sale: $1,500 from ...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 33.77s
  Iterations: 3
  Input tokens: 9702
  Output tokens: 746
  Validation: PASS (4/4 checks)

Running Code Mode Agent...
  Time: 33.19s
  Iterations: 1
  Input tokens: 937
  Output tokens: 937
  Sandbox: 1 runs, avg compile 4.67ms, avg exec 2.01ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (4/4 checks)

================================================================================

Scenario 5: Multi-Account Fund Management
Description: Transfer funds between accounts and track balances
Query: Perform the following account operations:

1. Record business income of $15,000 to checking account (category: 'contract...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 174.55s
  Iterations: 2
  Input tokens: 5883
  Output tokens: 725
  Validation: FAIL (0/1 checks)

Running Code Mode Agent...
  Time: 37.28s
  Iterations: 1
  Input tokens: 946
  Output tokens: 1262
  Sandbox: 1 runs, avg compile 10.61ms, avg exec 2.32ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (1/1 checks)

================================================================================

Scenario 6: Quarter-End Financial Analysis
Description: Create comprehensive quarterly report with all financial data
Query: Simulate a quarter's worth of business activity:

Month 1:
- Record income: $12,000 (consulting)
- Record expenses: Rent...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 86.00s
  Iterations: 6
  Input tokens: 24328
  Output tokens: 1971
  Validation: PASS (5/5 checks)

Running Code Mode Agent...
  Time: 539.75s
  Iterations: 8
  Input tokens: 41720
  Output tokens: 13835
  Sandbox: 8 runs, avg compile 17.19ms, avg exec 5.57ms
  Debug: iteration_failures=7, tool_discrepancies=0
  Validation: PASS (5/5 checks)

================================================================================

Scenario 7: Complex Multi-Client Invoice Management
Description: Manage multiple invoices with various statuses and partial payments
Query: Set up and manage invoices for multiple clients:

1. Create invoice for 'StartupX': Development 60hrs @ $175/hr (Due in ...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 50.86s
  Iterations: 5
  Input tokens: 17776
  Output tokens: 1215
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 826.95s
  Iterations: 4
  Input tokens: 11243
  Output tokens: 5027
  Sandbox: 4 runs, avg compile 54.12ms, avg exec 13.24ms
  Debug: iteration_failures=3, tool_discrepancies=4
  Validation: PASS (3/3 checks)

================================================================================

Scenario 8: Budget Tracking and Category Analysis
Description: Track expenses against budget categories and identify overspending
Query: Record a month of expenses and analyze spending patterns:

Office Expenses:
- Rent: $2,500
- Utilities: $180
- Internet:...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 89.19s
  Iterations: 3
  Input tokens: 11280
  Output tokens: 1663
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 28.69s
  Iterations: 1
  Input tokens: 985
  Output tokens: 1167
  Sandbox: 1 runs, avg compile 91.17ms, avg exec 12.89ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (2/2 checks)

================================================================================

================================================================================
SUMMARY
================================================================================

Regular Agent:
  Successful: 7/8
  Validation: 7/8 passed (87.5%)
  Avg Execution Time: 77.19s
  Avg Iterations: 4.00
  Total Input Tokens: 96934
  Total Output Tokens: 8103

Code Mode Agent:
  Successful: 8/8
  Validation: 7/8 passed (87.5%)
  Avg Execution Time: 213.53s
  Avg Iterations: 2.62
  Total Input Tokens: 64839
  Total Output Tokens: 27528
  Avg Sandbox Compile: 24.21ms
  Avg Sandbox Exec: 4.81ms
  Executed Code: 8/8 (100.0%)
  Iteration Failures: 13
  Tool Discrepancies: 8

Comparison:
  Code Mode time vs Regular: +176.6%
  Token difference (Code Mode - Regular): -12670
```