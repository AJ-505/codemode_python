"""
Execute code line by line to find exact failure.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools, get_state

# Reset state
state = get_state()
state.reset()

executor = CodeExecutor(get_tools())

# Build up the code line by line
lines = [
    'import json',
    '',
    '# Create invoice for TechStart Inc',
    'techstart_items = [',
    '    {"description": "Software Development", "quantity": 80, "price": 150},',
    '    {"description": "Code Review", "quantity": 10, "price": 100}',
    ']',
    'techstart_invoice_json = tools.create_invoice("TechStart Inc", techstart_items, 30)',
]

for i in range(1, len(lines) + 1):
    code = '\n'.join(lines[:i]) + '\n\nresult = "ok"'
    result = executor.execute(code)
    print(f"Lines 1-{i}: {'✓' if result['success'] else '✗ FAILED'}")
    if not result['success']:
        print(f"  Error: {result['error']}")
        print(f"  Last line: {lines[i-1]}")
        break
    state.reset()

print()

# Continue from successful point
continuing_lines = [
    'techstart_invoice_id = json.loads(techstart_invoice_json)["invoice"]["id"]',
]

base_code = '\n'.join(lines)
for i, line in enumerate(continuing_lines, start=len(lines)+1):
    code = base_code + '\n' + line + '\n\nresult = "ok"'
    result = executor.execute(code)
    print(f"Line {i}: {'✓' if result['success'] else '✗ FAILED'}")
    if not result['success']:
        print(f"  Error: {result['error']}")
        print(f"  Line: {line}")
        break
    base_code = code.replace('\n\nresult = "ok"', '')
    state.reset()
