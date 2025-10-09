"""
Narrow down the exact line causing the error.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools, get_state

# Reset state
state = get_state()
state.reset()

executor = CodeExecutor(get_tools())

# Test 1: Just create one invoice
code1 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
result = "Invoice created"
'''
print("Test 1 - Create invoice:")
print(executor.execute(code1))
print()

# Reset state
state.reset()

# Test 2: Create invoice and access ID
code2 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]
result = f"Invoice ID: {techstart_invoice_id}"
'''
print("Test 2 - Create invoice and access ID:")
print(executor.execute(code2))
print()

# Reset state
state.reset()

# Test 3: Use the continuation with backslashes
code3 = '''import json

techstart_invoice_id = "INV00001"
design_studio_invoice_id = "INV00002"
total_outstanding = 19500

result = f"Created 2 invoices:\\n" \\
         f"- TechStart Inc: {techstart_invoice_id}\\n" \\
         f"- Design Studio: {design_studio_invoice_id}\\n" \\
         f"Total outstanding receivables: ${total_outstanding:.2f}"
'''
print("Test 3 - Multi-line f-string with backslashes:")
print(executor.execute(code3))
print()

# Test 4: Same thing without backslashes
code4 = '''import json

techstart_invoice_id = "INV00001"
design_studio_invoice_id = "INV00002"
total_outstanding = 19500

result = f"Created 2 invoices:\\n- TechStart Inc: {techstart_invoice_id}\\n- Design Studio: {design_studio_invoice_id}\\n Total outstanding receivables: ${total_outstanding:.2f}"
'''
print("Test 4 - Single-line f-string:")
print(executor.execute(code4))
