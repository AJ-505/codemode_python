"""
Debug script to isolate the f-string formatting issue in RestrictedPython.
"""
from sandbox.executor import CodeExecutor
from tools.business_tools import get_tools

executor = CodeExecutor(get_tools())

# Test 1: Simple f-string without format specifier
code1 = '''
import json
total = 100
result = f"Total: ${total}"
'''
print("Test 1 - Simple f-string:")
print(executor.execute(code1))
print()

# Test 2: F-string with .2f format specifier
code2 = '''
import json
total = 100.5
result = f"Total: ${total:.2f}"
'''
print("Test 2 - F-string with .2f:")
print(executor.execute(code2))
print()

# Test 3: Using string format method instead
code3 = '''
import json
total = 100.5
result = "Total: ${:.2f}".format(total)
'''
print("Test 3 - String format method:")
print(executor.execute(code3))
print()

# Test 4: Using round()
code4 = '''
import json
total = 100.567
rounded = round(total, 2)
result = f"Total: ${rounded}"
'''
print("Test 4 - Using round():")
print(executor.execute(code4))
