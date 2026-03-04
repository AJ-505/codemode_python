"""
Unified tools module combining accounting and business operations.

This module provides:
1. Tool registry: Dictionary of all available tools
2. Tool schemas: JSON schemas for traditional function calling (Regular Agent)
3. Code Mode API: Python API definitions with TypedDict response schemas (Code Mode Agent)

The API definitions include:
- Typed function signatures
- Detailed docstrings
- Example return values with correct JSON structure
- TypedDict definitions for response types

This ensures the Code Mode agent can generate correctly-typed code on the first try.
"""

import json
from typing import Dict, List, Any, Callable
from tools.accounting_tools import (
    create_transaction,
    create_invoice,
    update_invoice_status,
    record_partial_payment,
    get_transactions,
    get_invoices,
    get_financial_summary,
    transfer_between_accounts,
    get_account_balance,
    get_state_summary,
    reset_state,
    create_customer,
    get_customers,
    create_project,
    log_time_entry,
    create_purchase_order,
    approve_purchase_order,
    receive_purchase_order,
    create_support_ticket,
    update_support_ticket,
    schedule_meeting,
    simulate_transient_failure,
    state
)


# Tool registry
TOOLS: Dict[str, Callable] = {
    "create_transaction": create_transaction,
    "create_invoice": create_invoice,
    "update_invoice_status": update_invoice_status,
    "record_partial_payment": record_partial_payment,
    "get_transactions": get_transactions,
    "get_invoices": get_invoices,
    "get_financial_summary": get_financial_summary,
    "transfer_between_accounts": transfer_between_accounts,
    "get_account_balance": get_account_balance,
    "get_state_summary": get_state_summary,
    "reset_state": reset_state,
    "create_customer": create_customer,
    "get_customers": get_customers,
    "create_project": create_project,
    "log_time_entry": log_time_entry,
    "create_purchase_order": create_purchase_order,
    "approve_purchase_order": approve_purchase_order,
    "receive_purchase_order": receive_purchase_order,
    "create_support_ticket": create_support_ticket,
    "update_support_ticket": update_support_ticket,
    "schedule_meeting": schedule_meeting,
    "simulate_transient_failure": simulate_transient_failure,
}


def get_tools() -> Dict[str, Callable]:
    """Return the dictionary of available tools."""
    return TOOLS


TOOL_PATHS: Dict[str, str] = {
    "create_transaction": "/accounting/create_transaction",
    "create_invoice": "/accounting/create_invoice",
    "update_invoice_status": "/accounting/update_invoice_status",
    "record_partial_payment": "/accounting/record_partial_payment",
    "get_transactions": "/accounting/get_transactions",
    "get_invoices": "/accounting/get_invoices",
    "get_financial_summary": "/accounting/get_financial_summary",
    "transfer_between_accounts": "/accounting/transfer_between_accounts",
    "get_account_balance": "/accounting/get_account_balance",
    "get_state_summary": "/accounting/get_state_summary",
    "reset_state": "/system/reset_state",
    "create_customer": "/crm/create_customer",
    "get_customers": "/crm/get_customers",
    "create_project": "/projects/create_project",
    "log_time_entry": "/projects/log_time_entry",
    "create_purchase_order": "/procurement/create_purchase_order",
    "approve_purchase_order": "/procurement/approve_purchase_order",
    "receive_purchase_order": "/procurement/receive_purchase_order",
    "create_support_ticket": "/support/create_support_ticket",
    "update_support_ticket": "/support/update_support_ticket",
    "schedule_meeting": "/calendar/schedule_meeting",
    "simulate_transient_failure": "/system/simulate_transient_failure",
}


