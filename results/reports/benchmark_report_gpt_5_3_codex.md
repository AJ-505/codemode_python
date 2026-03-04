# Benchmark Report

- Model: GPT-5.3 Codex (OpenAI)
- Model Key: `gpt_5_3_codex`
- Generated (UTC): 2026-03-04T12:30:13.323134Z

## Executive Summary

- Regular validation: 8/8 (100.0%)
- Code Mode validation: 8/8 (100.0%)
- Avg execution time: Regular `17.77s` vs Code Mode `14.86s`
- Total tokens: Regular `95482` vs Code Mode `22352`
- Code Mode iteration failures: `2`
- Code Mode tool discrepancies: `49`

## Scenario Breakdown

| Scenario | Regular (time/iter/tokens) | Code Mode (time/iter/tokens) | Validation (R/C) |
|---|---|---|---|
| 1 - Monthly Expense Recording | 12.09s / 3 / 5579 | 6.31s / 1 / 1321 | PASS (2/2 checks) / PASS (2/2 checks) |
| 2 - Client Invoicing Workflow | 21.09s / 6 / 11125 | 11.45s / 1 / 1676 | PASS (1/1 checks) / PASS (1/1 checks) |
| 3 - Payment Processing and Reconciliation | 18.61s / 6 / 11136 | 9.33s / 1 / 1766 | PASS (3/3 checks) / PASS (3/3 checks) |
| 4 - Mixed Income and Expense Tracking | 14.09s / 3 / 6618 | 9.41s / 1 / 1822 | PASS (4/4 checks) / PASS (4/4 checks) |
| 5 - Multi-Account Fund Management | 16.10s / 6 / 10933 | 9.61s / 1 / 1503 | PASS (1/1 checks) / PASS (1/1 checks) |
| 6 - Quarter-End Financial Analysis | 28.95s / 9 / 25177 | 52.10s / 3 / 10696 | PASS (5/5 checks) / PASS (5/5 checks) |
| 7 - Complex Multi-Client Invoice Management | 16.34s / 6 / 15588 | 13.97s / 1 / 1980 | PASS (3/3 checks) / PASS (3/3 checks) |
| 8 - Budget Tracking and Category Analysis | 14.88s / 3 / 9326 | 6.73s / 1 / 1588 | PASS (2/2 checks) / PASS (2/2 checks) |

## Code Mode Observability Highlights

| Scenario | Iteration Failures | Tool Discrepancies | Missing Expected Tools |
|---|---:|---:|---:|
| 1 - Monthly Expense Recording | 0 | 0 | 0 |
| 2 - Client Invoicing Workflow | 0 | 2 | 0 |
| 3 - Payment Processing and Reconciliation | 0 | 1 | 0 |
| 4 - Mixed Income and Expense Tracking | 0 | 0 | 0 |
| 5 - Multi-Account Fund Management | 0 | 0 | 0 |
| 6 - Quarter-End Financial Analysis | 2 | 34 | 0 |
| 7 - Complex Multi-Client Invoice Management | 0 | 12 | 0 |
| 8 - Budget Tracking and Category Analysis | 0 | 0 | 0 |

## Console Transcript

