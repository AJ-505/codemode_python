"""
Realistic business scenario test cases for the benchmark.
Each scenario involves multiple operations that modify state.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


def get_date(days_offset: int = 0) -> str:
    """Get ISO format date with offset from today."""
    return (datetime.now() + timedelta(days=days_offset)).strftime("%Y-%m-%d")


# Define expected outcomes for validation
SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "Monthly Expense Recording",
        "description": "Record all monthly business expenses and generate a summary",
        "query": """Record the following monthly expenses:
- Rent: $2,500 to checking account
- Utilities (electricity): $150 to checking account
- Internet/Phone: $100 to checking account
- Office supplies: $75 to checking account

Then provide a summary showing total expenses and remaining balance in the checking account.""",
        "expected_state": {
            "min_transactions": 4,
            "transaction_types": {"expense": 4},
            "categories": ["rent", "utilities", "office_supplies"],
            "total_expenses_min": 2825.0,
            "checking_balance_max": 7175.0  # Started with 10000
        },
        "validation_queries": [
            "How many expense transactions were created?",
            "What is the total amount of expenses?",
            "What is the checking account balance?"
        ]
    },
    {
        "id": 2,
        "name": "Client Invoicing Workflow",
        "description": "Create invoices for multiple clients and track their status",
        "query": """Create invoices for the following clients:

1. TechStart Inc:
   - Software Development: 80 hours at $150/hour
   - Code Review: 10 hours at $100/hour
   Due in 30 days

2. Design Studio:
   - UI/UX Design: 40 hours at $125/hour
   - Prototyping: 15 hours at $100/hour
   Due in 15 days

After creating the invoices, mark the TechStart Inc invoice as 'sent'.
Then provide a summary of all invoices and total outstanding receivables.""",
        "expected_state": {
            "min_invoices": 2,
            "invoice_statuses": {"draft": 1, "sent": 1},
            "total_invoice_amount_min": 15500.0,  # 13000 + 6500
            "clients": ["TechStart Inc", "Design Studio"]
        },
        "validation_queries": [
            "How many invoices were created?",
            "What is the status of each invoice?",
            "What is the total amount of outstanding receivables?"
        ]
    },
    {
        "id": 3,
        "name": "Payment Processing and Reconciliation",
        "description": "Process payments for invoices and reconcile accounts",
        "query": """First, create an invoice for 'Acme Corp' with these items:
- Consulting Services: 50 hours at $200/hour
- Project Management: 20 hours at $150/hour

Mark the invoice as 'sent'.

Then, record a partial payment of $8,000 from Acme Corp.
After that, record another partial payment of $5,000 from Acme Corp.

Finally, provide a summary showing:
- The invoice details including paid and remaining amounts
- The checking account balance
- Total income from invoice payments""",
        "expected_state": {
            "min_invoices": 1,
            "min_transactions": 2,  # Two payment transactions
            "total_income_min": 13000.0,
            "invoice_paid_amount": 13000.0,
            "invoice_status": "paid",
            "checking_balance_min": 23000.0  # Initial + payments
        },
        "validation_queries": [
            "Is the invoice fully paid?",
            "How much income was recorded?",
            "What is the checking account balance?"
        ]
    },
    {
        "id": 4,
        "name": "Mixed Income and Expense Tracking",
        "description": "Record various income and expense transactions and analyze cash flow",
        "query": """Record the following transactions:

Income:
- Client payment: $5,000 from 'consulting' work
- Product sale: $1,500 from 'product_sales'
- Referral bonus: $500 from 'referral_income'

Expenses:
- Software subscriptions: $299
- Marketing ads: $800
- Professional development: $450
- Business lunch: $125

Then provide a financial summary showing:
- Total income by category
- Total expenses by category
- Net income (income - expenses)
- Current checking account balance""",
        "expected_state": {
            "min_transactions": 7,
            "transaction_types": {"income": 3, "expense": 4},
            "total_income_min": 7000.0,
            "total_expenses_min": 1674.0,
            "net_income_min": 5326.0,
            "checking_balance_min": 15326.0
        },
        "validation_queries": [
            "What is the total income?",
            "What is the total expenses?",
            "What is the net income?",
            "What is the checking balance?"
        ]
    },
    {
        "id": 5,
        "name": "Multi-Account Fund Management",
        "description": "Transfer funds between accounts and track balances",
        "query": """Perform the following account operations:

