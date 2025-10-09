"""
Test the full flow step by step.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools, get_state

# Reset state
state = get_state()
state.reset()

executor = CodeExecutor(get_tools())

# Test 1: Do everything up to total_outstanding
code1 = '''import json

# Create invoice for TechStart Inc
techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

# Create invoice for Design Studio
design_studio_items = [
    {"description": "UI/UX Design", "quantity": 40, "price": 125},
    {"description": "Prototyping", "quantity": 15, "price": 100}
]
design_studio_invoice_json = tools.create_invoice("Design Studio", design_studio_items, 15)
design_studio_invoice_id = json.loads(design_studio_invoice_json)["invoice"]["id"]

# Mark TechStart Inc invoice as 'sent'
tools.update_invoice_status(techstart_invoice_id, "sent")

# Get summary of all invoices
invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total_outstanding = 0
for invoice in invoices:
    if invoice["status"] != "paid":
        total_outstanding += invoice["amount"] - invoice["paid_amount"]

result = f"Total: {total_outstanding}"
'''

print("Test 1 - Full flow with simple f-string:")
result1 = executor.execute(code1)
print(f"Success: {result1['success']}")
if result1["success"]:
    print(f"Result: {result1['result']}")
else:
    print(f"Error: {result1['error']}")
print()

# Reset state
state.reset()

# Test 2: With format specifier
code2 = '''import json

# Create invoice for TechStart Inc
techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

# Create invoice for Design Studio
design_studio_items = [
    {"description": "UI/UX Design", "quantity": 40, "price": 125},
    {"description": "Prototyping", "quantity": 15, "price": 100}
]
design_studio_invoice_json = tools.create_invoice("Design Studio", design_studio_items, 15)
design_studio_invoice_id = json.loads(design_studio_invoice_json)["invoice"]["id"]

# Mark TechStart Inc invoice as 'sent'
tools.update_invoice_status(techstart_invoice_id, "sent")

# Get summary of all invoices
invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total_outstanding = 0
for invoice in invoices:
    if invoice["status"] != "paid":
        total_outstanding += invoice["amount"] - invoice["paid_amount"]

result = f"Total: ${total_outstanding:.2f}"
'''

print("Test 2 - Full flow with .2f format specifier:")
result2 = executor.execute(code2)
print(f"Success: {result2['success']}")
if result2["success"]:
    print(f"Result: {result2['result']}")
else:
    print(f"Error: {result2['error']}")
print()

# Reset state
state.reset()

# Test 3: Check type of invoice variables
code3 = '''import json

# Create invoice for TechStart Inc
techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_data = json.loads(techstart_invoice_json)
techstart_invoice = techstart_data["invoice"]
techstart_invoice_id = techstart_invoice["id"]

result = f"ID: {techstart_invoice_id}, Type: {type(techstart_invoice_id)}"
'''

print("Test 3 - Check type of invoice_id:")
result3 = executor.execute(code3)
print(f"Success: {result3['success']}")
if result3["success"]:
    print(f"Result: {result3['result']}")
else:
    print(f"Error: {result3['error']}")
