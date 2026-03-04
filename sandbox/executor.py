"""
Safe code execution environment for Code Mode agents.

The sandbox uses RestrictedPython and adds:
- Import allow-list (blocks raw network/system modules)
- Timeout guard to stop runaway loops
- Optional memory cap (best effort on Unix)
- Tool-call interception/logging for auditability
"""

from __future__ import annotations

import json
import operator
import signal
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Callable, List, Optional

from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    guarded_unpack_sequence,
)

try:
    from RestrictedPython.Guards import safer_getattr  # type: ignore
except Exception:  # pragma: no cover - fallback for older RestrictedPython versions
    safer_getattr = getattr

try:
    from RestrictedPython.Guards import full_write_guard  # type: ignore
except Exception:  # pragma: no cover - fallback for older RestrictedPython versions
    full_write_guard = None

try:
    import resource  # Unix only
except Exception:  # pragma: no cover - unavailable on Windows
    resource = None  # type: ignore


ALLOWED_IMPORTS = {"json", "math", "statistics", "datetime", "decimal", "itertools", "collections"}


def _safe_import(name: str, globals_=None, locals_=None, fromlist=(), level=0):
    """Allow importing only a strict, explicit module allow-list."""
    root_module = name.split(".")[0]
    if root_module not in ALLOWED_IMPORTS:
        raise ImportError(f"Import '{name}' is blocked by sandbox policy")
    return __import__(name, globals_, locals_, fromlist, level)


@dataclass
class SandboxLimits:
    """Execution limits for generated code."""

    timeout_seconds: int = 5
    max_memory_mb: int = 512


def _inplacevar(op_str: str, x, y):
    """
    Handle augmented assignment operators for RestrictedPython.
    """
    op_map = {
        "+=": operator.iadd,
        "-=": operator.isub,
        "*=": operator.imul,
        "/=": operator.itruediv,
        "//=": operator.ifloordiv,
        "%=": operator.imod,
        "**=": operator.ipow,
        "&=": operator.iand,
        "|=": operator.ior,
        "^=": operator.ixor,
        ">>=": operator.irshift,
        "<<=": operator.ilshift,
    }

    if op_str in op_map:
        return op_map[op_str](x, y)
    raise ValueError(f"Unsupported inplace operator: {op_str}")


def _safe_repr(value: Any, max_chars: int = 240) -> str:
    """Create a short safe representation for logs."""
    text = repr(value)
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars-3]}..."


def _to_jsonable(value: Any, max_collection: int = 30, max_str: int = 400) -> Any:
    """Best-effort JSON-safe conversion for trace payloads."""
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        if len(value) <= max_str:
            return value
        return value[: max_str - 3] + "..."
    if isinstance(value, list):
        return [_to_jsonable(item, max_collection, max_str) for item in value[:max_collection]]
    if isinstance(value, tuple):
        return [_to_jsonable(item, max_collection, max_str) for item in value[:max_collection]]
    if isinstance(value, dict):
        converted: Dict[str, Any] = {}
        for idx, (key, item) in enumerate(value.items()):
            if idx >= max_collection:
                break
            converted[str(key)] = _to_jsonable(item, max_collection, max_str)
        return converted
    return _safe_repr(value)


def _extract_state_metrics(state_summary: Optional[Dict[str, Any]]) -> Dict[str, float]:
    if not isinstance(state_summary, dict):
        return {}
    accounts = state_summary.get("accounts") or {}
    checking = ((accounts.get("checking") or {}).get("balance")) if isinstance(accounts, dict) else None
    savings = ((accounts.get("savings") or {}).get("balance")) if isinstance(accounts, dict) else None
    credit = ((accounts.get("business_credit") or {}).get("balance")) if isinstance(accounts, dict) else None
    metrics: Dict[str, float] = {}
    for key, value in [
        ("checking_balance", checking),
        ("savings_balance", savings),
        ("business_credit_balance", credit),
        ("total_transactions", state_summary.get("total_transactions")),
        ("total_income", state_summary.get("total_income")),
        ("total_expenses", state_summary.get("total_expenses")),
        ("total_invoices", state_summary.get("total_invoices")),
        ("outstanding_receivables", state_summary.get("outstanding_receivables")),
    ]:
        if isinstance(value, (int, float)):
            metrics[key] = float(value)
    return metrics