def get_tool_fs_manifest() -> Dict[str, Dict[str, Any]]:
    """Return a virtual-filesystem manifest for progressive tool discovery."""
    by_name = {schema["name"]: schema for schema in get_tool_schemas()}
    manifest: Dict[str, Dict[str, Any]] = {}
    for tool_name, tool in TOOLS.items():
        schema = by_name.get(tool_name, {})
        path = TOOL_PATHS.get(tool_name, f"/tools/{tool_name}")
        manifest[path] = {
            "name": tool_name,
            "path": path,
            "description": schema.get("description", ""),
            "input_schema": schema.get("input_schema", {"type": "object", "properties": {}, "required": []}),
            "group": path.strip("/").split("/", 1)[0] if path.strip("/") else "tools",
        }
    return manifest


def get_tool_schemas() -> List[Dict[str, Any]]:
    """
    Return tool schemas for traditional function calling (Regular Agent).
    """
    return [
        {
            "name": "create_transaction",
            "description": "Create a new financial transaction (income, expense, or transfer). IMPORTANT: The amount parameter must ALWAYS be a positive number, regardless of transaction type. The system automatically handles debits/credits based on transaction_type.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "transaction_type": {
                        "type": "string",
                        "enum": ["income", "expense", "transfer"],
                        "description": "Type of transaction"
                    },
                    "category": {
                        "type": "string",
                        "description": "Transaction category (salary, rent, utilities, consulting, etc.)"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Transaction amount - MUST be a positive number. For expenses, pass the positive amount (e.g., 2500 for a $2500 expense, not -2500). The system will automatically debit the account.",
                        "minimum": 0.01
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the transaction"
                    },
                    "account": {
                        "type": "string",
                        "enum": ["checking", "savings", "business_credit"],
                        "description": "Account name",
                        "default": "checking"
                    },
                    "date": {
                        "type": "string",
                        "description": "Transaction date (ISO format YYYY-MM-DD), defaults to today"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags"
                    }
                },
                "required": ["transaction_type", "category", "amount", "description"]
            }
        },
        {
            "name": "create_invoice",
            "description": "Create a new invoice for a client",
            "input_schema": {
                "type": "object",
                "properties": {
                    "client_name": {
                        "type": "string",
                        "description": "Name of the client"
                    },
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "quantity": {"type": "number"},
                                "price": {"type": "number"}
                            },
                            "required": ["description", "quantity", "price"]
                        },
                        "description": "List of invoice items"
                    },
                    "due_days": {
                        "type": "integer",
                        "description": "Number of days until payment is due",
                        "default": 30
                    },
                    "issue_date": {
                        "type": "string",
                        "description": "Invoice issue date (ISO format), defaults to today"
                    }
                },
                "required": ["client_name", "items"]
            }
        },
        {
            "name": "update_invoice_status",
            "description": "Update the status of an invoice",
            "input_schema": {
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "Invoice ID (e.g., INV00001)"
                    },
                    "new_status": {
                        "type": "string",
                        "enum": ["draft", "sent", "paid", "overdue", "cancelled"],
                        "description": "New invoice status"
                    }
                },
                "required": ["invoice_id", "new_status"]
            }
        },
        {
            "name": "record_partial_payment",
            "description": "Record a partial payment for an invoice",
            "input_schema": {
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "Invoice ID"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Payment amount"
                    }
                },
                "required": ["invoice_id", "amount"]
            }
        },
        {
            "name": "get_transactions",
            "description": "Query transactions with optional filters",
            "input_schema": {
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "description": "Filter by account name"
                    },
                    "transaction_type": {
                        "type": "string",
                        "enum": ["income", "expense", "transfer"],
                        "description": "Filter by transaction type"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Filter by start date (ISO format)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Filter by end date (ISO format)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (any match)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_invoices",
            "description": "Query invoices with optional filters",
            "input_schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["draft", "sent", "paid", "overdue", "cancelled"],
                        "description": "Filter by invoice status"
                    },
                    "client_name": {
                        "type": "string",
                        "description": "Filter by client name (partial match)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_financial_summary",
            "description": "Get a financial summary with income, expenses, and breakdown by category",
            "input_schema": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date for summary (ISO format)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for summary (ISO format)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "transfer_between_accounts",
            "description": "Transfer money between accounts",
            "input_schema": {
                "type": "object",
                "properties": {
                    "from_account": {
                        "type": "string",
                        "enum": ["checking", "savings", "business_credit"],
                        "description": "Source account"
                    },
                    "to_account": {
                        "type": "string",
                        "enum": ["checking", "savings", "business_credit"],
                        "description": "Destination account"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Transfer amount"
                    },
                    "description": {
                        "type": "string",
                        "description": "Transfer description"
                    }
                },
                "required": ["from_account", "to_account", "amount"]
            }
        },
        {
            "name": "get_account_balance",
            "description": "Get the current balance of an account",
            "input_schema": {
                "type": "object",
                "properties": {
                    "account": {
                        "type": "string",
                        "enum": ["checking", "savings", "business_credit"],
                        "description": "Account name"
                    }
                },
                "required": ["account"]
            }
        },
        {
            "name": "get_state_summary",
            "description": "Get a complete summary of the current accounting state including all accounts, transactions, and invoices",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "reset_state",
            "description": "Reset all accounting state to initial values (for testing)",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "create_customer",
            "description": "Create a customer profile with billing terms",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "tier": {"type": "string"},
                    "payment_terms_days": {"type": "integer"}
                },
                "required": ["name", "email"]
            }
        },
        {
            "name": "get_customers",
            "description": "List customer profiles with optional filters",
            "input_schema": {
                "type": "object",
                "properties": {
                    "tier": {"type": "string"},
                    "active_only": {"type": "boolean"}
                },
                "required": []
            }
        },
        {
            "name": "create_project",
            "description": "Create a project linked to a customer",
            "input_schema": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "name": {"type": "string"},
                    "hourly_rate": {"type": "number"},
                    "budget_hours": {"type": "number"}
                },
                "required": ["customer_id", "name", "hourly_rate", "budget_hours"]
            }
        },
        {
            "name": "log_time_entry",
            "description": "Log billable time against a project",
            "input_schema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "person": {"type": "string"},
                    "hours": {"type": "number"},
                    "description": {"type": "string"}
                },
                "required": ["project_id", "person", "hours", "description"]
            }
        },
        {
            "name": "create_purchase_order",
            "description": "Create a purchase order draft",
            "input_schema": {
                "type": "object",
                "properties": {
                    "vendor_name": {"type": "string"},
                    "items": {"type": "array", "items": {"type": "object"}},
                    "currency": {"type": "string"}
                },
                "required": ["vendor_name", "items"]
            }
        },
        {
            "name": "approve_purchase_order",
            "description": "Approve a purchase order",
            "input_schema": {
                "type": "object",
                "properties": {
                    "po_id": {"type": "string"}
                },
                "required": ["po_id"]
            }
        },
        {
            "name": "receive_purchase_order",
            "description": "Mark a purchase order as received",
            "input_schema": {
                "type": "object",
                "properties": {
                    "po_id": {"type": "string"}
                },
                "required": ["po_id"]
            }
        },
        {
            "name": "create_support_ticket",
            "description": "Create a support ticket for a customer",
            "input_schema": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string"},
                    "subject": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
                },
                "required": ["customer_id", "subject"]
            }
        },
        {
            "name": "update_support_ticket",
            "description": "Update support ticket lifecycle status",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string"},
                    "new_status": {"type": "string", "enum": ["open", "in_progress", "blocked", "resolved", "closed"]}
                },
                "required": ["ticket_id", "new_status"]
            }
        },
        {
            "name": "schedule_meeting",
            "description": "Schedule a customer or internal meeting",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "attendees": {"type": "array", "items": {"type": "string"}},
                    "date": {"type": "string"},
                    "duration_minutes": {"type": "integer"}
                },
                "required": ["title", "attendees", "date"]
            }
        },
        {
            "name": "simulate_transient_failure",
            "description": "Failure-injection tool for resilience testing; fails for first N calls",
            "input_schema": {
                "type": "object",
                "properties": {
                    "operation_key": {"type": "string"},
                    "fail_times": {"type": "integer"},
                    "reset": {"type": "boolean"}
                },
                "required": ["operation_key"]
            }
        }
    ]


