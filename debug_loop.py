"""
Test the loop specifically.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools, get_state

def test_code(name, code):
    state = get_state()
    state.reset()
    executor = CodeExecutor(get_tools())
    result = executor.execute(code)
    print(f"\n{name}:")
    print(f"  {'✓ SUCCESS' if result['success'] else '✗ FAILED'}")
    if not result['success']:
        print(f"  Error: {result['error']}")
        # Try to get more details
        import traceback
        print(f"  (Full error details above)")
    elif result['result']:
        print(f"  Result: {result['result']}")
    return result

# Test 1: Simple loop with dict access
test1 = '''import json

invoices = [
    {"status": "sent", "amount": 1000, "paid_amount": 0},
    {"status": "draft", "amount": 500, "paid_amount": 0}
]

total = 0
for invoice in invoices:
    if invoice["status"] != "paid":
        total += invoice["amount"] - invoice["paid_amount"]

result = f"Total: {total}"
'''
test_code("Test 1: Simple loop with hardcoded data", test1)

# Test 2: Loop with tools-generated data
test2 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)

invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

result = f"Got {len(invoices)} invoices"
'''
test_code("Test 2: Get invoices from tools", test2)

# Test 3: Loop over tool-generated invoices
test3 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)

invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total = 0
for invoice in invoices:
    total += 1

result = f"Counted {total} invoices"
'''
test_code("Test 3: Simple loop over tool-generated invoices", test3)

# Test 4: Access invoice fields in loop
test4 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)

invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total = 0
for invoice in invoices:
    amount = invoice["amount"]
    total += amount

result = f"Total: {total}"
'''
test_code("Test 4: Access invoice amount in loop", test4)

# Test 5: Access invoice status
test5 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)

invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total = 0
for invoice in invoices:
    status = invoice["status"]
    result = f"Status: {status}"
'''
test_code("Test 5: Access invoice status", test5)

# Test 6: Check status in if statement
test6 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)

invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total = 0
for invoice in invoices:
    if invoice["status"] != "paid":
        total += 1

result = f"Unpaid: {total}"
'''
test_code("Test 6: Check status in if statement", test6)

# Test 7: Full calculation
test7 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)

invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total_outstanding = 0
for invoice in invoices:
    if invoice["status"] != "paid":
        total_outstanding += invoice["amount"] - invoice["paid_amount"]

result = f"Total: {total_outstanding}"
'''
test_code("Test 7: Full calculation with one invoice", test7)

# Test 8: Full calculation with TWO invoices
test8 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)

design_studio_items = [
    {"description": "UI/UX Design", "quantity": 40, "price": 125}
]
design_studio_invoice_json = tools.create_invoice("Design Studio", design_studio_items, 15)

invoices_json = tools.get_invoices()
invoices = json.loads(invoices_json)["invoices"]

total_outstanding = 0
for invoice in invoices:
    if invoice["status"] != "paid":
        total_outstanding += invoice["amount"] - invoice["paid_amount"]

result = f"Total: {total_outstanding}"
'''
test_code("Test 8: Full calculation with TWO invoices", test8)