def _state_delta(before: Optional[Dict[str, Any]], after: Optional[Dict[str, Any]]) -> Dict[str, float]:
    before_metrics = _extract_state_metrics(before)
    after_metrics = _extract_state_metrics(after)
    delta: Dict[str, float] = {}
    for key in sorted(set(before_metrics.keys()) | set(after_metrics.keys())):
        delta[key] = round(after_metrics.get(key, 0.0) - before_metrics.get(key, 0.0), 6)
    return delta


@contextmanager
def _execution_timeout(seconds: int):
    """Apply wall-clock timeout using SIGALRM (Unix)."""
    if seconds <= 0 or not hasattr(signal, "SIGALRM"):
        yield
        return

    def _timeout_handler(signum, frame):
        raise TimeoutError(f"Execution exceeded {seconds} seconds")

    previous_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)


@contextmanager
def _memory_limit(max_memory_mb: int):
    """Best-effort address-space limit on Unix."""
    if not resource or max_memory_mb <= 0:
        yield
        return

    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    except Exception:
        yield
        return

    target = max_memory_mb * 1024 * 1024
    if hard not in (-1, resource.RLIM_INFINITY):  # pragma: no cover - platform dependent
        target = min(target, hard)

    # Keep hard limit unchanged; only lower soft limit for sandbox run.
    original = (soft, hard)
    new_soft = target if soft in (-1, resource.RLIM_INFINITY) or soft > target else soft

    try:
        resource.setrlimit(resource.RLIMIT_AS, (new_soft, hard))
    except Exception:
        yield
        return

    try:
        yield
    finally:
        try:
            resource.setrlimit(resource.RLIMIT_AS, original)
        except Exception:
            pass


class ToolsAPI:
    """
    Wrapper that exposes tools and intercepts each call for auditing.
    """

    def __init__(self, tools: Dict[str, Callable], state_summary_getter: Optional[Callable[[], Dict[str, Any]]] = None):
        self._tools = tools
        self._call_log: List[Dict[str, Any]] = []
        self._wrapped_tools: Dict[str, Callable] = {}
        self._state_summary_getter = state_summary_getter

    def reset_call_log(self):
        self._call_log = []

    def get_call_log(self) -> List[Dict[str, Any]]:
        return list(self._call_log)

    def _wrap_tool(self, name: str, fn: Callable) -> Callable:
        if name in self._wrapped_tools:
            return self._wrapped_tools[name]

        def _wrapped(*args, **kwargs):
            start = time.perf_counter()
            state_before = None
            if self._state_summary_getter:
                try:
                    state_before = self._state_summary_getter()
                except Exception:
                    state_before = None
            try:
                result = fn(*args, **kwargs)
                state_after = None
                if self._state_summary_getter:
                    try:
                        state_after = self._state_summary_getter()
                    except Exception:
                        state_after = None
                self._call_log.append(
                    {
                        "tool": name,
                        "args_structured": _to_jsonable(list(args)),
                        "kwargs_structured": _to_jsonable(kwargs),
                        "args": _safe_repr(args),
                        "kwargs": _safe_repr(kwargs),
                        "duration_ms": round((time.perf_counter() - start) * 1000, 3),
                        "state_before": _to_jsonable(state_before),
                        "state_after": _to_jsonable(state_after),
                        "state_delta": _to_jsonable(_state_delta(state_before, state_after)),
                        "result_preview": _safe_repr(result),
                        "result_structured": _to_jsonable(result),
                        "success": True,
                    }
                )
                return result
            except Exception as exc:
                state_after = None
                if self._state_summary_getter:
                    try:
                        state_after = self._state_summary_getter()
                    except Exception:
                        state_after = None
                self._call_log.append(
                    {
                        "tool": name,
                        "args_structured": _to_jsonable(list(args)),
                        "kwargs_structured": _to_jsonable(kwargs),
                        "args": _safe_repr(args),
                        "kwargs": _safe_repr(kwargs),
                        "duration_ms": round((time.perf_counter() - start) * 1000, 3),
                        "state_before": _to_jsonable(state_before),
                        "state_after": _to_jsonable(state_after),
                        "state_delta": _to_jsonable(_state_delta(state_before, state_after)),
                        "error": str(exc),
                        "success": False,
                    }
                )
                raise

        self._wrapped_tools[name] = _wrapped
        return _wrapped

    def __getattr__(self, name: str):
        if name in self._tools:
            return self._wrap_tool(name, self._tools[name])
        raise AttributeError(f"Tool '{name}' not found")


