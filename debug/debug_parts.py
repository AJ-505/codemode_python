"""
Test parts of Scenario 2 separately.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools, get_state

def test_part(name, code):
    state = get_state()
    state.reset()
    executor = CodeExecutor(get_tools())
    result = executor.execute(code)
    print(f"{name}: {'✓ SUCCESS' if result['success'] else '✗ FAILED'}")
    if not result['success']:
        print(f"  Error: {result['error']}")
    elif result['result']:
        print(f"  Result: {result['result'][:100]}...")
    print()
    return result['success']

# Part 1: Create both invoices
part1 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

design_studio_items = [
    {"description": "UI/UX Design", "quantity": 40, "price": 125},
    {"description": "Prototyping", "quantity": 15, "price": 100}
]
design_studio_invoice_json = tools.create_invoice("Design Studio", design_studio_items, 15)
design_studio_invoice_id = json.loads(design_studio_invoice_json)["invoice"]["id"]

result = f"IDs: {techstart_invoice_id}, {design_studio_invoice_id}"
'''
test_part("Part 1: Create invoices", part1)

# Part 2: Add status update
part2 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

design_studio_items = [
    {"description": "UI/UX Design", "quantity": 40, "price": 125},
    {"description": "Prototyping", "quantity": 15, "price": 100}
]
design_studio_invoice_json = tools.create_invoice("Design Studio", design_studio_items, 15)
design_studio_invoice_id = json.loads(design_studio_invoice_json)["invoice"]["id"]

# Mark TechStart Inc invoice as 'sent'
tools.update_invoice_status(techstart_invoice_id, "sent")

result = "Updated invoice status"
'''
test_part("Part 2: Add status update", part2)

# Part 3: Add get invoices
part3 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

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

result = f"Got {len(invoices)} invoices"
'''
test_part("Part 3: Add get invoices", part3)

# Part 4: Add total calculation
part4 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

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
test_part("Part 4: Add total calculation", part4)

# Part 5: Full code with simple f-string result
part5 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

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

result = f"Created 2 invoices - IDs: {techstart_invoice_id}, {design_studio_invoice_id} - Total: {total_outstanding}"
'''
test_part("Part 5: Full code with single-line f-string", part5)

# Part 6: Multi-line f-string
part6 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150},
    {"description": "Code Review", "quantity": 10, "price": 100}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)
techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]

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
test_part("Part 6: Multi-line f-string with backslashes", part6)
