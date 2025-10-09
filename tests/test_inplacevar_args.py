"""Test what arguments _inplacevar_ receives."""
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence
import operator

# Compile code with +=
code = compile_restricted('''
x = 10
x += 5
result = x
''', '<test>', 'exec')

byte_code = code.code if hasattr(code, 'code') else code

# Custom _inplacevar_ that prints what it receives
def debug_inplacevar(op, x, y):
    print(f"  _inplacevar_ called with:")
    print(f"    op type: {type(op)}, value: {repr(op)}")
    print(f"    x type: {type(x)}, value: {repr(x)}")
    print(f"    y type: {type(y)}, value: {repr(y)}")
    # Try to figure out what to do
    if isinstance(op, str):
        print(f"    op is a string! This is the problem!")
        # Maybe it's the operator name?
        op_map = {
            '+=': operator.iadd,
            '-=': operator.isub,
            '*=': operator.imul,
            '/=': operator.itruediv,
        }
        if op in op_map:
            actual_op = op_map[op]
            result = actual_op(x, y)
            print(f"    Mapped to {actual_op}, result: {result}")
            return result
    return op(x, y)

builtins = safe_globals.copy()
builtins['int'] = int
builtins['_inplacevar_'] = debug_inplacevar

restricted_globals = {
    '__builtins__': builtins,
    '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
    '_unpack_sequence_': guarded_unpack_sequence,
}
restricted_locals = {}

print("Executing code...")
try:
    exec(byte_code, restricted_globals, restricted_locals)
    print(f"Result: {restricted_locals.get('result', 'NO RESULT')}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
