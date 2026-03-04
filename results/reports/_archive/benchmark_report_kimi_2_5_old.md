# Benchmark Report

- Model: OpenRouter (Moonshot Kimi K2.5)
- Model Key: `openrouter`
- Generated (UTC): 2026-03-04T16:01:49.916595Z

## Executive Summary

- Regular validation: 6/7 (85.7%)
- Code Mode validation: 5/6 (83.3%)
- Avg execution time: Regular `0.00s` vs Code Mode `0.00s`
- Total tokens: Regular `0` vs Code Mode `0`
- Code Mode iteration failures: `0`
- Code Mode tool discrepancies: `0`

## Scenario Breakdown

| Scenario | Regular (time/iter/tokens) | Code Mode (time/iter/tokens) | Validation (R/C) |
|---|---|---|---|
| 1 - Monthly Expense Recording | 75.93s / 3 / 6991 | 22.50s / 1 / 1627 | PASS (2/2 checks) / PASS (2/2 checks) |
| 2 - Client Invoicing Workflow | 36.64s / 4 / 8790 | 84.39s / 2 / 4429 | PASS (1/1 checks) / PASS (1/1 checks) |
| 3 - Payment Processing and Reconciliation | 67.42s / 6 / 14201 | 377.33s / 4 / 14522 | PASS (3/3 checks) / PASS (3/3 checks) |
| 4 - Mixed Income and Expense Tracking | 17.15s / 3 / 7333 | 77.35s / 2 / 4882 | PASS (4/4 checks) / PASS (4/4 checks) |
| 5 - Multi-Account Fund Management | 58.87s / 3 / 7989 | 111.56s / 3 / 7574 | PASS (1/1 checks) / PASS (1/1 checks) |
| 6 - Quarter-End Financial Analysis | 52.25s / 2 / 4432 | 772.19s / 2 / 2846 | FAIL (0/5 checks) / FAIL (0/5 checks) |
| 7 - Complex Multi-Client Invoice Management | 67.40s / 5 / 14602 | 0.00s / 0 / 0 | PASS (3/3 checks) / N/A |

## Code Mode Observability Highlights

| Scenario | Iteration Failures | Tool Discrepancies | Missing Expected Tools |
|---|---:|---:|---:|
| 1 - Monthly Expense Recording | 0 | 0 | 0 |
| 2 - Client Invoicing Workflow | 0 | 0 | 0 |
| 3 - Payment Processing and Reconciliation | 0 | 0 | 0 |
| 4 - Mixed Income and Expense Tracking | 0 | 0 | 0 |
| 5 - Multi-Account Fund Management | 0 | 0 | 0 |
| 6 - Quarter-End Financial Analysis | 0 | 0 | 0 |
| 7 - Complex Multi-Client Invoice Management | 0 | 0 | 0 |

## Console Transcript

```text
================================================================================
BENCHMARK: Regular Agent vs Code Mode Agent
Model: OpenRouter (Moonshot Kimi K2.5)
================================================================================

Scenario 1: Monthly Expense Recording
Description: Record all monthly business expenses and generate a summary
Query: Record monthly expenses...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 75.93s
  Iterations: 3
  Input tokens: 6373
  Output tokens: 618
  Validation: PASS (2/2 checks)

Running Code Mode Agent...
  Time: 22.50s
  Iterations: 1
  Input tokens: 898
  Output tokens: 729
  Validation: PASS (2/2 checks)

================================================================================

Scenario 2: Client Invoicing Workflow
Description: Create invoices for multiple clients and track their status
Query: Create invoices for TechStart and Design Studio...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 36.64s
  Iterations: 4
  Input tokens: 7918
  Output tokens: 872
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 84.39s
  Iterations: 2
  Input tokens: 2624
  Output tokens: 1805
  Validation: PASS (1/1 checks)

================================================================================

Scenario 3: Payment Processing and Reconciliation
Description: Process payments for invoices and reconcile accounts
Query: Process payments for invoices and reconcile accounts...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 67.42s
  Iterations: 6
  Input tokens: 13306
  Output tokens: 895
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 377.33s
  Iterations: 4
  Input tokens: 8571
  Output tokens: 5951
  Validation: PASS (3/3 checks)

================================================================================

Scenario 4: Mixed Income and Expense Tracking
Description: Record various income and expense transactions and analyze cash flow
Query: Record income and expenses and analyze cash flow...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 17.15s
  Iterations: 3
  Input tokens: 6584
  Output tokens: 749
  Validation: PASS (4/4 checks)

Running Code Mode Agent...
  Time: 77.35s
  Iterations: 2
  Input tokens: 1935
  Output tokens: 2947
  Validation: PASS (4/4 checks)

================================================================================

Scenario 5: Multi-Account Fund Management
Description: Transfer funds between accounts and track balances
Query: Transfer funds between accounts and track balances...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 58.87s
  Iterations: 3
  Input tokens: 7032
  Output tokens: 957
  Validation: PASS (1/1 checks)

Running Code Mode Agent...
  Time: 111.56s
  Iterations: 3
  Input tokens: 3314
  Output tokens: 4260
  Validation: PASS (1/1 checks)

================================================================================

Scenario 6: Quarter-End Financial Analysis
Description: Create comprehensive quarterly report with all financial data
Query: Simulate a quarter's worth of business activity...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 52.25s
  Iterations: 2
  Input tokens: 3714
  Output tokens: 718
  Validation: FAIL (0/5 checks)
  Error: Validation failed

Running Code Mode Agent...
  Time: 772.19s
  Iterations: 2
  Input tokens: 1046
  Output tokens: 1800
  Validation: FAIL (0/5 checks)
  Error: Validation failed

================================================================================

Scenario 7: Complex Multi-Client Invoice Management
Description: Manage multiple invoices with various statuses and partial payments
Query: Setup invoices for StartupX, RetailCo, TechGiant...
--------------------------------------------------------------------------------
Running Regular Agent...
  Time: 67.40s
  Iterations: 5
  Input tokens: 13190
  Output tokens: 1412
  Validation: PASS (3/3 checks)

Running Code Mode Agent...
  Time: 0.00s
  Iterations: 0
  Input tokens: 0
  Output tokens: 0
  Validation: N/A
  Error: Run canceled before Code Mode

================================================================================

================================================================================
SUMMARY
================================================================================

Regular Agent:
  Successful: 6/7
  Validation: 6/7 passed (85.7%)
  Avg Execution Time: 0.00s
  Avg Iterations: 0.00
  Total Input Tokens: 0
  Total Output Tokens: 0

Code Mode Agent:
  Successful: 5/7
  Validation: 5/6 passed (83.3%)
  Avg Execution Time: 0.00s
  Avg Iterations: 0.00
  Total Input Tokens: 0
  Total Output Tokens: 0
```