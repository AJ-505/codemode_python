"""
Practical accounting and business management tools with state management.
These tools simulate real business operations that modify state.
"""

import json
import copy
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class InvoiceStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


@dataclass
class Transaction:
    id: str
    date: str
    type: str
    category: str
    amount: float
    description: str
    account: str
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Invoice:
    id: str
    client_name: str
    amount: float
    issue_date: str
    due_date: str
    status: str
    items: List[Dict[str, Any]]
    paid_amount: float = 0.0


@dataclass
class Account:
    name: str
    balance: float
    account_type: str  # checking, savings, credit


class AccountingState:
    """Central state management for accounting operations."""

    def __init__(self):
        self.transactions: List[Transaction] = []
        self.invoices: List[Invoice] = []
        self.accounts: Dict[str, Account] = {
            "checking": Account("checking", 10000.0, "checking"),
            "savings": Account("savings", 50000.0, "savings"),
            "business_credit": Account("business_credit", 0.0, "credit"),
        }
        self.next_transaction_id = 1
        self.next_invoice_id = 1

    def reset(self):
        """Reset state for testing."""
        self.__init__()

    def snapshot(self) -> Dict[str, Any]:
        """Create a deep-copy snapshot for safe rollback across retries."""
        return {
            "transactions": copy.deepcopy(self.transactions),
            "invoices": copy.deepcopy(self.invoices),
            "accounts": copy.deepcopy(self.accounts),
            "next_transaction_id": self.next_transaction_id,
            "next_invoice_id": self.next_invoice_id,
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """Restore a previously captured snapshot."""
        self.transactions = copy.deepcopy(snapshot["transactions"])
        self.invoices = copy.deepcopy(snapshot["invoices"])
        self.accounts = copy.deepcopy(snapshot["accounts"])
        self.next_transaction_id = int(snapshot["next_transaction_id"])
        self.next_invoice_id = int(snapshot["next_invoice_id"])

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        total_income = sum(t.amount for t in self.transactions if t.type == "income")
        total_expenses = sum(t.amount for t in self.transactions if t.type == "expense")

        return {
            "accounts": {name: {"balance": acc.balance, "type": acc.account_type}
                        for name, acc in self.accounts.items()},
            "total_transactions": len(self.transactions),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_income": total_income - total_expenses,
            "total_invoices": len(self.invoices),
            "invoices_by_status": self._count_invoices_by_status(),
            "outstanding_receivables": sum(inv.amount - inv.paid_amount
                                          for inv in self.invoices
                                          if inv.status in ["sent", "overdue"])
        }

    def _count_invoices_by_status(self) -> Dict[str, int]:
        counts = {}
        for inv in self.invoices:
            counts[inv.status] = counts.get(inv.status, 0) + 1
        return counts


# Global state instance
state = AccountingState()


# Tool implementations
def create_transaction(
    transaction_type: str,
    category: str,
    amount: float,
    description: str,
    account: str = "checking",
    date: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Create a new financial transaction.

    Args:
        transaction_type: Type of transaction (income, expense, transfer)
        category: Transaction category (salary, rent, utilities, consulting, etc.)
        amount: Transaction amount (positive number)
        description: Description of the transaction
        account: Account name (checking, savings, business_credit)
        date: Transaction date (ISO format), defaults to today
        tags: Optional list of tags

    Returns:
        JSON string with transaction details
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if account not in state.accounts:
        return json.dumps({"error": f"Unknown account: {account}"})

    # Validate amount is positive
    if amount <= 0:
        return json.dumps({"error": f"Amount must be a positive number, got {amount}"})

    transaction_id = f"TXN{state.next_transaction_id:05d}"
    state.next_transaction_id += 1

    transaction = Transaction(
        id=transaction_id,
        date=date,
        type=transaction_type,
        category=category,
        amount=amount,
        description=description,
        account=account,
        tags=tags or []
    )

    state.transactions.append(transaction)

    # Update account balance
    if transaction_type == "income":
        state.accounts[account].balance += amount
    elif transaction_type == "expense":
        state.accounts[account].balance -= amount

    return json.dumps({
        "status": "success",
        "transaction": asdict(transaction),
        "new_balance": state.accounts[account].balance
    })


def create_invoice(
    client_name: str,
    items: List[Dict[str, Any]],
    due_days: int = 30,
    issue_date: Optional[str] = None
) -> str:
    """
    Create a new invoice.

    Args:
        client_name: Name of the client
        items: List of items, each with 'description', 'quantity', and 'price'
        due_days: Number of days until payment is due
        issue_date: Invoice issue date (ISO format), defaults to today

    Returns:
        JSON string with invoice details
    """
    if issue_date is None:
        issue_date = datetime.now().strftime("%Y-%m-%d")

    issue_dt = datetime.fromisoformat(issue_date)
    due_dt = issue_dt + timedelta(days=due_days)
    due_date = due_dt.strftime("%Y-%m-%d")

    # Calculate total
    total_amount = sum(item['quantity'] * item['price'] for item in items)

    invoice_id = f"INV{state.next_invoice_id:05d}"
    state.next_invoice_id += 1

    invoice = Invoice(
        id=invoice_id,
        client_name=client_name,
        amount=total_amount,
        issue_date=issue_date,
        due_date=due_date,
        status=InvoiceStatus.DRAFT.value,
        items=items,
        paid_amount=0.0
    )

    state.invoices.append(invoice)

    return json.dumps({
        "status": "success",
        "invoice": asdict(invoice)
    })


def update_invoice_status(invoice_id: str, new_status: str) -> str:
    """
    Update the status of an invoice.

    Args:
        invoice_id: Invoice ID
        new_status: New status (draft, sent, paid, overdue, cancelled)

    Returns:
        JSON string with update result
    """
    invoice = next((inv for inv in state.invoices if inv.id == invoice_id), None)

    if not invoice:
        return json.dumps({"error": f"Invoice {invoice_id} not found"})

    old_status = invoice.status
    invoice.status = new_status

    # If marked as paid, record the income
    if new_status == "paid" and old_status != "paid":
        remaining = invoice.amount - invoice.paid_amount
        if remaining > 0:
            invoice.paid_amount = invoice.amount
            create_transaction(
                transaction_type="income",
                category="invoice_payment",
                amount=remaining,
                description=f"Payment for invoice {invoice_id} from {invoice.client_name}",
                account="checking",
                tags=[invoice_id, invoice.client_name]
            )

    return json.dumps({
        "status": "success",
        "invoice_id": invoice_id,
        "old_status": old_status,
        "new_status": new_status,
        "invoice": asdict(invoice)
    })


def record_partial_payment(invoice_id: str, amount: float) -> str:
    """
    Record a partial payment for an invoice.

    Args:
        invoice_id: Invoice ID
        amount: Payment amount

    Returns:
        JSON string with payment result
    """
    invoice = next((inv for inv in state.invoices if inv.id == invoice_id), None)

    if not invoice:
        return json.dumps({"error": f"Invoice {invoice_id} not found"})

    if invoice.paid_amount + amount > invoice.amount:
        return json.dumps({"error": "Payment amount exceeds invoice total"})

    invoice.paid_amount += amount

    # Record the income transaction
    create_transaction(
        transaction_type="income",
        category="invoice_payment",
        amount=amount,
        description=f"Partial payment for invoice {invoice_id} from {invoice.client_name}",
        account="checking",
        tags=[invoice_id, invoice.client_name]
    )

    # Update status if fully paid
    if invoice.paid_amount >= invoice.amount:
        invoice.status = InvoiceStatus.PAID.value

    return json.dumps({
        "status": "success",
        "invoice_id": invoice_id,
        "payment_amount": amount,
        "total_paid": invoice.paid_amount,
        "remaining": invoice.amount - invoice.paid_amount,
        "invoice": asdict(invoice)
    })


def get_transactions(
    account: Optional[str] = None,
    transaction_type: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Query transactions with filters.

    Args:
        account: Filter by account name
        transaction_type: Filter by type (income, expense, transfer)
        category: Filter by category
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        tags: Filter by tags (any match)

    Returns:
        JSON string with matching transactions
    """
    filtered = state.transactions

    if account:
        filtered = [t for t in filtered if t.account == account]

    if transaction_type:
        filtered = [t for t in filtered if t.type == transaction_type]

    if category:
        filtered = [t for t in filtered if t.category == category]

    if start_date:
        filtered = [t for t in filtered if t.date >= start_date]

    if end_date:
        filtered = [t for t in filtered if t.date <= end_date]

    if tags:
        filtered = [t for t in filtered if any(tag in t.tags for tag in tags)]

    return json.dumps({
        "status": "success",
        "count": len(filtered),
        "transactions": [asdict(t) for t in filtered]
    })


def get_invoices(
    status: Optional[str] = None,
    client_name: Optional[str] = None
) -> str:
    """
    Query invoices with filters.

    Args:
        status: Filter by status
        client_name: Filter by client name (case-insensitive partial match)

    Returns:
        JSON string with matching invoices
    """
    filtered = state.invoices

    if status:
        filtered = [inv for inv in filtered if inv.status == status]

    if client_name:
        client_lower = client_name.lower()
        filtered = [inv for inv in filtered if client_lower in inv.client_name.lower()]

    return json.dumps({
        "status": "success",
        "count": len(filtered),
        "invoices": [asdict(inv) for inv in filtered]
    })


def get_financial_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    Get a financial summary for a date range.

    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)

    Returns:
        JSON string with financial summary
    """
    filtered = state.transactions

    if start_date:
        filtered = [t for t in filtered if t.date >= start_date]

    if end_date:
        filtered = [t for t in filtered if t.date <= end_date]

    # Calculate summaries
    income_by_category = {}
    expense_by_category = {}

    for t in filtered:
        if t.type == "income":
            income_by_category[t.category] = income_by_category.get(t.category, 0) + t.amount
        elif t.type == "expense":
            expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount

    total_income = sum(income_by_category.values())
    total_expenses = sum(expense_by_category.values())

    return json.dumps({
        "status": "success",
        "period": {
            "start_date": start_date or "beginning",
            "end_date": end_date or "now"
        },
        "summary": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_income": total_income - total_expenses,
            "income_by_category": income_by_category,
            "expense_by_category": expense_by_category,
            "transaction_count": len(filtered)
        },
        "accounts": {name: acc.balance for name, acc in state.accounts.items()}
    })


def transfer_between_accounts(from_account: str, to_account: str, amount: float, description: str = "") -> str:
    """
    Transfer money between accounts.

    Args:
        from_account: Source account
        to_account: Destination account
        amount: Transfer amount
        description: Transfer description

    Returns:
        JSON string with transfer result
    """
    if from_account not in state.accounts:
        return json.dumps({"error": f"Unknown source account: {from_account}"})

    if to_account not in state.accounts:
        return json.dumps({"error": f"Unknown destination account: {to_account}"})

    if state.accounts[from_account].balance < amount:
        return json.dumps({"error": "Insufficient funds"})

    # Create two transactions for the transfer
    date = datetime.now().strftime("%Y-%m-%d")

    # Debit from source
    state.accounts[from_account].balance -= amount
    txn1_id = f"TXN{state.next_transaction_id:05d}"
    state.next_transaction_id += 1

    txn1 = Transaction(
        id=txn1_id,
        date=date,
        type="transfer",
        category="transfer_out",
        amount=amount,
        description=f"Transfer to {to_account}: {description}",
        account=from_account,
        tags=["transfer", to_account]
    )
    state.transactions.append(txn1)

    # Credit to destination
    state.accounts[to_account].balance += amount
    txn2_id = f"TXN{state.next_transaction_id:05d}"
    state.next_transaction_id += 1

    txn2 = Transaction(
        id=txn2_id,
        date=date,
        type="transfer",
        category="transfer_in",
        amount=amount,
        description=f"Transfer from {from_account}: {description}",
        account=to_account,
        tags=["transfer", from_account]
    )
    state.transactions.append(txn2)

    return json.dumps({
        "status": "success",
        "from_account": from_account,
        "to_account": to_account,
        "amount": amount,
        "new_balances": {
            from_account: state.accounts[from_account].balance,
            to_account: state.accounts[to_account].balance
        },
        "transaction_ids": [txn1_id, txn2_id]
    })


def get_account_balance(account: str) -> str:
    """
    Get the current balance of an account.

    Args:
        account: Account name

    Returns:
        JSON string with account balance
    """
    if account not in state.accounts:
        return json.dumps({"error": f"Unknown account: {account}"})

    acc = state.accounts[account]
    return json.dumps({
        "status": "success",
        "account": account,
        "balance": acc.balance,
        "type": acc.account_type
    })


def get_state_summary() -> str:
    """
    Get a complete summary of the current accounting state.

    Returns:
        JSON string with complete state summary
    """
    return json.dumps({
        "status": "success",
        "summary": state.get_summary()
    })


def reset_state() -> str:
    """
    Reset all accounting state (for testing).

    Returns:
        JSON string confirming reset
    """
    state.reset()
    return json.dumps({
        "status": "success",
        "message": "State has been reset"
    })
