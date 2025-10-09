"""Test RestrictedPython augmented assignment."""
from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence
import operator

# Compile code with +=
code = compile_restricted('''
x = 10
x += 5
result = x
''', '<test>', 'exec')

if hasattr(code, 'errors') and code.errors:
    print("Compilation errors:", code.errors)
else:
    # Get the code object
    byte_code = code.code if hasattr(code, 'code') else code

    # Try different _inplacevar_ implementations

    # Option 1: Just apply the operator
    def inplacevar_v1(op, x, y):
        return op(x, y)

    # Option 2: The proper way for augmented assignment
    def inplacevar_v2(op, x, y):
        # For +=, op should be operator.iadd
        result = op(x, y)
        return result

    # Test without _inplacevar_
    print("\n=== Test 1: No _inplacevar_ defined ===")
    try:
        restricted_globals = {
            '__builtins__': safe_globals,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            '_unpack_sequence_': guarded_unpack_sequence,
        }
        restricted_locals = {}
        exec(byte_code, restricted_globals, restricted_locals)
        print(f"Result: {restricted_locals.get('result', 'NO RESULT')}")
    except Exception as e:
        print(f"Error: {e}")

    # Test with _inplacevar_ v1
    print("\n=== Test 2: With _inplacevar_ v1 ===")
    try:
        restricted_globals = {
            '__builtins__': safe_globals,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            '_unpack_sequence_': guarded_unpack_sequence,
            '_inplacevar_': inplacevar_v1,
        }
        restricted_locals = {}
        exec(byte_code, restricted_globals, restricted_locals)
        print(f"Result: {restricted_locals.get('result', 'NO RESULT')}")
    except Exception as e:
        print(f"Error: {e}")

    # Test with proper builtins that include int
    print("\n=== Test 3: With proper builtins ===")
    try:
        builtins = safe_globals.copy()
        builtins['int'] = int
        builtins['_inplacevar_'] = lambda op, x, y: op(x, y)

        restricted_globals = {
            '__builtins__': builtins,
            '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            '_unpack_sequence_': guarded_unpack_sequence,
        }
        restricted_locals = {}
        exec(byte_code, restricted_globals, restricted_locals)
        print(f"Result: {restricted_locals.get('result', 'NO RESULT')}")
    except Exception as e:
        print(f"Error: {e}")
