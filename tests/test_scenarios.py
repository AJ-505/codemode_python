"""
Realistic business scenario test cases for the benchmark.
Each scenario involves multiple operations that modify state.
"""

from dataclasses import asdict, is_dataclass
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
            "total_transactions": 4,
            "transaction_types": {"expense": 4},
            "total_expenses": 2825.0,
            "checking_balance": 7175.0,  # Started with 10000
            "categories": ["rent", "utilities", "internet_phone", "office_supplies"],
        },
        "expected_tool_flow": [
            {"tool": "create_transaction", "min_calls": 4},
            {"tool": "get_financial_summary", "min_calls": 1},
        ],
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
            "total_invoices": 2,
            "invoice_statuses": {"draft": 1, "sent": 1},
            "total_invoice_amount": 19500.0,  # 13000 + 6500
            "clients": ["TechStart Inc", "Design Studio"]
        },
        "expected_tool_flow": [
            {"tool": "create_invoice", "min_calls": 2},
            {"tool": "update_invoice_status", "min_calls": 1},
            {"tool": "get_invoices", "min_calls": 1},
        ],
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
            "total_invoices": 1,
            "total_transactions": 2,  # Two payment transactions
            "total_income": 13000.0,
            "invoice_paid_amount": 13000.0,
            "invoice_status": "paid",
            "checking_balance": 23000.0  # Initial + payments
        },
        "expected_tool_flow": [
            {"tool": "create_invoice", "min_calls": 1},
            {"tool": "update_invoice_status", "min_calls": 1},
            {"tool": "record_partial_payment", "min_calls": 2},
            {"tool": "get_account_balance", "min_calls": 1},
        ],
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
            "total_transactions": 7,
            "transaction_types": {"income": 3, "expense": 4},
            "total_income": 7000.0,
            "total_expenses": 1674.0,
            "net_income": 5326.0,
            "checking_balance": 15326.0
        },
        "expected_tool_flow": [
            {"tool": "create_transaction", "min_calls": 7},
            {"tool": "get_financial_summary", "min_calls": 1},
        ],
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
            "total_transactions": 6,  # 2 transfers (4 txns) + 1 income + 1 expense
            "transfer_count": 4,  # Each transfer creates 2 transactions
            "checking_balance": 6500.0,  # 10000 + 15000 - 20000 - 3500 + 5000 = 6500
            "savings_balance": 65000.0,  # 50000 + 20000 - 5000 = 65000
            "total_transfers": 2
        },
        "expected_tool_flow": [
            {"tool": "create_transaction", "min_calls": 2},
            {"tool": "transfer_between_accounts", "min_calls": 2},
            {"tool": "get_state_summary", "min_calls": 1},
        ],
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
            "total_transactions": 12,  # 4 income + 8 expense + invoice payment
            "total_invoices": 1,
            "total_income": 41000.0,  # 12k + 8k + 15k (invoice) + 6k
            "total_expenses": 10650.0,  # Sum of all expenses
            "net_income": 30350.0,
            "invoice_statuses": {"paid": 1},
            "categories_count_min": 8
        },
        "expected_tool_flow": [
            {"tool": "create_transaction", "min_calls": 10},
            {"tool": "create_invoice", "min_calls": 1},
            {"tool": "update_invoice_status", "min_calls": 2},
            {"tool": "get_financial_summary", "min_calls": 1},
        ],
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
            "total_invoices": 3,
            "invoice_statuses": {"sent": 2, "paid": 1},
            "total_invoice_amount": 32500.0,  # 10500 + 8000 + 14000 = 32500 (not 33500!)
            "total_paid": 25000.0,  # 7000 + 8000 + 10000
            "outstanding_receivables": 7500.0,  # 32500 - 25000 = 7500
            "total_income": 25000.0
        },
        "expected_tool_flow": [
            {"tool": "create_invoice", "min_calls": 3},
            {"tool": "update_invoice_status", "min_calls": 4},
            {"tool": "record_partial_payment", "min_calls": 2},
            {"tool": "get_invoices", "min_calls": 1},
        ],
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
            "total_transactions": 14,
            "expense_categories": ["rent", "utilities", "marketing", "software", "professional_development"],
            "total_expenses": 6355.0,
            "highest_expense": 2500.0,
            "checking_balance": 3645.0,
            "category_totals": {
                "office_related": 3230.0,
                "marketing": 1550.0,
                "operations": 800.0,
                "professional_development": 775.0
            }
        },
        "expected_tool_flow": [
            {"tool": "create_transaction", "min_calls": 14},
            {"tool": "get_financial_summary", "min_calls": 1},
        ],
        "validation_queries": [
            "What is the total for each major category?",
            "What are the three highest expenses?",
            "What is the total monthly expense?",
            "What is the remaining balance?"
        ]
    },
    {
        "id": 9,
        "name": "Customer Onboarding and Delivery Workflow",
        "description": "Onboard a customer, start a project, track delivery work, and resolve support",
        "query": f"""Set up a lightweight delivery workflow for a new customer:

1. Create a customer named 'Northwind Labs' with email 'ops@northwind.example', tier 'enterprise', and payment terms of 15 days.
2. Create a project for that customer called 'Website Revamp' at an hourly rate of $180 with a budget of 120 hours.
3. Log two time entries on that project:
   - Alice: 6 hours for 'Discovery workshop'
   - Bob: 4.5 hours for 'UI prototype'
4. Create a high-priority support ticket for that customer with subject 'SSO login issue', then move it to 'resolved'.
5. Schedule a 60-minute kickoff meeting titled 'Northwind kickoff' for tomorrow with attendees:
   - ops@northwind.example
   - pm@agency.example

Then provide a summary showing the customer tier, total logged hours, total billable amount, current support ticket status, and the scheduled meeting date.""",
        "expected_state": {
            "customers_count": 1,
            "customer_names": ["Northwind Labs"],
            "customer_tiers": {"enterprise": 1},
            "projects_count": 1,
            "project_names": ["Website Revamp"],
            "project_logged_hours_total": 10.5,
            "project_billable_amount_total": 1890.0,
            "time_entries_count": 2,
            "support_ticket_statuses": {"resolved": 1},
            "meetings_count": 1,
            "meeting_titles": ["Northwind kickoff"],
            "meeting_dates": [get_date(1)],
        },
        "expected_tool_flow": [
            {"tool": "create_customer", "min_calls": 1},
            {"tool": "create_project", "min_calls": 1},
            {"tool": "log_time_entry", "min_calls": 2},
            {"tool": "create_support_ticket", "min_calls": 1},
            {"tool": "update_support_ticket", "min_calls": 1},
            {"tool": "schedule_meeting", "min_calls": 1},
        ],
        "validation_queries": [
            "How many customers and projects were created?",
            "What are the logged hours and billable amount for the project?",
            "What is the final support ticket status?",
            "When is the kickoff meeting scheduled?"
        ]
    },
    {
        "id": 10,
        "name": "Procurement Approval and Receiving",
        "description": "Create purchase orders, approve them, and receive part of the order set",
        "query": """Manage this procurement workflow:

1. Create a purchase order for 'Acme Hardware' with these line items:
   - 3 monitors at $220 each
   - 5 keyboards at $45 each
   - 2 docking stations at $180 each
2. Create a second purchase order for 'CloudHost LLC' with:
   - 1 annual hosting renewal at $1200
3. Approve both purchase orders.
4. Mark only the Acme Hardware purchase order as received.

Then provide a summary showing each purchase order status, the total committed spend, and which vendor is still awaiting delivery.""",
        "expected_state": {
            "purchase_orders_count": 2,
            "purchase_order_statuses": {"received": 1, "approved": 1},
            "purchase_order_vendors": ["Acme Hardware", "CloudHost LLC"],
            "total_purchase_order_amount": 2445.0,
        },
        "expected_tool_flow": [
            {"tool": "create_purchase_order", "min_calls": 2},
            {"tool": "approve_purchase_order", "min_calls": 2},
            {"tool": "receive_purchase_order", "min_calls": 1},
        ],
        "validation_queries": [
            "How many purchase orders were created?",
            "What is the status of each purchase order?",
            "What is the total committed spend?",
            "Which vendor is still pending receipt?"
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


def _normalized_rows(rows: List[Any]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            normalized.append(dict(row))
        elif is_dataclass(row):
            normalized.append(asdict(row))
        else:
            normalized.append(dict(getattr(row, "__dict__", {})))
    return normalized


def _append_check(
    checks: List[Dict[str, Any]],
    label: str,
    expected: Any,
    actual: Any,
    passed: bool,
) -> tuple[int, int]:
    checks.append(
        {
            "check": label,
            "expected": expected,
            "actual": actual,
            "passed": passed,
        }
    )
    return (1, 0) if passed else (0, 1)


def _approx_equal(a: Any, b: Any, tolerance: float = 0.01) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(float(a) - float(b)) < tolerance
    return a == b


def _normalize_category_label(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    lowered = value.strip().lower()
    aliases = {
        "rent": "rent",
        "utilities": "utilities",
        "utilities electricity": "utilities",
        "electricity": "utilities",
        "internet phone": "internet_phone",
        "internet": "internet",
        "office supplies": "office_supplies",
        "cleaning service": "cleaning_service",
        "social media ads": "social_media_ads",
        "marketing ads": "marketing",
        "content creation": "content_creation",
        "seo tools": "seo_tools",
        "software licenses": "software_licenses",
        "software subscriptions": "software_subscriptions",
        "cloud hosting": "cloud_hosting",
        "domain renewals": "domain_renewals",
        "online courses": "online_courses",
        "conference ticket": "conference_ticket",
        "professional development": "professional_development",
        "product sales": "product_sales",
        "referral bonus": "referral_income",
        "business lunch": "business_lunch",
    }
    cleaned = "".join(ch if ch.isalnum() else " " for ch in lowered)
    cleaned = " ".join(cleaned.split())
    return aliases.get(cleaned, cleaned.replace(" ", "_"))


def _account_balance(state_summary: Dict[str, Any], account_name: str) -> float:
    accounts = state_summary.get("accounts") or {}
    account = accounts.get(account_name) or {}
    value = account.get("balance")
    return float(value) if isinstance(value, (int, float)) else 0.0


def _invoice_status_counts(invoices: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for invoice in invoices:
        status = invoice.get("status")
        if isinstance(status, str):
            counts[status] = counts.get(status, 0) + 1
    return counts


def _status_counts(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        status = row.get("status")
        if isinstance(status, str):
            counts[status] = counts.get(status, 0) + 1
    return counts


def _unique_values(rows: List[Dict[str, Any]], key: str) -> List[str]:
    return sorted(
        {
            value
            for value in (row.get(key) for row in rows)
            if isinstance(value, str)
        }
    )


def _count_by_value(rows: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows:
        value = row.get(key)
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return counts


def _sum_numeric(rows: List[Dict[str, Any]], key: str) -> float:
    total = 0.0
    for row in rows:
        value = row.get(key)
        if isinstance(value, (int, float)):
            total += float(value)
    return round(total, 2)


def _transaction_type_counts(transactions: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for transaction in transactions:
        txn_type = transaction.get("type")
        if isinstance(txn_type, str):
            counts[txn_type] = counts.get(txn_type, 0) + 1
    return counts


def _category_totals(transactions: List[Dict[str, Any]], txn_type: str) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for transaction in transactions:
        if transaction.get("type") != txn_type:
            continue
        category = _normalize_category_label(transaction.get("category"))
        amount = transaction.get("amount")
        if category and isinstance(amount, (int, float)):
            totals[category] = round(totals.get(category, 0.0) + float(amount), 2)
    return totals


def _unique_invoice_clients(invoices: List[Dict[str, Any]]) -> List[str]:
    return sorted(
        {
            client
            for client in (invoice.get("client_name") for invoice in invoices)
            if isinstance(client, str)
        }
    )


def _major_expense_totals(transactions: List[Dict[str, Any]]) -> Dict[str, float]:
    category_map = {
        "rent": "office_related",
        "utilities": "office_related",
        "internet": "office_related",
        "internet_phone": "office_related",
        "office_supplies": "office_related",
        "cleaning_service": "office_related",
        "social_media_ads": "marketing",
        "content_creation": "marketing",
        "seo_tools": "marketing",
        "software_licenses": "operations",
        "cloud_hosting": "operations",
        "domain_renewals": "operations",
        "online_courses": "professional_development",
        "conference_ticket": "professional_development",
        "books": "professional_development",
    }
    totals: Dict[str, float] = {}
    for transaction in transactions:
        if transaction.get("type") != "expense":
            continue
        category = _normalize_category_label(transaction.get("category"))
        amount = transaction.get("amount")
        bucket = category_map.get(category)
        if bucket and isinstance(amount, (int, float)):
            totals[bucket] = round(totals.get(bucket, 0.0) + float(amount), 2)
    return totals


def validate_scenario_result(
    scenario_id: int,
    state_summary: Dict[str, Any],
    full_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
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

    transactions = _normalized_rows((full_state or {}).get("transactions", []))
    invoices = _normalized_rows((full_state or {}).get("invoices", []))
    customers = _normalized_rows((full_state or {}).get("customers", []))
    projects = _normalized_rows((full_state or {}).get("projects", []))
    time_entries = _normalized_rows((full_state or {}).get("time_entries", []))
    purchase_orders = _normalized_rows((full_state or {}).get("purchase_orders", []))
    support_tickets = _normalized_rows((full_state or {}).get("support_tickets", []))
    meetings = _normalized_rows((full_state or {}).get("meetings", []))

    if "total_transactions" in expected:
        actual = state_summary.get("total_transactions", 0)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact total transactions",
            expected["total_transactions"],
            actual,
            actual == expected["total_transactions"],
        )
        passed += gained_passed
        failed += gained_failed

    if "min_transactions" in expected:
        actual = state_summary.get("total_transactions", 0)
        gained_passed, gained_failed = _append_check(
            checks,
            f"Minimum {expected['min_transactions']} transactions",
            f">= {expected['min_transactions']}",
            actual,
            actual >= expected["min_transactions"],
        )
        passed += gained_passed
        failed += gained_failed

    if "total_invoices" in expected:
        actual = state_summary.get("total_invoices", 0)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact total invoices",
            expected["total_invoices"],
            actual,
            actual == expected["total_invoices"],
        )
        passed += gained_passed
        failed += gained_failed

    if "min_invoices" in expected:
        actual = state_summary.get("total_invoices", 0)
        gained_passed, gained_failed = _append_check(
            checks,
            f"Minimum {expected['min_invoices']} invoices",
            f">= {expected['min_invoices']}",
            actual,
            actual >= expected["min_invoices"],
        )
        passed += gained_passed
        failed += gained_failed

    for key, label in [
        ("total_income", "Exact total income"),
        ("total_expenses", "Exact total expenses"),
        ("net_income", "Exact net income"),
    ]:
        if key in expected:
            actual = float(state_summary.get(key, 0))
            gained_passed, gained_failed = _append_check(
                checks,
                label,
                f"${expected[key]}",
                f"${actual}",
                _approx_equal(actual, expected[key]),
            )
            passed += gained_passed
            failed += gained_failed

    for key, label in [
        ("total_income_min", "Minimum total income"),
        ("total_expenses_min", "Minimum total expenses"),
        ("net_income_min", "Minimum net income"),
    ]:
        if key in expected:
            summary_key = key.replace("_min", "")
            actual = float(state_summary.get(summary_key, 0))
            gained_passed, gained_failed = _append_check(
                checks,
                label,
                f">= ${expected[key]}",
                f"${actual}",
                actual >= float(expected[key]),
            )
            passed += gained_passed
            failed += gained_failed

    for key, account_name in [
        ("checking_balance", "checking"),
        ("savings_balance", "savings"),
    ]:
        if key in expected:
            actual = _account_balance(state_summary, account_name)
            gained_passed, gained_failed = _append_check(
                checks,
                f"Exact {account_name} balance",
                f"${expected[key]}",
                f"${actual}",
                _approx_equal(actual, expected[key]),
            )
            passed += gained_passed
            failed += gained_failed

    for key, account_name in [
        ("checking_balance_min", "checking"),
        ("checking_balance_max", "checking"),
    ]:
        if key in expected:
            actual = _account_balance(state_summary, account_name)
            is_min = key.endswith("_min")
            check_passed = actual >= expected[key] if is_min else actual <= expected[key]
            gained_passed, gained_failed = _append_check(
                checks,
                f"{'Minimum' if is_min else 'Maximum'} {account_name} balance",
                f"{'>=' if is_min else '<='} ${expected[key]}",
                f"${actual}",
                check_passed,
            )
            passed += gained_passed
            failed += gained_failed

    if "outstanding_receivables" in expected:
        actual = float(state_summary.get("outstanding_receivables", 0))
        gained_passed, gained_failed = _append_check(
            checks,
            "Outstanding receivables",
            f"${expected['outstanding_receivables']}",
            f"${actual}",
            _approx_equal(actual, expected["outstanding_receivables"]),
        )
        passed += gained_passed
        failed += gained_failed

    if transactions and "transaction_types" in expected:
        actual_counts = _transaction_type_counts(transactions)
        for txn_type, expected_count in expected["transaction_types"].items():
            actual = actual_counts.get(txn_type, 0)
            gained_passed, gained_failed = _append_check(
                checks,
                f"Transaction count for {txn_type}",
                expected_count,
                actual,
                actual == expected_count,
            )
            passed += gained_passed
            failed += gained_failed

    if invoices and "invoice_statuses" in expected:
        actual_statuses = _invoice_status_counts(invoices)
        for status, expected_count in expected["invoice_statuses"].items():
            actual = actual_statuses.get(status, 0)
            gained_passed, gained_failed = _append_check(
                checks,
                f"Invoice status count for {status}",
                expected_count,
                actual,
                actual == expected_count,
            )
            passed += gained_passed
            failed += gained_failed

    if invoices and "clients" in expected:
        actual_clients = _unique_invoice_clients(invoices)
        expected_clients = sorted(expected["clients"])
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact invoice client set",
            expected_clients,
            actual_clients,
            actual_clients == expected_clients,
        )
        passed += gained_passed
        failed += gained_failed

    if invoices and "total_invoice_amount" in expected:
        actual_total = round(
            sum(float(invoice.get("amount", 0.0)) for invoice in invoices), 2
        )
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact total invoice amount",
            f"${expected['total_invoice_amount']}",
            f"${actual_total}",
            _approx_equal(actual_total, expected["total_invoice_amount"]),
        )
        passed += gained_passed
        failed += gained_failed

    if invoices and "total_invoice_amount_min" in expected:
        actual_total = round(
            sum(float(invoice.get("amount", 0.0)) for invoice in invoices), 2
        )
        gained_passed, gained_failed = _append_check(
            checks,
            "Minimum total invoice amount",
            f">= ${expected['total_invoice_amount_min']}",
            f"${actual_total}",
            actual_total >= float(expected["total_invoice_amount_min"]),
        )
        passed += gained_passed
        failed += gained_failed

    if invoices and "invoice_paid_amount" in expected and len(invoices) == 1:
        actual_paid = float(invoices[0].get("paid_amount", 0.0))
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact invoice paid amount",
            f"${expected['invoice_paid_amount']}",
            f"${actual_paid}",
            _approx_equal(actual_paid, expected["invoice_paid_amount"]),
        )
        passed += gained_passed
        failed += gained_failed

    if invoices and "invoice_status" in expected and len(invoices) == 1:
        actual_status = invoices[0].get("status")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact invoice status",
            expected["invoice_status"],
            actual_status,
            actual_status == expected["invoice_status"],
        )
        passed += gained_passed
        failed += gained_failed

    if invoices and "total_paid" in expected:
        actual_paid = round(
            sum(float(invoice.get("paid_amount", 0.0)) for invoice in invoices), 2
        )
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact total paid across invoices",
            f"${expected['total_paid']}",
            f"${actual_paid}",
            _approx_equal(actual_paid, expected["total_paid"]),
        )
        passed += gained_passed
        failed += gained_failed

    if transactions and "transfer_count" in expected:
        transfer_rows = [t for t in transactions if t.get("type") == "transfer"]
        actual = len(transfer_rows)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact transfer transaction count",
            expected["transfer_count"],
            actual,
            actual == expected["transfer_count"],
        )
        passed += gained_passed
        failed += gained_failed

    if transactions and "total_transfers" in expected:
        transfer_rows = [t for t in transactions if t.get("type") == "transfer"]
        actual = len(transfer_rows) // 2
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact logical transfer count",
            expected["total_transfers"],
            actual,
            actual == expected["total_transfers"],
        )
        passed += gained_passed
        failed += gained_failed

    if transactions and "categories_count_min" in expected:
        categories = {
            category
            for category in (txn.get("category") for txn in transactions)
            if isinstance(category, str)
        }
        actual = len(categories)
        gained_passed, gained_failed = _append_check(
            checks,
            "Minimum distinct category count",
            f">= {expected['categories_count_min']}",
            actual,
            actual >= int(expected["categories_count_min"]),
        )
        passed += gained_passed
        failed += gained_failed

    if transactions and "highest_expense" in expected:
        expenses = [
            float(txn.get("amount", 0.0))
            for txn in transactions
            if txn.get("type") == "expense"
        ]
        actual = max(expenses) if expenses else 0.0
        gained_passed, gained_failed = _append_check(
            checks,
            "Highest individual expense",
            f"${expected['highest_expense']}",
            f"${actual}",
            _approx_equal(actual, expected["highest_expense"]),
        )
        passed += gained_passed
        failed += gained_failed

    if transactions and "category_totals" in expected:
        actual_totals = _major_expense_totals(transactions)
        for category, expected_total in expected["category_totals"].items():
            actual = actual_totals.get(category, 0.0)
            gained_passed, gained_failed = _append_check(
                checks,
                f"Major category total for {category}",
                f"${expected_total}",
                f"${actual}",
                _approx_equal(actual, expected_total),
            )
            passed += gained_passed
            failed += gained_failed

    if transactions and "categories" in expected:
        actual_categories = sorted(
            {
                _normalize_category_label(category)
                for category in (txn.get("category") for txn in transactions)
                if _normalize_category_label(category)
            }
        )
        expected_categories = sorted(_normalize_category_label(category) for category in expected["categories"])
        gained_passed, gained_failed = _append_check(
            checks,
            "Required transaction categories present",
            expected_categories,
            actual_categories,
            all(category in actual_categories for category in expected_categories),
        )
        passed += gained_passed
        failed += gained_failed

    if "customers_count" in expected:
        actual = len(customers)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact customer count",
            expected["customers_count"],
            actual,
            actual == expected["customers_count"],
        )
        passed += gained_passed
        failed += gained_failed

    if customers and "customer_names" in expected:
        actual_names = _unique_values(customers, "name")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact customer name set",
            sorted(expected["customer_names"]),
            actual_names,
            actual_names == sorted(expected["customer_names"]),
        )
        passed += gained_passed
        failed += gained_failed

    if customers and "customer_tiers" in expected:
        actual_tiers = _count_by_value(customers, "tier")
        for tier, expected_count in expected["customer_tiers"].items():
            actual = actual_tiers.get(tier, 0)
            gained_passed, gained_failed = _append_check(
                checks,
                f"Customer tier count for {tier}",
                expected_count,
                actual,
                actual == expected_count,
            )
            passed += gained_passed
            failed += gained_failed

    if "projects_count" in expected:
        actual = len(projects)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact project count",
            expected["projects_count"],
            actual,
            actual == expected["projects_count"],
        )
        passed += gained_passed
        failed += gained_failed

    if projects and "project_names" in expected:
        actual_names = _unique_values(projects, "name")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact project name set",
            sorted(expected["project_names"]),
            actual_names,
            actual_names == sorted(expected["project_names"]),
        )
        passed += gained_passed
        failed += gained_failed

    if projects and "project_logged_hours_total" in expected:
        actual = _sum_numeric(projects, "logged_hours")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact total project logged hours",
            expected["project_logged_hours_total"],
            actual,
            _approx_equal(actual, expected["project_logged_hours_total"]),
        )
        passed += gained_passed
        failed += gained_failed

    if projects and "project_billable_amount_total" in expected:
        actual = _sum_numeric(projects, "billable_amount")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact total project billable amount",
            f"${expected['project_billable_amount_total']}",
            f"${actual}",
            _approx_equal(actual, expected["project_billable_amount_total"]),
        )
        passed += gained_passed
        failed += gained_failed

    if "time_entries_count" in expected:
        actual = len(time_entries)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact time entry count",
            expected["time_entries_count"],
            actual,
            actual == expected["time_entries_count"],
        )
        passed += gained_passed
        failed += gained_failed

    if support_tickets and "support_ticket_statuses" in expected:
        actual_statuses = _status_counts(support_tickets)
        for status, expected_count in expected["support_ticket_statuses"].items():
            actual = actual_statuses.get(status, 0)
            gained_passed, gained_failed = _append_check(
                checks,
                f"Support ticket status count for {status}",
                expected_count,
                actual,
                actual == expected_count,
            )
            passed += gained_passed
            failed += gained_failed

    if "meetings_count" in expected:
        actual = len(meetings)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact meeting count",
            expected["meetings_count"],
            actual,
            actual == expected["meetings_count"],
        )
        passed += gained_passed
        failed += gained_failed

    if meetings and "meeting_titles" in expected:
        actual_titles = _unique_values(meetings, "title")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact meeting title set",
            sorted(expected["meeting_titles"]),
            actual_titles,
            actual_titles == sorted(expected["meeting_titles"]),
        )
        passed += gained_passed
        failed += gained_failed

    if meetings and "meeting_dates" in expected:
        actual_dates = _unique_values(meetings, "date")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact meeting date set",
            sorted(expected["meeting_dates"]),
            actual_dates,
            actual_dates == sorted(expected["meeting_dates"]),
        )
        passed += gained_passed
        failed += gained_failed

    if "purchase_orders_count" in expected:
        actual = len(purchase_orders)
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact purchase order count",
            expected["purchase_orders_count"],
            actual,
            actual == expected["purchase_orders_count"],
        )
        passed += gained_passed
        failed += gained_failed

    if purchase_orders and "purchase_order_statuses" in expected:
        actual_statuses = _status_counts(purchase_orders)
        for status, expected_count in expected["purchase_order_statuses"].items():
            actual = actual_statuses.get(status, 0)
            gained_passed, gained_failed = _append_check(
                checks,
                f"Purchase order status count for {status}",
                expected_count,
                actual,
                actual == expected_count,
            )
            passed += gained_passed
            failed += gained_failed

    if purchase_orders and "purchase_order_vendors" in expected:
        actual_vendors = _unique_values(purchase_orders, "vendor_name")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact purchase order vendor set",
            sorted(expected["purchase_order_vendors"]),
            actual_vendors,
            actual_vendors == sorted(expected["purchase_order_vendors"]),
        )
        passed += gained_passed
        failed += gained_failed

    if purchase_orders and "total_purchase_order_amount" in expected:
        actual = _sum_numeric(purchase_orders, "total_amount")
        gained_passed, gained_failed = _append_check(
            checks,
            "Exact total purchase order amount",
            f"${expected['total_purchase_order_amount']}",
            f"${actual}",
            _approx_equal(actual, expected["total_purchase_order_amount"]),
        )
        passed += gained_passed
        failed += gained_failed

    return {
        "valid": failed == 0,
        "scenario_id": scenario_id,
        "scenario_name": scenario["name"],
        "checks": checks,
        "passed": passed,
        "failed": failed,
        "total_checks": len(checks)
    }
