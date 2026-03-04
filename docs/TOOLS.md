# Available Business Tools

This document describes all the stateful business tools available in the benchmark.
Current tool count: **22**.

## Accounting State

The tools maintain a shared state that includes:
- **Accounts**: checking, savings, business_credit (with balances)
- **Transactions**: All income, expense, and transfer records
- **Invoices**: Client invoices with status tracking

Initial state:
- Checking account: $10,000
- Savings account: $50,000
- Business credit: $0

## Tools

### 1. create_transaction

Create a new financial transaction (income, expense, or transfer).

**Parameters:**
- `transaction_type` (str): "income", "expense", or "transfer"
- `category` (str): Category like "salary", "rent", "utilities", "consulting", etc.
- `amount` (float): Transaction amount (positive number)
- `description` (str): Description of the transaction
- `account` (str, optional): "checking", "savings", or "business_credit" (default: "checking")
- `date` (str, optional): ISO format date (default: today)
- `tags` (list, optional): List of tags

**Returns:** Transaction details and new account balance

**Example:**
```python
result = tools.create_transaction(
    transaction_type="income",
    category="consulting",
    amount=5000.0,
    description="Website development project"
)
```

### 2. create_invoice

Create a new invoice for a client.

**Parameters:**
- `client_name` (str): Name of the client
- `items` (list): List of dicts with 'description', 'quantity', and 'price'
- `due_days` (int, optional): Days until payment due (default: 30)
- `issue_date` (str, optional): ISO format date (default: today)

**Returns:** Invoice details including calculated total

**Example:**
```python
result = tools.create_invoice(
    client_name="Acme Corp",
    items=[
        {"description": "Consulting", "quantity": 50, "price": 200},
        {"description": "Design", "quantity": 20, "price": 150}
    ]
)
```

### 3. update_invoice_status

Update the status of an invoice.

**Parameters:**
- `invoice_id` (str): Invoice ID (e.g., "INV00001")
- `new_status` (str): "draft", "sent", "paid", "overdue", or "cancelled"

**Returns:** Update result

**Note:** Marking as "paid" automatically creates an income transaction.

### 4. record_partial_payment

Record a partial payment for an invoice.

**Parameters:**
- `invoice_id` (str): Invoice ID
- `amount` (float): Payment amount

**Returns:** Payment result and remaining balance

**Note:** Automatically creates an income transaction and updates status to "paid" if fully paid.

### 5. get_transactions

Query transactions with optional filters.

**Parameters:**
- `account` (str, optional): Filter by account
- `transaction_type` (str, optional): Filter by type
- `category` (str, optional): Filter by category
- `start_date` (str, optional): ISO format start date
- `end_date` (str, optional): ISO format end date
- `tags` (list, optional): Filter by tags

**Returns:** List of matching transactions

### 6. get_invoices

Query invoices with optional filters.

**Parameters:**
- `status` (str, optional): Filter by status
- `client_name` (str, optional): Filter by client name (partial match)

**Returns:** List of matching invoices

### 7. get_financial_summary

Get a financial summary with income/expense breakdown.

**Parameters:**
- `start_date` (str, optional): ISO format start date
- `end_date` (str, optional): ISO format end date

**Returns:** Complete financial summary including:
- Total income and breakdown by category
- Total expenses and breakdown by category
- Net income
- Account balances

### 8. transfer_between_accounts

Transfer money between accounts.

**Parameters:**
- `from_account` (str): Source account
- `to_account` (str): Destination account
- `amount` (float): Transfer amount
- `description` (str, optional): Transfer description

**Returns:** Transfer result and new balances

**Note:** Creates two transactions (one debit, one credit).

### 9. get_account_balance

Get the current balance of an account.

**Parameters:**
- `account` (str): Account name

**Returns:** Account balance and type

### 10. get_state_summary

Get a complete summary of the current accounting state.

**Parameters:** None

**Returns:** Complete state including:
- All account balances
- Total transaction count
- Total income and expenses
- Net income
- Invoice counts by status
- Outstanding receivables

### 11. reset_state

Reset all accounting state to initial values (for testing).

**Parameters:** None

**Returns:** Confirmation message

## Usage Examples

### Example 1: Record Monthly Expenses
```python
import json

# Record rent
rent = tools.create_transaction(
    transaction_type="expense",
    category="rent",
    amount=2500,
    description="Office rent - January"
)

# Record utilities
utilities = tools.create_transaction(
    transaction_type="expense",
    category="utilities",
    amount=200,
    description="Electric and water"
)

# Get summary
summary_json = tools.get_financial_summary()
summary = json.loads(summary_json)

result = {
    "total_expenses": summary["summary"]["total_expenses"],
    "checking_balance": summary["summary"]["accounts"]["checking"]
}
```

### Example 2: Invoice Workflow
```python
import json

# Create invoice
invoice_json = tools.create_invoice(
    client_name="TechStart Inc",
    items=[
        {"description": "Development", "quantity": 80, "price": 150}
    ]
)
invoice = json.loads(invoice_json)
invoice_id = invoice["invoice"]["id"]

# Send invoice
tools.update_invoice_status(invoice_id, "sent")

# Record payment
payment = tools.record_partial_payment(invoice_id, 12000)

# Check state
state = tools.get_state_summary()
result = json.loads(state)
```

### Example 3: Multi-Account Management
```python
import json

# Transfer to savings
transfer = tools.transfer_between_accounts(
    from_account="checking",
    to_account="savings",
    amount=5000,
    description="Monthly savings"
)

# Check balances
checking = tools.get_account_balance("checking")
savings = tools.get_account_balance("savings")

result = {
    "checking": json.loads(checking)["balance"],
    "savings": json.loads(savings)["balance"]
}
```

## State Validation

Each test scenario validates the final state by checking:
- Transaction counts and types
- Invoice counts and statuses
- Account balances
- Total income/expenses
- Outstanding receivables

This ensures both agents not only produce reasonable-looking output but actually perform the correct operations.