```text
================================================================================
BENCHMARK: Regular Agent vs Code Mode Agent
Model: GPT-5.3 Codex (OpenAI)
================================================================================

Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses and generate a summary
Query: Record the following monthly expenses:
- Rent: $2,500 to checking account
- Utilities (electricity): $150 to checking ac...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 12.09s
  Iterations: 3
  Input tokens: 5208
  Output tokens: 371
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 6.31s
  Iterations: 1
  Input tokens: 897
  Output tokens: 424
  Sandbox: 1 runs, avg compile 12.35ms, avg exec 1.51ms
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
  Time: 21.09s
  Iterations: 6
  Input tokens: 10608
  Output tokens: 517
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 11.45s
  Iterations: 1
  Input tokens: 955
  Output tokens: 721
  Sandbox: 1 runs, avg compile 3.93ms, avg exec 2.30ms
  Debug: iteration_failures=0, tool_discrepancies=2
  Validation: PASS (1/1 checks)

================================================================================

Scenario 3: Payment Processing and Reconciliation
Description: Process payments for invoices and reconcile accounts
Query: First, create an invoice for 'Acme Corp' with these items:
- Consulting Services: 50 hours at $200/hour
- Project Manage...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 18.61s
  Iterations: 6
  Input tokens: 10711
  Output tokens: 425
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 9.33s
  Iterations: 1
  Input tokens: 969
  Output tokens: 797
  Sandbox: 1 runs, avg compile 7.93ms, avg exec 1.77ms
  Debug: iteration_failures=0, tool_discrepancies=1
  Validation: PASS (3/3 checks)

================================================================================

Scenario 4: Mixed Income and Expense Tracking
Description: Record various income and expense transactions and analyze cash flow
Query: Record the following transactions:

Income:
- Client payment: $5,000 from 'consulting' work
- Product sale: $1,500 from ...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 14.09s
  Iterations: 3
  Input tokens: 6066
  Output tokens: 552
  Validation: PASS (4/4 checks)

Running Code Mode Agent...
  Time: 9.41s
  Iterations: 1
  Input tokens: 942
  Output tokens: 880
  Sandbox: 1 runs, avg compile 10.40ms, avg exec 2.89ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (4/4 checks)

================================================================================

Scenario 5: Multi-Account Fund Management
Description: Transfer funds between accounts and track balances
Query: Perform the following account operations:

1. Record business income of $15,000 to checking account (category: 'contract...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 16.10s
  Iterations: 6
  Input tokens: 10412
  Output tokens: 521
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 9.61s
  Iterations: 1
  Input tokens: 954
  Output tokens: 549
  Sandbox: 1 runs, avg compile 6.23ms, avg exec 2.77ms
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
  Time: 28.95s
  Iterations: 9
  Input tokens: 23771
  Output tokens: 1406
  Validation: PASS (5/5 checks)

Running Code Mode Agent...
  Time: 52.10s
  Iterations: 3
  Input tokens: 7019
  Output tokens: 3677
  Sandbox: 3 runs, avg compile 4.13ms, avg exec 3.14ms
  Debug: iteration_failures=2, tool_discrepancies=34
  Validation: PASS (5/5 checks)

================================================================================

Scenario 7: Complex Multi-Client Invoice Management
Description: Manage multiple invoices with various statuses and partial payments
Query: Set up and manage invoices for multiple clients:

1. Create invoice for 'StartupX': Development 60hrs @ $175/hr (Due in ...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 16.34s
  Iterations: 6
  Input tokens: 14855
  Output tokens: 733
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 13.97s
  Iterations: 1
  Input tokens: 1031
  Output tokens: 949
  Sandbox: 1 runs, avg compile 5.83ms, avg exec 2.74ms
  Debug: iteration_failures=0, tool_discrepancies=12
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
  Time: 14.88s
  Iterations: 3
  Input tokens: 8335
  Output tokens: 991
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 6.73s
  Iterations: 1
  Input tokens: 993
  Output tokens: 595
  Sandbox: 1 runs, avg compile 5.51ms, avg exec 13.18ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (2/2 checks)

================================================================================

================================================================================
SUMMARY
================================================================================

Regular Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 17.77s
  Avg Iterations: 5.25
  Total Input Tokens: 89966
  Total Output Tokens: 5516

Code Mode Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 14.86s
  Avg Iterations: 1.25
  Total Input Tokens: 13760
  Total Output Tokens: 8592
  Avg Sandbox Compile: 7.04ms
  Avg Sandbox Exec: 3.79ms
  Executed Code: 8/8 (100.0%)
  Iteration Failures: 2
  Tool Discrepancies: 49

Comparison:
  Code Mode time vs Regular: -16.3%
  Token difference (Code Mode - Regular): -73130
```