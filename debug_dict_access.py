"""
Test dictionary access patterns.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools, get_state

# Reset state
state = get_state()
state.reset()

executor = CodeExecutor(get_tools())

# Test 1: Simple dict access
code1 = '''import json

data = {"invoice": {"id": "INV00001"}}
invoice_id = data["invoice"]["id"]
result = f"ID: {invoice_id}"
'''

print("Test 1 - Simple nested dict access:")
result1 = executor.execute(code1)
print(f"Success: {result1['success']}")
if result1["success"]:
    print(f"Result: {result1['result']}")
else:
    print(f"Error: {result1['error']}")
print()

# Test 2: JSON parsing then dict access
code2 = '''import json

json_str = '{"invoice": {"id": "INV00001"}}'
data = json.loads(json_str)
invoice_id = data["invoice"]["id"]
result = f"ID: {invoice_id}"
'''

print("Test 2 - JSON parsing then nested dict access:")
result2 = executor.execute(code2)
print(f"Success: {result2['success']}")
if result2["success"]:
    print(f"Result: {result2['result']}")
else:
    print(f"Error: {result2['error']}")
print()

# Test 3: From tool then dict access
code3 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
json_str = tools.create_invoice("TechStart Inc", techstart_items, 30)
result = f"Type: {json_str.__class__.__name__}, Length: {len(json_str)}"
'''

print("Test 3 - Check what tool returns:")
result3 = executor.execute(code3)
print(f"Success: {result3['success']}")
if result3["success"]:
    print(f"Result: {result3['result']}")
else:
    print(f"Error: {result3['error']}")
print()

# Test 4: From tool, parse, then access
code4 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
json_str = tools.create_invoice("TechStart Inc", techstart_items, 30)
data = json.loads(json_str)
result = f"Keys: {list(data.keys())}"
'''

print("Test 4 - From tool, parse, show keys:")
result4 = executor.execute(code4)
print(f"Success: {result4['success']}")
if result4["success"]:
    print(f"Result: {result4['result']}")
else:
    print(f"Error: {result4['error']}")
print()

# Test 5: From tool, parse, access invoice
code5 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
json_str = tools.create_invoice("TechStart Inc", techstart_items, 30)
data = json.loads(json_str)
invoice = data["invoice"]
result = f"Invoice keys: {list(invoice.keys())}"
'''

print("Test 5 - From tool, parse, access invoice:")
result5 = executor.execute(code5)
print(f"Success: {result5['success']}")
if result5["success"]:
    print(f"Result: {result5['result']}")
else:
    print(f"Error: {result5['error']}")
print()

# Test 6: From tool, parse, access invoice ID
code6 = '''import json

techstart_items = [
    {"description": "Software Development", "quantity": 80, "price": 150}
]
json_str = tools.create_invoice("TechStart Inc", techstart_items, 30)
data = json.loads(json_str)
invoice = data["invoice"]
invoice_id = invoice["id"]
result = f"Invoice ID: {invoice_id}"
'''

print("Test 6 - From tool, parse, access invoice ID:")
result6 = executor.execute(code6)
print(f"Success: {result6['success']}")
if result6["success"]:
    print(f"Result: {result6['result']}")
else:
    print(f"Error: {result6['error']}")
