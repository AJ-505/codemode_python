"""
Test inplace operators specifically.
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
    elif result['result']:
        print(f"  Result: {result['result']}")
    return result

# Test 1: Simple += outside loop
test1 = '''
total = 0
total += 5
result = f"Total: {total}"
'''
test_code("Test 1: Simple += outside loop", test1)

# Test 2: += in a for loop with range
test2 = '''
total = 0
for i in range(3):
    total += 1
result = f"Total: {total}"
'''
test_code("Test 2: += in for loop with range", test2)

# Test 3: += in a for loop with list
test3 = '''
total = 0
numbers = [1, 2, 3]
for n in numbers:
    total += n
result = f"Total: {total}"
'''
test_code("Test 3: += in for loop with list", test3)

# Test 4: += in a for loop with dict list
test4 = '''
total = 0
items = [{"value": 10}, {"value": 20}]
for item in items:
    total += item["value"]
result = f"Total: {total}"
'''
test_code("Test 4: += in for loop with dict list", test4)

# Test 5: Using explicit assignment instead of +=
test5 = '''
total = 0
items = [{"value": 10}, {"value": 20}]
for item in items:
    total = total + item["value"]
result = f"Total: {total}"
'''
test_code("Test 5: Using = instead of += in for loop", test5)