1. Record business income of $15,000 to checking account (category: 'contract_work')
2. Transfer $20,000 from checking to savings for emergency fund
3. Pay a large expense of $3,500 from checking (category: 'equipment', description: 'New laptop and monitors')
4. Transfer $5,000 from savings back to checking to cover upcoming expenses

Then provide a summary showing:
- Balance of each account (checking, savings, business_credit)
- Total transaction count
- List of all transfers made""",
        "expected_state": {
            "min_transactions": 6,  # 2 transfers (4 txns) + 1 income + 1 expense
            "transfer_count": 4,  # Each transfer creates 2 transactions
            "checking_balance": 6500.0,  # 10000 + 15000 - 20000 - 3500 + 5000 = 6500
            "savings_balance": 65000.0,  # 50000 + 20000 - 5000 = 65000
            "total_transfers": 2
        },
        "validation_queries": [
            "What are the balances of all accounts?",
            "How many transfers were made?",
            "What is the current checking balance?"
        ]
    },
    {
        "id": 6,
        "name": "Quarter-End Financial Analysis",
        "description": "Create comprehensive quarterly report with all financial data",
        "query": """Simulate a quarter's worth of business activity:

Month 1:
- Record income: $12,000 (consulting)
- Record expenses: Rent $2,500, Utilities $200, Supplies $300

Month 2:
- Create invoice for 'BigCorp': Consulting 100hrs @ $150/hr, mark as sent
- Record income: $8,000 (product sales)
- Record expenses: Rent $2,500, Marketing $1,200, Software $400

Month 3:
- Record payment for BigCorp invoice (mark as paid)
- Record income: $6,000 (consulting)
- Record expenses: Rent $2,500, Utilities $250, Travel $800

Then provide a comprehensive quarter-end report including:
- Total income and breakdown by category
- Total expenses and breakdown by category
- Net profit for the quarter
- Number of invoices and their statuses
- All account balances
- Outstanding receivables""",
        "expected_state": {
            "min_transactions": 12,  # 4 income + 8 expense + invoice payment
            "min_invoices": 1,
            "total_income_min": 41000.0,  # 12k + 8k + 15k (invoice) + 6k
            "total_expenses_min": 10650.0,  # Sum of all expenses
            "net_income_min": 30000.0,
            "invoice_statuses": {"paid": 1},
            "categories_count_min": 8
        },
        "validation_queries": [
            "What is the total income for the quarter?",
            "What is the total expenses?",
            "What is the net profit?",
            "What are all the expense categories?",
            "What is the outstanding receivables amount?"
        ]
    },
    {
        "id": 7,
        "name": "Complex Multi-Client Invoice Management",
        "description": "Manage multiple invoices with various statuses and partial payments",
        "query": """Set up and manage invoices for multiple clients:

1. Create invoice for 'StartupX': Development 60hrs @ $175/hr (Due in 30 days)
2. Create invoice for 'RetailCo': Consulting 40hrs @ $200/hr (Due in 45 days)
3. Create invoice for 'TechGiant': Design 80hrs @ $150/hr, Testing 20hrs @ $100/hr (Due in 30 days)

Then:
- Mark all invoices as 'sent'
- Record partial payment of $7,000 for StartupX
- Mark RetailCo invoice as 'paid' (full payment)
- Record partial payment of $10,000 for TechGiant

Finally, provide a report showing:
- List all invoices with their status and amounts (total, paid, remaining)
- Total outstanding receivables
- Total payments received (income)
- Which invoices still need follow-up""",
        "expected_state": {
            "min_invoices": 3,
            "invoice_statuses": {"sent": 2, "paid": 1},
            "total_invoice_amount": 32500.0,  # 10500 + 8000 + 14000 = 32500 (not 33500!)
            "total_paid": 25000.0,  # 7000 + 8000 + 10000
            "outstanding_receivables": 7500.0,  # 32500 - 25000 = 7500
            "total_income_min": 25000.0
        },
        "validation_queries": [
            "How many invoices are still unpaid or partially paid?",
            "What is the total outstanding receivables?",
            "Which clients have fully paid?",
            "What is the total income from invoice payments?"
        ]
    },
    {
        "id": 8,
        "name": "Budget Tracking and Category Analysis",
        "description": "Track expenses against budget categories and identify overspending",
        "query": """Record a month of expenses and analyze spending patterns:

Office Expenses:
- Rent: $2,500
- Utilities: $180
- Internet: $100
- Office supplies: $250
- Cleaning service: $200

Marketing:
- Social media ads: $600
- Content creation: $800
- SEO tools: $150