class CodeExecutor:
    """
    Executes Python code in a restricted environment.
    """

    def __init__(
        self,
        tools: Dict[str, Callable],
        limits: SandboxLimits | None = None,
        state_summary_getter: Optional[Callable[[], Dict[str, Any]]] = None,
    ):
        self.tools_api = ToolsAPI(tools, state_summary_getter=state_summary_getter)
        self.limits = limits or SandboxLimits()

    def _build_restricted_globals(self) -> Dict[str, Any]:
        base_builtins = {}
        if isinstance(safe_globals, dict):
            maybe_builtins = safe_globals.get("__builtins__", {})
            if isinstance(maybe_builtins, dict):
                base_builtins = maybe_builtins.copy()

        write_guard = full_write_guard if callable(full_write_guard) else (lambda value: value)

        base_builtins.update(
            {
                "__import__": _safe_import,
                "_getattr_": safer_getattr,
                "_getitem_": lambda obj, index: obj[index],
                "_getiter_": iter,
                "_inplacevar_": _inplacevar,
                "_write_": write_guard,
                "float": float,
                "int": int,
                "str": str,
                "bool": bool,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "type": type,
                "sum": sum,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "reversed": reversed,
                "zip": zip,
                "all": all,
                "any": any,
            }
        )

        class SafePrinter:
            """Captures print output instead of writing to stdout/stderr."""

            def __init__(self):
                self.output: List[str] = []

            def __call__(self, *args):
                return self

            def _call_print(self, *args):
                self.output.append(" ".join(str(arg) for arg in args))

        return {
            "__builtins__": base_builtins,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_unpack_sequence_": guarded_unpack_sequence,
            "_getattr_": safer_getattr,
            "_write_": write_guard,
            "_print_": SafePrinter(),
            "__name__": "restricted_execution",
            "__metaclass__": type,
            "json": json,
            "tools": self.tools_api,
            # Compatibility alias for model outputs that instantiate `Tools()`.
            "Tools": lambda: self.tools_api,
        }

    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute code in a restricted environment.

        Returns:
            Dictionary with success flag, result/error, locals, tool log, and sandbox metrics.
        """
        self.tools_api.reset_call_log()
        started = time.perf_counter()

        try:
            compile_started = time.perf_counter()
            compile_result = compile_restricted(code, filename="<inline code>", mode="exec")
            compile_ms = (time.perf_counter() - compile_started) * 1000

            if hasattr(compile_result, "errors") and compile_result.errors:
                return {
                    "success": False,
                    "error": f"Compilation errors: {compile_result.errors}",
                    "tool_calls": self.tools_api.get_call_log(),
                    "sandbox": {
                        "compile_ms": round(compile_ms, 3),
                        "execution_ms": 0.0,
                        "total_ms": round((time.perf_counter() - started) * 1000, 3),
                        "timeout_seconds": self.limits.timeout_seconds,
                        "max_memory_mb": self.limits.max_memory_mb,
                    },
                }

            byte_code = compile_result.code if hasattr(compile_result, "code") else compile_result
            if not hasattr(byte_code, "co_code"):
                return {
                    "success": False,
                    "error": "Code compilation failed - no valid code object produced",
                    "tool_calls": self.tools_api.get_call_log(),
                    "sandbox": {
                        "compile_ms": round(compile_ms, 3),
                        "execution_ms": 0.0,
                        "total_ms": round((time.perf_counter() - started) * 1000, 3),
                        "timeout_seconds": self.limits.timeout_seconds,
                        "max_memory_mb": self.limits.max_memory_mb,
                    },
                }

            restricted_globals = self._build_restricted_globals()
            restricted_locals: Dict[str, Any] = {}

            exec_started = time.perf_counter()
            with _memory_limit(self.limits.max_memory_mb):
                with _execution_timeout(self.limits.timeout_seconds):
                    exec(byte_code, restricted_globals, restricted_locals)
            execution_ms = (time.perf_counter() - exec_started) * 1000

            result = restricted_locals.get("result", None)
            serializable_locals = {}
            for key, value in restricted_locals.items():
                if key.startswith("_"):
                    continue
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    serializable_locals[key] = value

            return {
                "success": True,
                "result": result,
                "locals": serializable_locals,
                "tool_calls": self.tools_api.get_call_log(),
                "sandbox": {
                    "compile_ms": round(compile_ms, 3),
                    "execution_ms": round(execution_ms, 3),
                    "total_ms": round((time.perf_counter() - started) * 1000, 3),
                    "timeout_seconds": self.limits.timeout_seconds,
                    "max_memory_mb": self.limits.max_memory_mb,
                },
            }
        except TimeoutError as exc:
            return {
                "success": False,
                "error": f"Timeout error: {exc}",
                "tool_calls": self.tools_api.get_call_log(),
                "sandbox": {
                    "compile_ms": 0.0,
                    "execution_ms": 0.0,
                    "total_ms": round((time.perf_counter() - started) * 1000, 3),
                    "timeout_seconds": self.limits.timeout_seconds,
                    "max_memory_mb": self.limits.max_memory_mb,
                },
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Execution error: {exc}",
                "tool_calls": self.tools_api.get_call_log(),
                "sandbox": {
                    "compile_ms": 0.0,
                    "execution_ms": 0.0,
                    "total_ms": round((time.perf_counter() - started) * 1000, 3),
                    "timeout_seconds": self.limits.timeout_seconds,
                    "max_memory_mb": self.limits.max_memory_mb,
                },
            }

    def run_security_evaluation(self) -> Dict[str, Any]:
        """
        Run targeted jailbreak/security checks against the sandbox.
        """
        scenarios = [
            {
                "name": "allow_safe_json_import",
                "code": "import json\nresult = json.dumps({'ok': True})",
                "expect_success": True,
            },
            {
                "name": "block_environment_access",
                "code": "import os\nresult = os.environ.get('HOME')",
                "expect_success": False,
            },
            {
                "name": "block_raw_network_access",
                "code": "import socket\ns = socket.socket()\nresult = 'socket-created'",
                "expect_success": False,
            },
            {
                "name": "block_file_read_builtin_open",
                "code": "f = open('/etc/passwd', 'r')\nresult = f.read()",
                "expect_success": False,
            },
            {
                "name": "stop_runaway_loop",
                "code": "while True:\n    pass\nresult = 'done'",
                "expect_success": False,
            },
        ]

        results = []
        passed = 0

        for scenario in scenarios:
            execution = self.execute(scenario["code"])
            scenario_passed = execution["success"] == scenario["expect_success"]
            if scenario_passed:
                passed += 1
            results.append(
                {
                    "name": scenario["name"],
                    "passed": scenario_passed,
                    "expect_success": scenario["expect_success"],
                    "actual_success": execution["success"],
                    "error": execution.get("error"),
                }
            )

        return {
            "passed": passed,
            "total": len(scenarios),
            "pass_rate": passed / len(scenarios) if scenarios else 0.0,
            "results": results,
        }


def test_executor():
    """Manual smoke test for the sandbox executor."""
    from tools.business_tools import get_tools, get_state

    state = get_state()
    state.reset()
    executor = CodeExecutor(get_tools())

    code = """
import json

tools.create_transaction("expense", "rent", 1200, "Office rent", "checking")
summary = json.loads(tools.get_financial_summary())
result = summary["summary"]["total_expenses"]
"""

    print("Execution result:")
    print(executor.execute(code))
    print()
    print("Security evaluation:")
    print(executor.run_security_evaluation())


if __name__ == "__main__":
    test_executor()
