# Benchmark Report

- Model: Claude Opus 4.6 (Anthropic)
- Model Key: `opus_4_6`
- Generated (UTC): 2026-03-04T12:37:14.076381Z

## Executive Summary

- Regular validation: 8/8 (100.0%)
- Code Mode validation: 8/8 (100.0%)
- Avg execution time: Regular `27.30s` vs Code Mode `19.53s`
- Total tokens: Regular `435483` vs Code Mode `27292`
- Code Mode iteration failures: `3`
- Code Mode tool discrepancies: `24`

## Scenario Breakdown

| Scenario | Regular (time/iter/tokens) | Code Mode (time/iter/tokens) | Validation (R/C) |
|---|---|---|---|
| 1 - Monthly Expense Recording | 17.07s / 3 / 26653 | 8.70s / 1 / 1364 | PASS (2/2 checks) / PASS (2/2 checks) |
| 2 - Client Invoicing Workflow | 18.77s / 4 / 19239 | 12.34s / 1 / 1890 | PASS (1/1 checks) / PASS (1/1 checks) |
| 3 - Payment Processing and Reconciliation | 25.30s / 6 / 32793 | 27.49s / 2 / 5468 | PASS (3/3 checks) / PASS (3/3 checks) |
| 4 - Mixed Income and Expense Tracking | 20.32s / 3 / 42034 | 24.18s / 2 / 5155 | PASS (4/4 checks) / PASS (4/4 checks) |
| 5 - Multi-Account Fund Management | 19.48s / 3 / 36073 | 14.03s / 1 / 2108 | PASS (1/1 checks) / PASS (1/1 checks) |
| 6 - Quarter-End Financial Analysis | 51.61s / 6 / 137960 | 18.80s / 1 / 2742 | PASS (5/5 checks) / PASS (5/5 checks) |
| 7 - Complex Multi-Client Invoice Management | 31.65s / 5 / 50869 | 33.70s / 2 / 6285 | PASS (3/3 checks) / PASS (3/3 checks) |
| 8 - Budget Tracking and Category Analysis | 34.22s / 3 / 89862 | 17.01s / 1 / 2280 | PASS (2/2 checks) / PASS (2/2 checks) |

## Code Mode Observability Highlights

| Scenario | Iteration Failures | Tool Discrepancies | Missing Expected Tools |
|---|---:|---:|---:|
| 1 - Monthly Expense Recording | 0 | 0 | 0 |
| 2 - Client Invoicing Workflow | 0 | 0 | 0 |
| 3 - Payment Processing and Reconciliation | 1 | 0 | 0 |
| 4 - Mixed Income and Expense Tracking | 1 | 0 | 0 |
| 5 - Multi-Account Fund Management | 0 | 0 | 1 |
| 6 - Quarter-End Financial Analysis | 0 | 17 | 0 |
| 7 - Complex Multi-Client Invoice Management | 1 | 7 | 0 |
| 8 - Budget Tracking and Category Analysis | 0 | 0 | 0 |

## Console Transcript

```text
================================================================================
BENCHMARK: Regular Agent vs Code Mode Agent
Model: Claude Opus 4.6 (Anthropic)
================================================================================

Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses and generate a summary
Query: Record the following monthly expenses:
- Rent: $2,500 to checking account
- Utilities (electricity): $150 to checking ac...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 17.07s
  Iterations: 3
  Input tokens: 24231
  Output tokens: 2422
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 8.70s
  Iterations: 1
  Input tokens: 946
  Output tokens: 418
  Sandbox: 1 runs, avg compile 4.40ms, avg exec 0.90ms
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
  Time: 18.77s
  Iterations: 4
  Input tokens: 18083
  Output tokens: 1156
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 12.34s
  Iterations: 1
  Input tokens: 1012
  Output tokens: 878
  Sandbox: 1 runs, avg compile 2.67ms, avg exec 0.54ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (1/1 checks)

================================================================================

Scenario 3: Payment Processing and Reconciliation
Description: Process payments for invoices and reconcile accounts
Query: First, create an invoice for 'Acme Corp' with these items:
- Consulting Services: 50 hours at $200/hour
- Project Manage...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 25.30s
  Iterations: 6
  Input tokens: 31408
  Output tokens: 1385
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 27.49s
  Iterations: 2
  Input tokens: 3124
  Output tokens: 2344
  Sandbox: 2 runs, avg compile 2.91ms, avg exec 0.61ms
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
  Time: 20.32s
  Iterations: 3
  Input tokens: 35796
  Output tokens: 6238
  Validation: PASS (4/4 checks)

Running Code Mode Agent...
  Time: 24.18s
  Iterations: 2
  Input tokens: 3082
  Output tokens: 2073
  Sandbox: 2 runs, avg compile 4.08ms, avg exec 1.52ms
  Debug: iteration_failures=1, tool_discrepancies=0
  Validation: PASS (4/4 checks)

================================================================================

Scenario 5: Multi-Account Fund Management
Description: Transfer funds between accounts and track balances
Query: Perform the following account operations:

1. Record business income of $15,000 to checking account (category: 'contract...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 19.48s
  Iterations: 3
  Input tokens: 33020
  Output tokens: 3053
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 14.03s
  Iterations: 1
  Input tokens: 1005
  Output tokens: 1103
  Sandbox: 1 runs, avg compile 18.12ms, avg exec 0.96ms
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
  Time: 51.61s
  Iterations: 6
  Input tokens: 123354
  Output tokens: 14606
  Validation: PASS (5/5 checks)

Running Code Mode Agent...
  Time: 18.80s
  Iterations: 1
  Input tokens: 1096
  Output tokens: 1646
  Sandbox: 1 runs, avg compile 14.50ms, avg exec 3.37ms
  Debug: iteration_failures=0, tool_discrepancies=17
  Validation: PASS (5/5 checks)

================================================================================

Scenario 7: Complex Multi-Client Invoice Management
Description: Manage multiple invoices with various statuses and partial payments
Query: Set up and manage invoices for multiple clients:

1. Create invoice for 'StartupX': Development 60hrs @ $175/hr (Due in ...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 31.65s
  Iterations: 5
  Input tokens: 47584
  Output tokens: 3285
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 33.70s
  Iterations: 2
  Input tokens: 3511
  Output tokens: 2774
  Sandbox: 2 runs, avg compile 4.64ms, avg exec 0.82ms
  Debug: iteration_failures=1, tool_discrepancies=7
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
  Time: 34.22s
  Iterations: 3
  Input tokens: 63456
  Output tokens: 26406
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 17.01s
  Iterations: 1
  Input tokens: 1048
  Output tokens: 1232
  Sandbox: 1 runs, avg compile 88.77ms, avg exec 6.22ms
  Debug: iteration_failures=0, tool_discrepancies=0
  Validation: PASS (2/2 checks)

================================================================================

================================================================================
SUMMARY
================================================================================

Regular Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 27.30s
  Avg Iterations: 4.12
  Total Input Tokens: 376932
  Total Output Tokens: 58551

Code Mode Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 19.53s
  Avg Iterations: 1.38
  Total Input Tokens: 14824
  Total Output Tokens: 12468
  Avg Sandbox Compile: 17.51ms
  Avg Sandbox Exec: 1.87ms
  Executed Code: 8/8 (100.0%)
  Iteration Failures: 3
  Tool Discrepancies: 24

Comparison:
  Code Mode time vs Regular: -28.5%
  Token difference (Code Mode - Regular): -408191
```