Operations:
- Software licenses: $450
- Cloud hosting: $300
- Domain renewals: $50

Professional Development:
- Online courses: $200
- Conference ticket: $500
- Books: $75

Then provide an analysis showing:
- Total spent in each major category (Office, Marketing, Operations, Professional Development)
- The three highest individual expenses
- Total expenses for the month
- Remaining checking account balance""",
        "expected_state": {
            "min_transactions": 14,
            "expense_categories": ["rent", "utilities", "marketing", "software", "professional_development"],
            "total_expenses_min": 6355.0,
            "highest_expense": 2500.0,
            "category_totals": {
                "office_related": 3230.0,
                "marketing": 1550.0,
                "operations": 800.0,
                "professional_development": 775.0
            }
        },
        "validation_queries": [
            "What is the total for each major category?",
            "What are the three highest expenses?",
            "What is the total monthly expense?",
            "What is the remaining balance?"
        ]
    }
]


def get_scenarios() -> List[Dict[str, Any]]:
    """Return all test scenarios."""
    return SCENARIOS


def get_scenario_by_id(scenario_id: int) -> Dict[str, Any]:
    """Get a specific scenario by ID."""
    for scenario in SCENARIOS:
        if scenario["id"] == scenario_id:
            return scenario
    return None


def validate_scenario_result(scenario_id: int, state_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that the final state matches expected outcomes for a scenario.

    Args:
        scenario_id: The scenario ID
        state_summary: The final state summary from get_state_summary()

    Returns:
        Dictionary with validation results
    """
    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        return {"valid": False, "error": f"Scenario {scenario_id} not found"}

    expected = scenario["expected_state"]
    checks = []
    passed = 0
    failed = 0

    # Validate transaction count
    if "min_transactions" in expected:
        actual = state_summary.get("total_transactions", 0)
        check_passed = actual >= expected["min_transactions"]
        checks.append({
            "check": f"Minimum {expected['min_transactions']} transactions",
            "expected": f">= {expected['min_transactions']}",
            "actual": actual,
            "passed": check_passed
        })
        if check_passed:
            passed += 1
        else:
            failed += 1

    # Validate invoice count
    if "min_invoices" in expected:
        actual = state_summary.get("total_invoices", 0)
        check_passed = actual >= expected["min_invoices"]
        checks.append({
            "check": f"Minimum {expected['min_invoices']} invoices",
            "expected": f">= {expected['min_invoices']}",
            "actual": actual,
            "passed": check_passed
        })
        if check_passed:
            passed += 1
        else:
            failed += 1

    # Validate total income
    if "total_income_min" in expected:
        actual = state_summary.get("total_income", 0)
        check_passed = actual >= expected["total_income_min"]
        checks.append({
            "check": f"Minimum total income",
            "expected": f">= ${expected['total_income_min']}",
            "actual": f"${actual}",
            "passed": check_passed
        })
        if check_passed:
            passed += 1
        else:
            failed += 1

    # Validate total expenses
    if "total_expenses_min" in expected:
        actual = state_summary.get("total_expenses", 0)
        check_passed = actual >= expected["total_expenses_min"]
        checks.append({
            "check": f"Minimum total expenses",
            "expected": f">= ${expected['total_expenses_min']}",
            "actual": f"${actual}",
            "passed": check_passed
        })
        if check_passed:
            passed += 1
        else:
            failed += 1

    # Validate net income
    if "net_income_min" in expected:
        actual = state_summary.get("net_income", 0)
        check_passed = actual >= expected["net_income_min"]
        checks.append({
            "check": f"Minimum net income",
            "expected": f">= ${expected['net_income_min']}",
            "actual": f"${actual}",
            "passed": check_passed
        })
        if check_passed:
            passed += 1
        else:
            failed += 1

    # Validate outstanding receivables
    if "outstanding_receivables" in expected:
        actual = state_summary.get("outstanding_receivables", 0)
        check_passed = abs(actual - expected["outstanding_receivables"]) < 0.01  # Float comparison
        checks.append({
            "check": "Outstanding receivables",
            "expected": f"${expected['outstanding_receivables']}",
            "actual": f"${actual}",
            "passed": check_passed
        })
        if check_passed:
            passed += 1
        else:
            failed += 1

    return {
        "valid": failed == 0,
        "scenario_id": scenario_id,
        "scenario_name": scenario["name"],
        "checks": checks,
        "passed": passed,
        "failed": failed,
        "total_checks": len(checks)
    }