def get_code_mode_api() -> str:
    """
    Return Python API definitions for Code Mode Agent with typed response schemas.

    This string contains:
    - TypedDict definitions showing exact response structures
    - Function signatures with full type hints
    - Detailed docstrings with example return values
    - Important notes about JSON parsing

    The Code Mode agent uses this to understand:
    1. What parameters each tool accepts
    2. What the return value structure looks like
    3. How to correctly parse and access nested data

    Returns:
        Python code string defining the Tools class and response types
    """
    return '''
from typing import TypedDict, List, Literal, Dict

# ============================================================================
# Response Type Definitions
# ============================================================================
# These TypedDicts show the exact structure of JSON responses from each tool.
# All tools return JSON strings that must be parsed with json.loads().

# Nested structure types
class InvoiceItemDict(TypedDict):
    """Structure of an invoice item"""
    description: str
    quantity: float
    price: float

class InvoiceDict(TypedDict):
    """Structure of an invoice object"""
    id: str  # e.g., "INV00001"
    client_name: str
    amount: float  # Total invoice amount
    issue_date: str  # ISO format date
    due_date: str  # ISO format date
    status: Literal["draft", "sent", "paid", "overdue", "cancelled"]
    items: List[InvoiceItemDict]
    paid_amount: float  # Amount paid so far

class TransactionDict(TypedDict):
    """Structure of a transaction object"""
    id: str  # e.g., "TXN00001"
    date: str  # ISO format date
    type: Literal["income", "expense", "transfer"]
    category: str
    amount: float  # Positive for income, negative for expenses
    description: str
    account: str
    tags: List[str]

class PeriodDict(TypedDict):
    """Date range period for financial summaries"""
    start_date: str  # ISO format date or "beginning"
    end_date: str  # ISO format date or "now"

class FinancialSummaryDict(TypedDict):
    """Financial summary with income/expense breakdown"""
    total_income: float
    total_expenses: float
    net_income: float
    income_by_category: Dict[str, float]  # e.g., {"consulting": 5000.0, "product_sales": 1500.0}
    expense_by_category: Dict[str, float]  # e.g., {"rent": 2500.0, "utilities": 150.0}
    transaction_count: int

class AccountBalancesDict(TypedDict):
    """Account balances - values are floats, not nested objects"""
    checking: float
    savings: float
    business_credit: float

class InvoicesByStatusDict(TypedDict, total=False):
    """Count of invoices by status - keys may not all be present"""
    draft: int
    sent: int
    paid: int
    overdue: int
    cancelled: int

class NewBalancesDict(TypedDict):
    """Updated balances after a transfer between two accounts"""
    # Keys are dynamic account names like "checking", "savings", etc.
    # This is a Dict[str, float] at runtime

class StateSummaryDict(TypedDict):
    """Complete accounting state summary"""
    accounts: Dict[str, Dict[str, any]]  # {"checking": {"balance": 10000.0, "type": "checking"}}
    total_transactions: int
    total_income: float
    total_expenses: float
    net_income: float
    total_invoices: int
    invoices_by_status: InvoicesByStatusDict
    outstanding_receivables: float

class AccountInfoDict(TypedDict):
    """Account information with balance and type"""
    balance: float
    type: Literal["checking", "savings", "credit"]

# Response types
class TransactionResponse(TypedDict):
    """Response from create_transaction"""
    status: Literal["success"]
    transaction: TransactionDict
    new_balance: float  # Updated account balance after transaction

class InvoiceResponse(TypedDict):
    """Response from create_invoice"""
    status: Literal["success"]
    invoice: InvoiceDict

class InvoiceUpdateResponse(TypedDict):
    """Response from update_invoice_status"""
    status: Literal["success"]
    invoice_id: str
    old_status: str
    new_status: str
    invoice: InvoiceDict

class PartialPaymentResponse(TypedDict):
    """Response from record_partial_payment"""
    status: Literal["success"]
    invoice_id: str
    payment_amount: float
    total_paid: float
    remaining: float
    invoice: InvoiceDict

class TransactionsQueryResponse(TypedDict):
    """Response from get_transactions"""
    status: Literal["success"]
    count: int
    transactions: List[TransactionDict]

class InvoicesQueryResponse(TypedDict):
    """Response from get_invoices"""
    status: Literal["success"]
    count: int
    invoices: List[InvoiceDict]

class FinancialSummaryResponse(TypedDict):
    """Response from get_financial_summary"""
    status: Literal["success"]
    period: PeriodDict
    summary: FinancialSummaryDict
    accounts: AccountBalancesDict

class TransferResponse(TypedDict):
    """Response from transfer_between_accounts"""
    status: Literal["success"]
    from_account: str
    to_account: str
    amount: float
    new_balances: Dict[str, float]  # e.g., {"checking": 5000.0, "savings": 65000.0}
    transaction_ids: List[str]  # e.g., ["TXN00001", "TXN00002"]

class AccountBalanceResponse(TypedDict):
    """Response from get_account_balance"""
    status: Literal["success"]
    account: str
    balance: float
    type: Literal["checking", "savings", "credit"]

class StateSummaryResponse(TypedDict):
    """Response from get_state_summary"""
    status: Literal["success"]
    summary: StateSummaryDict

class ResetResponse(TypedDict):
    """Response from reset_state"""
    status: Literal["success"]
    message: str

class ErrorResponse(TypedDict):
    """Error response from any tool"""
    error: str


# ============================================================================
# Tools API
# ============================================================================

class Tools:
    """Available business and accounting tools."""

    def create_transaction(
        self,
        transaction_type: Literal["income", "expense", "transfer"],
        category: str,
        amount: float,
        description: str,
        account: Literal["checking", "savings", "business_credit"] = "checking",
        date: str = None,
        tags: List[str] = None
    ) -> str:
        """
        Create a new financial transaction.

        Args:
            transaction_type: Type of transaction ('income', 'expense', 'transfer')
            category: Transaction category (e.g., 'salary', 'rent', 'utilities', 'consulting')
            amount: Transaction amount (positive number)
            description: Description of the transaction
            account: Account name ('checking', 'savings', 'business_credit')
            date: Transaction date (ISO format YYYY-MM-DD), defaults to today
            tags: Optional list of tags

        Returns:
            JSON string that parses to TransactionResponse.
            After parsing: result["transaction"] is a TransactionDict
            and result["new_balance"] is a float.

            Example parsed structure:
            {
                "status": "success",
                "transaction": {
                    "id": "TXN00001",
                    "date": "2025-10-09",
                    "type": "income",
                    "category": "consulting",
                    "amount": 5000.0,
                    "description": "...",
                    "account": "checking",
                    "tags": []
                },
                "new_balance": 12500.0
            }

            Usage:
            result_str = tools.create_transaction("income", "consulting", 5000.0, "Payment received")
            result: TransactionResponse = json.loads(result_str)
            new_balance: float = result["new_balance"]
            transaction_id: str = result["transaction"]["id"]
        """
        pass

    def create_invoice(
        self,
        client_name: str,
        items: List[InvoiceItemDict],
        due_days: int = 30,
        issue_date: str = None
    ) -> str:
        """
        Create a new invoice for a client.

        Args:
            client_name: Name of the client
            items: List of InvoiceItemDict with 'description', 'quantity', and 'price'
                   Example: [{"description": "Consulting", "quantity": 10, "price": 150.0}]
            due_days: Number of days until payment is due
            issue_date: Invoice issue date (ISO format), defaults to today

        Returns:
            JSON string that parses to InvoiceResponse.
            After parsing: result["invoice"] is an InvoiceDict.

            Example parsed structure:
            {
                "status": "success",
                "invoice": {
                    "id": "INV00001",
                    "client_name": "Acme Corp",
                    "amount": 15000.0,
                    "issue_date": "2025-10-09",
                    "due_date": "2025-11-08",
                    "status": "draft",
                    "items": [{"description": "...", "quantity": 10, "price": 150.0}],
                    "paid_amount": 0.0
                }
            }

            Usage:
            items = [{"description": "Consulting", "quantity": 10, "price": 150.0}]
            result_str = tools.create_invoice("Acme Corp", items)
            result: InvoiceResponse = json.loads(result_str)
            invoice_id: str = result["invoice"]["id"]
            invoice_amount: float = result["invoice"]["amount"]
        """
        pass

    def update_invoice_status(
        self,
        invoice_id: str,
        new_status: Literal["draft", "sent", "paid", "overdue", "cancelled"]
    ) -> str:
        """
        Update the status of an invoice.

        Args:
            invoice_id: Invoice ID (e.g., 'INV00001')
            new_status: New status ('draft', 'sent', 'paid', 'overdue', 'cancelled')

        Returns:
            JSON string that parses to InvoiceUpdateResponse.

            Example parsed structure:
            {
                "status": "success",
                "invoice_id": "INV00001",
                "old_status": "draft",
                "new_status": "sent",
                "invoice": {...}  # Full InvoiceDict
            }

            Usage:
            result_str = tools.update_invoice_status("INV00001", "sent")
            result: InvoiceUpdateResponse = json.loads(result_str)
            updated_invoice: InvoiceDict = result["invoice"]
        """
        pass

    def record_partial_payment(self, invoice_id: str, amount: float) -> str:
        """
        Record a partial payment for an invoice.

        Args:
            invoice_id: Invoice ID (e.g., 'INV00001')
            amount: Payment amount

        Returns:
            JSON string that parses to PartialPaymentResponse.

            Example parsed structure:
            {
                "status": "success",
                "invoice_id": "INV00001",
                "payment_amount": 5000.0,
                "total_paid": 5000.0,
                "remaining": 8000.0,
                "invoice": {...}  # Full InvoiceDict
            }

            Usage:
            result_str = tools.record_partial_payment("INV00001", 5000.0)
            result: PartialPaymentResponse = json.loads(result_str)
            remaining: float = result["remaining"]
            total_paid: float = result["total_paid"]
        """
        pass

    def get_transactions(
        self,
        account: Literal["checking", "savings", "business_credit"] = None,
        transaction_type: Literal["income", "expense", "transfer"] = None,
        category: str = None,
        start_date: str = None,
        end_date: str = None,
        tags: List[str] = None
    ) -> str:
        """
        Query transactions with filters.

        Args:
            account: Filter by account name
            transaction_type: Filter by type ('income', 'expense', 'transfer')
            category: Filter by category
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            tags: Filter by tags (any match)

        Returns:
            JSON string that parses to TransactionsQueryResponse.

            Example parsed structure:
            {
                "status": "success",
                "count": 5,
                "transactions": [
                    {"id": "TXN00001", "type": "income", "amount": 5000.0, ...},
                    {"id": "TXN00002", "type": "expense", "amount": 2500.0, ...}
                ]
            }

            Usage:
            result_str = tools.get_transactions(transaction_type="income")
            result: TransactionsQueryResponse = json.loads(result_str)
            transactions: List[TransactionDict] = result["transactions"]
            for txn in transactions:
                print(f"Transaction {txn['id']}: ${txn['amount']}")
        """
        pass

    def get_invoices(
        self,
        status: Literal["draft", "sent", "paid", "overdue", "cancelled"] = None,
        client_name: str = None
    ) -> str:
        """
        Query invoices with filters.

        Args:
            status: Filter by status
            client_name: Filter by client name (partial match)

        Returns:
            JSON string that parses to InvoicesQueryResponse.

            Example parsed structure:
            {
                "status": "success",
                "count": 2,
                "invoices": [
                    {
                        "id": "INV00001",
                        "client_name": "Acme Corp",
                        "amount": 13000.0,
                        "status": "sent",
                        "paid_amount": 0.0,
                        "issue_date": "2025-10-09",
                        "due_date": "2025-11-08",
                        "items": [...]
                    }
                ]
            }

            Usage:
            result_str = tools.get_invoices(status="sent")
            result: InvoicesQueryResponse = json.loads(result_str)
            invoices: List[InvoiceDict] = result["invoices"]
            for inv in invoices:
                print(f"Invoice {inv['id']}: ${inv['amount']}")
        """
        pass

    def get_financial_summary(self, start_date: str = None, end_date: str = None) -> str:
        """
        Get a financial summary with income/expense breakdown.

        Args:
            start_date: Start date (ISO format YYYY-MM-DD)
            end_date: End date (ISO format YYYY-MM-DD)

        Returns:
            JSON string that parses to FinancialSummaryResponse.

            Example parsed structure:
            {
                "status": "success",
                "period": {
                    "start_date": "2025-01-01",
                    "end_date": "2025-12-31"
                },
                "summary": {
                    "total_income": 26000.0,
                    "total_expenses": 10650.0,
                    "net_income": 15350.0,
                    "income_by_category": {
                        "consulting": 12000.0,
                        "product_sales": 8000.0,
                        "invoice_payment": 6000.0
                    },
                    "expense_by_category": {
                        "rent": 7500.0,
                        "utilities": 650.0,
                        "marketing": 1200.0,
                        "software": 400.0,
                        "travel": 800.0,
                        "supplies": 100.0
                    },
                    "transaction_count": 15
                },
                "accounts": {
                    "checking": 12500.0,
                    "savings": 50000.0,
                    "business_credit": 0.0
                }
            }

            Usage:
            result_str = tools.get_financial_summary()
            result: FinancialSummaryResponse = json.loads(result_str)
            summary: FinancialSummaryDict = result["summary"]
            total_income: float = summary["total_income"]
            checking_balance: float = result["accounts"]["checking"]
            income_by_cat: Dict[str, float] = summary["income_by_category"]
        """
        pass

    def transfer_between_accounts(
        self,
        from_account: Literal["checking", "savings", "business_credit"],
        to_account: Literal["checking", "savings", "business_credit"],
        amount: float,
        description: str = ""
    ) -> str:
        """
        Transfer money between accounts.

        Args:
            from_account: Source account ('checking', 'savings', 'business_credit')
            to_account: Destination account ('checking', 'savings', 'business_credit')
            amount: Transfer amount (positive number)
            description: Transfer description

        Returns:
            JSON string that parses to TransferResponse.

            Example parsed structure:
            {
                "status": "success",
                "from_account": "checking",
                "to_account": "savings",
                "amount": 20000.0,
                "new_balances": {
                    "checking": 5000.0,
                    "savings": 70000.0
                },
                "transaction_ids": ["TXN00005", "TXN00006"]
            }

            Usage:
            result_str = tools.transfer_between_accounts("checking", "savings", 20000.0, "Emergency fund")
            result: TransferResponse = json.loads(result_str)
            new_checking: float = result["new_balances"]["checking"]
            new_savings: float = result["new_balances"]["savings"]
        """
        pass

    def get_account_balance(self, account: Literal["checking", "savings", "business_credit"]) -> str:
        """
        Get the current balance of an account.

        Args:
            account: Account name ('checking', 'savings', 'business_credit')

        Returns:
            JSON string that parses to AccountBalanceResponse.

            Example parsed structure:
            {
                "status": "success",
                "account": "checking",
                "balance": 12500.0,
                "type": "checking"
            }

            Usage:
            result_str = tools.get_account_balance("checking")
            result: AccountBalanceResponse = json.loads(result_str)
            balance: float = result["balance"]
        """
        pass

    def get_state_summary(self) -> str:
        """
        Get a complete summary of the current accounting state.

        Returns:
            JSON string that parses to StateSummaryResponse.

            Example parsed structure:
            {
                "status": "success",
                "summary": {
                    "accounts": {
                        "checking": {"balance": 10000.0, "type": "checking"},
                        "savings": {"balance": 50000.0, "type": "savings"},
                        "business_credit": {"balance": 0.0, "type": "credit"}
                    },
                    "total_transactions": 10,
                    "total_income": 26000.0,
                    "total_expenses": 10650.0,
                    "net_income": 15350.0,
                    "total_invoices": 3,
                    "invoices_by_status": {"draft": 1, "sent": 1, "paid": 1},
                    "outstanding_receivables": 8500.0
                }
            }

            Usage:
            result_str = tools.get_state_summary()
            result: StateSummaryResponse = json.loads(result_str)
            summary: StateSummaryDict = result["summary"]
            total_income: float = summary["total_income"]
            checking_info: Dict[str, any] = summary["accounts"]["checking"]
            checking_balance: float = checking_info["balance"]
        """
        pass

    def reset_state(self) -> str:
        """
        Reset all accounting state to initial values (for testing).

        Returns:
            JSON string that parses to ResetResponse.

            Example parsed structure:
            {
                "status": "success",
                "message": "State has been reset"
            }

            Usage:
            result_str = tools.reset_state()
            result: ResetResponse = json.loads(result_str)
            print(result["message"])
        """
        pass

# Runtime note:
# The sandbox already provides a pre-initialized `tools` object.
# Do not instantiate Tools() inside generated code.
# tools = Tools()
    '''


