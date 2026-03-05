# Benchmark Report

- Model: Claude Sonnet 4.6 (Anthropic)
- Model Key: `sonnet_4_6`
- Generated (UTC): 2026-03-05T16:43:09.836361Z

## Executive Summary

- Regular validation: 8/8 (100.0%)
- Code Mode validation: 8/8 (100.0%)
- Avg execution time: Regular `29.08s` vs Code Mode `47.24s`
- Total tokens: Regular `430286` vs Code Mode `89991`
- Code Mode iteration failures: `12`
- Code Mode tool discrepancies: `56`

## Scenario Breakdown

| Scenario | Regular (time/iter/tokens) | Code Mode (time/iter/tokens) | Validation (R/C) |
|---|---|---|---|
| 1 - Monthly Expense Recording | 29.43s / 3 / 27275 | 11.82s / 1 / 1805 | PASS (2/2 checks) / PASS (2/2 checks) |
| 2 - Client Invoicing Workflow | 18.83s / 4 / 19609 | 36.00s / 3 / 9721 | PASS (1/1 checks) / PASS (1/1 checks) |
| 3 - Payment Processing and Reconciliation | 24.82s / 6 / 33693 | 24.40s / 2 / 5513 | PASS (3/3 checks) / PASS (3/3 checks) |
| 4 - Mixed Income and Expense Tracking | 21.04s / 3 / 41872 | 12.63s / 1 / 2069 | PASS (4/4 checks) / PASS (4/4 checks) |
| 5 - Multi-Account Fund Management | 27.21s / 5 / 47890 | 11.19s / 1 / 2069 | PASS (1/1 checks) / PASS (1/1 checks) |
| 6 - Quarter-End Financial Analysis | 47.71s / 6 / 121137 | 68.26s / 4 / 23180 | PASS (5/5 checks) / PASS (5/5 checks) |
| 7 - Complex Multi-Client Invoice Management | 32.80s / 5 / 50612 | 148.89s / 4 / 22485 | PASS (3/3 checks) / PASS (3/3 checks) |
| 8 - Budget Tracking and Category Analysis | 30.84s / 3 / 88198 | 64.70s / 4 / 23149 | PASS (2/2 checks) / PASS (2/2 checks) |

## Code Mode Observability Highlights

| Scenario | Iteration Failures | Tool Discrepancies | Missing Expected Tools |
|---|---:|---:|---:|
| 1 - Monthly Expense Recording | 0 | 0 | 0 |
| 2 - Client Invoicing Workflow | 2 | 6 | 0 |
| 3 - Payment Processing and Reconciliation | 1 | 0 | 0 |
| 4 - Mixed Income and Expense Tracking | 0 | 7 | 0 |
| 5 - Multi-Account Fund Management | 0 | 0 | 0 |
| 6 - Quarter-End Financial Analysis | 3 | 34 | 1 |
| 7 - Complex Multi-Client Invoice Management | 3 | 9 | 0 |
| 8 - Budget Tracking and Category Analysis | 3 | 0 | 0 |

## Console Transcript

```text
================================================================================
BENCHMARK: Regular Agent vs Code Mode Agent
Model: Claude Sonnet 4.6 (Anthropic)
================================================================================

Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses and generate a summary
Query: Record the following monthly expenses:
- Rent: $2,500 to checking account
- Utilities (electricity): $150 to checking ac...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 29.43s
  Iterations: 3
  Input tokens: 24630
  Output tokens: 2645
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 11.82s
  Iterations: 1
  Input tokens: 1064
  Output tokens: 741
  Sandbox: 1 runs, avg compile 3.21ms, avg exec 0.56ms
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
  Time: 18.83s
  Iterations: 4
  Input tokens: 18375
  Output tokens: 1234
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 36.00s
  Iterations: 3
  Input tokens: 6647
  Output tokens: 3074
  Sandbox: 3 runs, avg compile 1.41ms, avg exec 0.38ms
  Debug: iteration_failures=2, tool_discrepancies=6
  Validation: PASS (1/1 checks)

================================================================================

Scenario 3: Payment Processing and Reconciliation
Description: Process payments for invoices and reconcile accounts
Query: First, create an invoice for 'Acme Corp' with these items:
- Consulting Services: 50 hours at $200/hour
- Project Manage...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 24.82s
  Iterations: 6
  Input tokens: 32002
  Output tokens: 1691
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 24.40s
  Iterations: 2
  Input tokens: 3301
  Output tokens: 2212
  Sandbox: 2 runs, avg compile 2.51ms, avg exec 0.43ms
  Debug: iteration_failures=1, tool_discrepancies=0
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
  Time: 21.04s
  Iterations: 3
  Input tokens: 36016
  Output tokens: 5856
  Validation: PASS (4/4 checks)

Running Code Mode Agent...
  Time: 12.63s
  Iterations: 1
  Input tokens: 1120
  Output tokens: 949
  Sandbox: 1 runs, avg compile 4.26ms, avg exec 2.08ms
  Debug: iteration_failures=0, tool_discrepancies=7
  Validation: PASS (4/4 checks)

================================================================================

Scenario 5: Multi-Account Fund Management
Description: Transfer funds between accounts and track balances
Query: Perform the following account operations:

1. Record business income of $15,000 to checking account (category: 'contract...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 27.21s
  Iterations: 5
  Input tokens: 45020
  Output tokens: 2870
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 11.19s
  Iterations: 1
  Input tokens: 1133
  Output tokens: 936
  Sandbox: 1 runs, avg compile 10.81ms, avg exec 1.33ms
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
  Time: 47.71s
  Iterations: 6
  Input tokens: 110493
  Output tokens: 10644
  Validation: PASS (5/5 checks)

Running Code Mode Agent...
  Time: 68.26s
  Iterations: 4
  Input tokens: 16411
  Output tokens: 6769
  Sandbox: 4 runs, avg compile 2.05ms, avg exec 0.56ms
  Debug: iteration_failures=3, tool_discrepancies=34
  Validation: PASS (5/5 checks)

================================================================================

Scenario 7: Complex Multi-Client Invoice Management
Description: Manage multiple invoices with various statuses and partial payments
Query: Set up and manage invoices for multiple clients:

1. Create invoice for 'StartupX': Development 60hrs @ $175/hr (Due in ...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 32.80s
  Iterations: 5
  Input tokens: 47252
  Output tokens: 3360
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 148.89s
  Iterations: 4
  Input tokens: 15650
  Output tokens: 6835
  Sandbox: 4 runs, avg compile 3.48ms, avg exec 0.66ms
  Debug: iteration_failures=3, tool_discrepancies=9
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
  Time: 30.84s
  Iterations: 3
  Input tokens: 64051
  Output tokens: 24147
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 64.70s
  Iterations: 4
  Input tokens: 16086
  Output tokens: 7063
  Sandbox: 4 runs, avg compile 6.92ms, avg exec 0.64ms
  Debug: iteration_failures=3, tool_discrepancies=0
  Validation: PASS (2/2 checks)

================================================================================

================================================================================
SUMMARY
================================================================================

Regular Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 29.08s
  Avg Iterations: 4.38
  Total Input Tokens: 377839
  Total Output Tokens: 52447

Code Mode Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 47.24s
  Avg Iterations: 2.50
  Total Input Tokens: 61412
  Total Output Tokens: 28579
  Avg Sandbox Compile: 4.33ms
  Avg Sandbox Exec: 0.83ms
  Executed Code: 8/8 (100.0%)
  Iteration Failures: 12
  Tool Discrepancies: 56

Comparison:
  Code Mode time vs Regular: +62.4%
  Token difference (Code Mode - Regular): -340295
```