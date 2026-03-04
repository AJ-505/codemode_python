# Benchmark Report

- Model: GPT-5.2 (OpenAI)
- Model Key: `gpt_5_2`
- Generated (UTC): 2026-03-04T12:30:13.113653Z

## Executive Summary

- Regular validation: 8/8 (100.0%)
- Code Mode validation: 6/8 (75.0%)
- Avg execution time: Regular `12.33s` vs Code Mode `27.23s`
- Total tokens: Regular `79240` vs Code Mode `79657`
- Code Mode iteration failures: `14`
- Code Mode tool discrepancies: `23`

## Scenario Breakdown

| Scenario | Regular (time/iter/tokens) | Code Mode (time/iter/tokens) | Validation (R/C) |
|---|---|---|---|
| 1 - Monthly Expense Recording | 6.88s / 3 / 5478 | 5.22s / 1 / 1179 | PASS (2/2 checks) / PASS (2/2 checks) |
| 2 - Client Invoicing Workflow | 9.64s / 4 / 7823 | 30.91s / 3 / 8141 | PASS (1/1 checks) / PASS (1/1 checks) |
| 3 - Payment Processing and Reconciliation | 11.29s / 5 / 9753 | 9.95s / 1 / 1849 | PASS (3/3 checks) / PASS (3/3 checks) |
| 4 - Mixed Income and Expense Tracking | 7.72s / 3 / 6564 | 23.99s / 3 / 6927 | PASS (4/4 checks) / PASS (4/4 checks) |
| 5 - Multi-Account Fund Management | 10.16s / 3 / 6505 | 6.57s / 1 / 1438 | PASS (1/1 checks) / PASS (1/1 checks) |
| 6 - Quarter-End Financial Analysis | 19.87s / 6 / 17649 | 15.79s / 1 / 2552 | PASS (5/5 checks) / FAIL (3/5 checks) |
| 7 - Complex Multi-Client Invoice Management | 16.77s / 6 / 15837 | 13.29s / 1 / 2284 | PASS (3/3 checks) / FAIL (1/3 checks) |
| 8 - Budget Tracking and Category Analysis | 16.33s / 3 / 9631 | 112.09s / 11 / 55287 | PASS (2/2 checks) / PASS (2/2 checks) |

## Code Mode Observability Highlights

| Scenario | Iteration Failures | Tool Discrepancies | Missing Expected Tools |
|---|---:|---:|---:|
| 1 - Monthly Expense Recording | 0 | 0 | 0 |
| 2 - Client Invoicing Workflow | 2 | 6 | 0 |
| 3 - Payment Processing and Reconciliation | 0 | 2 | 0 |
| 4 - Mixed Income and Expense Tracking | 2 | 0 | 0 |
| 5 - Multi-Account Fund Management | 0 | 0 | 0 |
| 6 - Quarter-End Financial Analysis | 0 | 5 | 0 |
| 7 - Complex Multi-Client Invoice Management | 0 | 10 | 0 |
| 8 - Budget Tracking and Category Analysis | 10 | 0 | 0 |

## Console Transcript

```text
================================================================================
BENCHMARK: Regular Agent vs Code Mode Agent
Model: GPT-5.2 (OpenAI)
================================================================================

Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses and generate a summary
Query: Record the following monthly expenses:
- Rent: $2,500 to checking account
- Utilities (electricity): $150 to checking ac...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 6.88s
  Iterations: 3
  Input tokens: 5192
  Output tokens: 286
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 5.22s
  Iterations: 1
  Input tokens: 865
  Output tokens: 314
  Sandbox: 1 runs, avg compile 6.39ms, avg exec 4.24ms
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
  Time: 9.64s
  Iterations: 4
  Input tokens: 7284
  Output tokens: 539
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 30.91s
  Iterations: 3
  Input tokens: 5465
  Output tokens: 2676
  Sandbox: 3 runs, avg compile 2.58ms, avg exec 0.29ms
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
  Time: 11.29s
  Iterations: 5
  Input tokens: 9336
  Output tokens: 417
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 9.95s
  Iterations: 1
  Input tokens: 937
  Output tokens: 912
  Sandbox: 1 runs, avg compile 9.64ms, avg exec 2.25ms
  Debug: iteration_failures=0, tool_discrepancies=2
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
  Time: 7.72s
  Iterations: 3
  Input tokens: 6030
  Output tokens: 534
  Validation: PASS (4/4 checks)

Running Code Mode Agent...
  Time: 23.99s
  Iterations: 3
  Input tokens: 4885
  Output tokens: 2042
  Sandbox: 3 runs, avg compile 1.18ms, avg exec 0.35ms
  Debug: iteration_failures=2, tool_discrepancies=0
  Validation: PASS (4/4 checks)

================================================================================

Scenario 5: Multi-Account Fund Management
Description: Transfer funds between accounts and track balances
Query: Perform the following account operations:

1. Record business income of $15,000 to checking account (category: 'contract...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 10.16s
  Iterations: 3
  Input tokens: 6031
  Output tokens: 474
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 6.57s
  Iterations: 1
  Input tokens: 922
  Output tokens: 516
  Sandbox: 1 runs, avg compile 3.36ms, avg exec 1.26ms
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
  Time: 19.87s
  Iterations: 6
  Input tokens: 16509
  Output tokens: 1140
  Validation: PASS (5/5 checks)

Running Code Mode Agent...
  Time: 15.79s
  Iterations: 1
  Input tokens: 1011
  Output tokens: 1541
  Sandbox: 1 runs, avg compile 6.83ms, avg exec 5.21ms
  Debug: iteration_failures=0, tool_discrepancies=5
  Validation: FAIL (3/5 checks)

================================================================================

Scenario 7: Complex Multi-Client Invoice Management
Description: Manage multiple invoices with various statuses and partial payments
Query: Set up and manage invoices for multiple clients:

1. Create invoice for 'StartupX': Development 60hrs @ $175/hr (Due in ...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 16.77s
  Iterations: 6
  Input tokens: 15128
  Output tokens: 709
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 13.29s
  Iterations: 1
  Input tokens: 999
  Output tokens: 1285
  Sandbox: 1 runs, avg compile 4.90ms, avg exec 1.21ms
  Debug: iteration_failures=0, tool_discrepancies=10
  Validation: FAIL (1/3 checks)

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
  Time: 16.33s
  Iterations: 3
  Input tokens: 8814
  Output tokens: 817
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 112.09s
  Iterations: 11
  Input tokens: 45119
  Output tokens: 10168
  Sandbox: 11 runs, avg compile 1.35ms, avg exec 1.24ms
  Debug: iteration_failures=10, tool_discrepancies=0
  Validation: PASS (2/2 checks)

================================================================================

================================================================================
SUMMARY
================================================================================

Regular Agent:
  Successful: 8/8
  Validation: 8/8 passed (100.0%)
  Avg Execution Time: 12.33s
  Avg Iterations: 4.12
  Total Input Tokens: 74324
  Total Output Tokens: 4916

Code Mode Agent:
  Successful: 8/8
  Validation: 6/8 passed (75.0%)
  Avg Execution Time: 27.23s
  Avg Iterations: 2.75
  Total Input Tokens: 60203
  Total Output Tokens: 19454
  Avg Sandbox Compile: 4.53ms
  Avg Sandbox Exec: 2.01ms
  Executed Code: 8/8 (100.0%)
  Iteration Failures: 14
  Tool Discrepancies: 23

Comparison:
  Code Mode time vs Regular: +120.8%
  Token difference (Code Mode - Regular): +417
```