def get_code_mode_api_compact() -> str:
    """
    Return a compact Python API reference for Code Mode.

    This keeps token footprint low while preserving the fields the model needs
    for first-pass correctness.
    """
    return '''
# Code Mode tool contract:
# - Default strategy: progressive discovery via tools.ls/read/call
# - Fast path: direct tool methods when names/params are already known
#
# Sandbox constraints:
# - Use only "import json" (other imports are blocked)
# - Do not use private names (starting with "_")
# - Do not call getattr()
# - Do not use str.format(); use f-strings or "%" formatting

class Tools:
    # Progressive discovery API
    def ls(self, path="/") -> str: ...
    def read(self, path) -> str: ...
    def call(self, path, args=None) -> str: ...

    # Direct methods (low latency when already known)
    def create_transaction(self, transaction_type, category, amount, description, account="checking", date=None, tags=None) -> str: ...
    def create_invoice(self, client_name, items, due_days=30, issue_date=None) -> str: ...
    def update_invoice_status(self, invoice_id, new_status) -> str: ...
    def record_partial_payment(self, invoice_id, amount) -> str: ...
    def get_transactions(self, account=None, transaction_type=None, category=None, start_date=None, end_date=None, tags=None) -> str: ...
    def get_invoices(self, status=None, client_name=None) -> str: ...
    def get_financial_summary(self, start_date=None, end_date=None) -> str: ...
    def transfer_between_accounts(self, from_account, to_account, amount, description="") -> str: ...
    def get_account_balance(self, account) -> str: ...
    def get_state_summary(self) -> str: ...
    def reset_state(self) -> str: ...
    # Additional domain tools are discoverable through tools.ls/read/call.

# Path map (for tools.call):
# /accounting/*: transactions, invoices, balances, summaries
# /crm/*: customers
# /projects/*: projects and time entries
# /procurement/*: purchase orders
# /support/*: support tickets
# /calendar/*: meeting scheduling
# /system/*: reset_state, simulate_transient_failure
#
# Important accounting rule:
# Invoice payment tools already record income.
# - record_partial_payment(...) creates income automatically.
# - update_invoice_status(invoice_id, "paid") may create remaining payment income.
# Do NOT create duplicate manual income transactions for the same invoice payment.
'''


def get_state():
    """Return the current accounting state for validation."""
    return state
