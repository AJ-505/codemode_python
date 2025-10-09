"""
Safe code execution environment for Code Mode agent.
Uses RestrictedPython to safely execute LLM-generated code.
"""

from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence
from typing import Any, Dict, Callable
import json
import operator


def _inplacevar(op_str: str, x, y):
    """
    Handle augmented assignment operators for RestrictedPython.

    RestrictedPython passes the operator as a string ('+=' , '-=', etc.),
    so we need to map it to the actual operator function.

    Args:
        op_str: The operator string (e.g., '+=', '-=', '*=')
        x: The left operand
        y: The right operand

    Returns:
        The result of the operation
    """
    op_map = {
        '+=': operator.iadd,
        '-=': operator.isub,
        '*=': operator.imul,
        '/=': operator.itruediv,
        '//=': operator.ifloordiv,
        '%=': operator.imod,
        '**=': operator.ipow,
        '&=': operator.iand,
        '|=': operator.ior,
        '^=': operator.ixor,
        '>>=': operator.irshift,
        '<<=': operator.ilshift,
    }

    if op_str in op_map:
        return op_map[op_str](x, y)
    else:
        raise ValueError(f"Unsupported inplace operator: {op_str}")


class ToolsAPI:
    """
    Wrapper class that provides tools to the sandboxed code.

    This class dynamically exposes tool functions to the sandboxed environment
    without requiring hardcoded method definitions.
    """

    def __init__(self, tools: Dict[str, Callable]):
        """
        Initialize the tools API wrapper.

        Args:
            tools: Dictionary mapping tool names to callable functions
        """
        self._tools = tools

    def __getattr__(self, name: str):
        """
        Dynamically provide access to any tool in the tools dictionary.

        Args:
            name: Name of the tool to access

        Returns:
            The tool function

        Raises:
            AttributeError: If the tool is not found
        """
        if name in self._tools:
            return self._tools[name]
        raise AttributeError(f"Tool '{name}' not found")


class CodeExecutor:
    """
    Executes Python code in a restricted environment.

    Uses RestrictedPython to provide a safe sandbox for executing
    LLM-generated code with access to approved tools.
    """

    def __init__(self, tools: Dict[str, Callable]):
        """
        Initialize the code executor.

        Args:
            tools: Dictionary of available tools to expose to sandboxed code
        """
        self.tools_api = ToolsAPI(tools)

    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute code in a restricted environment.

        Args:
            code: Python code to execute

        Returns:
            Dictionary with 'success', 'result', and optionally 'error'
        """
        try:
            # Compile the code with restrictions
            compile_result = compile_restricted(
                code,
                filename='<inline code>',
                mode='exec'
            )

            # Check if compilation failed
            if hasattr(compile_result, 'errors') and compile_result.errors:
                return {
                    "success": False,
                    "error": f"Compilation errors: {compile_result.errors}"
                }

            # Extract the actual code object from CompileResult
            # compile_restricted returns a CompileResult object with a 'code' attribute
            if hasattr(compile_result, 'code'):
                byte_code = compile_result.code
            else:
                byte_code = compile_result

            # Verify we have a valid code object
            if not hasattr(byte_code, 'co_code'):
                return {
                    "success": False,
                    "error": "Code compilation failed - no valid code object produced"
                }

            # Create restricted globals with safe builtins + necessary additions
            restricted_builtins = safe_globals.copy()

            # Add essential Python builtins
            restricted_builtins.update({
                '__import__': __import__,
                '_getattr_': getattr,
                '_getitem_': lambda obj, index: obj[index],
                '_getiter_': iter,
                # Type constructors and conversions
                'float': float,
                'int': int,
                'str': str,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'type': type,
                'set': set,
                # Common operations
                'sum': sum,
                'len': len,
                'range': range,
                'enumerate': enumerate,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'zip': zip,
                'all': all,
                'any': any,
                # Support for augmented assignment operators (+=, -=, etc.)
                # RestrictedPython passes operators as strings, so we need a mapper
                '_inplacevar_': _inplacevar,
            })

            # Create a safe print handler for RestrictedPython
            class SafePrinter:
                """Safe print implementation for RestrictedPython."""
                def __init__(self):
                    self.output = []

                def __call__(self, *args):
                    """Called when print() is used."""
                    return self

                def _call_print(self, *args):
                    """RestrictedPython calls this method for print statements."""
                    # Store output instead of printing (can be retrieved if needed)
                    self.output.append(' '.join(str(arg) for arg in args))

            restricted_globals = {
                '__builtins__': restricted_builtins,
                '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
                '_unpack_sequence_': guarded_unpack_sequence,
                'json': json,
                'tools': self.tools_api,
                '_print_': SafePrinter(),  # Proper print handler
                '_getattr_': getattr,
                '__name__': 'restricted_execution',
                '__metaclass__': type,
            }

            # Create a locals dictionary to capture results
            restricted_locals = {}

            # Execute the code
            exec(byte_code, restricted_globals, restricted_locals)

            # Try to get the result
            result = restricted_locals.get('result', None)

            # Filter locals to only include JSON-serializable values
            # Exclude modules, functions, and other non-serializable objects
            serializable_locals = {}
            for k, v in restricted_locals.items():
                if not k.startswith('_'):
                    # Only include basic types that are JSON-serializable
                    if isinstance(v, (str, int, float, bool, list, dict, type(None))):
                        serializable_locals[k] = v

            return {
                "success": True,
                "result": result,
                "locals": serializable_locals
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }


def test_executor():
    """Test the code executor with accounting tools."""
    from tools.business_tools import get_tools, get_state

    # Reset state before testing
    state = get_state()
    state.reset()

    executor = CodeExecutor(get_tools())

    # Test 1: Create transaction
    code1 = '''
import json

# Create an income transaction
result_json = tools.create_transaction(
    transaction_type="income",
    category="consulting",
    amount=5000.0,
    description="Website development project",
    account="checking"
)

result = json.loads(result_json)
'''
    print("Test 1 - Create transaction:")
    print(executor.execute(code1))
    print()

    # Test 2: Create invoice and check state
    code2 = '''
import json

# Create an invoice
invoice_json = tools.create_invoice(
    client_name="Acme Corp",
    items=[
        {"description": "Web Development", "quantity": 40, "price": 150},
        {"description": "Design Work", "quantity": 10, "price": 100}
    ],
    due_days=30
)

invoice_data = json.loads(invoice_json)
invoice_id = invoice_data["invoice"]["id"]

# Send the invoice
tools.update_invoice_status(invoice_id, "sent")

# Get state summary
summary_json = tools.get_state_summary()
summary = json.loads(summary_json)

result = {
    "invoice_id": invoice_id,
    "summary": summary["summary"]
}
'''
    print("Test 2 - Complex workflow:")
    print(executor.execute(code2))
    print()

    # Test 3: Query and summarize
    code3 = '''
import json

# Get financial summary
summary_json = tools.get_financial_summary()
summary = json.loads(summary_json)

result = {
    "total_income": summary["summary"]["total_income"],
    "total_expenses": summary["summary"]["total_expenses"],
    "net_income": summary["summary"]["net_income"]
}
'''
    print("Test 3 - Query and summarize:")
    print(executor.execute(code3))


if __name__ == "__main__":
    test_executor()
