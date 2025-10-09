"""
Debug script to test the exact failing code from Scenario 2.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools, get_state

# Reset state
state = get_state()
state.reset()

executor = CodeExecutor(get_tools())

# This is the exact code that fails in the benchmark
code = '''import json

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

result = f"Created 2 invoices:\\n" \\
         f"- TechStart Inc: {techstart_invoice_id}\\n" \\
         f"- Design Studio: {design_studio_invoice_id}\\n" \\
         f"Total outstanding receivables: ${total_outstanding:.2f}"
'''

print("Executing Scenario 2 code:")
result = executor.execute(code)
print(result)
print()

if result["success"]:
    print("SUCCESS! Result:")
    print(result["result"])
else:
    print("FAILED! Error:")
    print(result["error"])
