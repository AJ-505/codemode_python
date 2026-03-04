"""
Code Mode agent using OpenAI-compatible chat completions.
"""

import json
import re
from typing import Dict, Any, Callable, Optional, List

from openai import OpenAI

from sandbox.executor import CodeExecutor


class OpenAICompatibleCodeModeAgent:
    """Agent that generates Python code to call tools via an OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str,
        tools: Dict[str, Callable],
        tools_api: str,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        **_: Any,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        self.tools = tools
        self.tools_api = tools_api
        if not model_name:
            raise ValueError("model_name is required for OpenAICompatibleCodeModeAgent")
        self.model_name = model_name
        self.max_output_tokens = 4096
        self._token_limit_param = "max_completion_tokens" if self.model_name.lower().startswith("gpt-5") else "max_tokens"
        self._state_manager = self._resolve_state_manager()
        self._tool_manifest = self._resolve_tool_manifest()
        self.executor = CodeExecutor(
            tools,
            state_summary_getter=self._get_state_summary,
            tool_manifest=self._tool_manifest,
        )

    def _get_state_summary(self) -> Optional[Dict[str, Any]]:
        if self._state_manager is None:
            return None
        try:
            if hasattr(self._state_manager, "get_summary"):
                return self._state_manager.get_summary()
        except Exception:
            return None
        return None

    @staticmethod
    def _is_unsupported_parameter_error(exc: Exception, param_name: str) -> bool:
        """Check whether the provider rejected a specific request parameter."""
        message = str(exc).lower()
        unsupported = "unsupported parameter" in message
        mentions_param = (
            f"'{param_name}'" in message
            or f"\"{param_name}\"" in message
            or f" {param_name}" in message
        )
        return unsupported and mentions_param

    def _create_chat_completion(self, messages: List[Dict[str, Any]]):
        """Create a chat completion with compatibility fallback for token-limit params."""
        base_kwargs: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
        }
        primary = self._token_limit_param
        fallback = "max_completion_tokens" if primary == "max_tokens" else "max_tokens"
        last_exc: Optional[Exception] = None

        for token_param in [primary, fallback]:
            request_kwargs = dict(base_kwargs)
            request_kwargs[token_param] = self.max_output_tokens
            try:
                response = self.client.chat.completions.create(**request_kwargs)
                self._token_limit_param = token_param
                return response
            except Exception as exc:
                last_exc = exc
                if self._is_unsupported_parameter_error(exc, token_param):
                    continue
                raise

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Failed to create chat completion")

    @staticmethod
    def _trim_messages(messages: List[Dict[str, Any]], max_messages: int = 10) -> List[Dict[str, Any]]:
        """Keep prompt history compact while preserving the original user request."""
        if len(messages) <= max_messages:
            return messages
        return [messages[0], *messages[-(max_messages - 1):]]

    @staticmethod
    def _short_error(error: Any, max_len: int = 220) -> str:
        text = str(error or "Unknown execution error").strip()
        first_line = text.splitlines()[0] if text else "Unknown execution error"
        return first_line if len(first_line) <= max_len else first_line[: max_len - 3] + "..."

    @staticmethod
    def _extract_code_candidate(response_text: str) -> Optional[str]:
        text = (response_text or "").strip()
        if not text:
            return None

        fenced_patterns = [
            r"```python\s*(.*?)```",
            r"```py\s*(.*?)```",
            r"```(?:[a-zA-Z0-9_+-]*)\s*(.*?)```",
        ]
        for pattern in fenced_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            if matches:
                candidate = matches[0].strip()
                if candidate:
                    return candidate

        code_markers = (
            "tools.",
            "json.loads(",
            "result =",
            "import json",
            "for ",
            "while ",
            "if ",
            "def ",
        )
        if any(marker in text for marker in code_markers):
            return text

        return None

    def _build_retry_prompt(self, execution_error: Any) -> str:
        short_error = self._short_error(execution_error)
        error_lower = short_error.lower()
        hints = [
            "Use only `import json`.",
            "Return exactly one corrected ```python``` block and no extra text.",
            "Set the final answer in a variable named `result`.",
            "Prefer progressive discovery: tools.ls(...), tools.read(...), then tools.call(path, args).",
        ]
        if "_write_" in short_error:
            hints.append("Avoid dict/list item writes like `obj[key] = ...`; build new dict/list values.")
        if "getattr" in error_lower:
            hints.append("Do not call `getattr`; read dict keys directly.")
        if "blocked by sandbox policy" in error_lower or "import '" in error_lower:
            hints.append("Do not import modules besides `json`.")
        if "tools" in error_lower and "not defined" in error_lower:
            hints.append("Never instantiate tools; runtime already provides `tools`.")
        if "format*()" in error_lower or "format methods of `str`" in error_lower:
            hints.append("Do not use `str.format`; use f-strings or `%` formatting.")
        if "'price'" in short_error:
            hints.append("Invoice item objects must use the key `price` (not `unit_price`).")
        if "augmented assignment of object items and slices" in error_lower:
            hints.append("Do not use `obj[key] += ...`; compute value first, then assign.")

        hint_lines = "\n".join(f"- {hint}" for hint in hints[:6])
        return (
            f"Execution failed: {short_error}\n"
            "Fix the code and return one corrected Python block.\n"
            f"Constraints:\n{hint_lines}"
        )

    def _resolve_state_manager(self):
        """Resolve optional benchmark state manager for rollback safety."""
        try:
            from tools import get_state

            state = get_state()
            if hasattr(state, "snapshot") and hasattr(state, "restore"):
                return state
        except Exception:
            return None
        return None

    @staticmethod
    def _resolve_tool_manifest() -> Optional[Dict[str, Dict[str, Any]]]:
        try:
            from tools import get_tool_fs_manifest

            manifest = get_tool_fs_manifest()
            if isinstance(manifest, dict):
                return manifest
        except Exception:
            return None
        return None

    def _snapshot_state(self):
        if self._state_manager is None:
            return None
        try:
            return self._state_manager.snapshot()
        except Exception:
            return None

    def _restore_state(self, snapshot: Any) -> None:
        if self._state_manager is None or snapshot is None:
            return
        try:
            self._state_manager.restore(snapshot)
        except Exception:
            pass

    def _create_system_prompt(self) -> str:
        return f"""Write Python that uses the provided tools to solve the user request.

Tools API:

{self.tools_api}

Rules:
- Respond with one ```python``` block only.
- Use only `import json`; other imports are blocked.
- Parse all tool responses via `json.loads(...)`.
- Set the final user-facing output in `result`.
- Progressive discovery is the default strategy:
  - discover with `tools.ls(path)`
  - inspect with `tools.read(path)`
  - invoke with `tools.call(path, args_dict)`
- If a tool is already known, direct calls can also work.
- Do not call `Tools()`.
- Do not use type annotations.
- Do not use private names (for example names starting with `_`) or `getattr`.
- Do not use `str.format`; use f-strings or `%` formatting.
- Prefer batched logic (loops/lists) over repeated single-step code.
- For invoice items, use `price` (not `unit_price`).
- Avoid duplicate financial side-effects:
  `record_partial_payment` and `update_invoice_status(..., "paid")` already record invoice-payment income.
"""

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_message}]
        code_executions = []
        iteration_trace: List[Dict[str, Any]] = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0
        system_prompt = self._create_system_prompt()

        try:
            while iterations < max_iterations:
                iterations += 1

                response = self._create_chat_completion(
                    [
                        {"role": "system", "content": system_prompt},
                        *messages,
                    ]
                )

                if response.usage:
                    total_input_tokens += response.usage.prompt_tokens or 0
                    total_output_tokens += response.usage.completion_tokens or 0

                if not response.choices:
                    return {
                        "success": False,
                        "error": "No response choices returned by model",
                        "code_executions": code_executions,
                        "iterations": iterations,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                    }

                response_text = response.choices[0].message.content or ""
                iteration_event: Dict[str, Any] = {
                    "iteration": iterations,
                    "model_response": response_text,
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                    "state_before": self._get_state_summary(),
                }

                code = self._extract_code_candidate(response_text)
                if not code:
                    iteration_event.update(
                        {
                            "event": "non_code_response",
                            "execution_success": None,
                            "error": "No executable code candidate found",
                            "state_after": self._get_state_summary(),
                        }
                    )
                    iteration_trace.append(iteration_event)
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Return one executable ```python``` block only. "
                                "Do not include explanations. "
                                "Use the existing `tools` object and set final output in `result`."
                            ),
                        }
                    )
                    messages = self._trim_messages(messages)
                    continue

                state_snapshot = self._snapshot_state()
                execution_result = self.executor.execute(code)
                state_after_execution = self._get_state_summary()
                code_executions.append(
                    {
                        "code": code,
                        "execution_result": execution_result,
                        "state_before": iteration_event.get("state_before"),
                        "state_after": state_after_execution,
                    }
                )
                iteration_event.update(
                    {
                        "event": "code_execution",
                        "code": code,
                        "execution_success": execution_result.get("success", False),
                        "error": execution_result.get("error"),
                        "tool_calls": execution_result.get("tool_calls", []),
                        "sandbox": execution_result.get("sandbox", {}),
                        "state_after": state_after_execution,
                    }
                )
                iteration_trace.append(iteration_event)

                if not execution_result["success"]:
                    self._restore_state(state_snapshot)
                    messages.append({"role": "assistant", "content": f"```python\n{code}\n```"})
                    messages.append(
                        {
                            "role": "user",
                            "content": self._build_retry_prompt(execution_result.get("error")),
                        }
                    )
                    messages = self._trim_messages(messages)
                    continue

                result = execution_result.get("result")
                if result is not None:
                    return {
                        "success": True,
                        "response": result if isinstance(result, str) else json.dumps(result, indent=2),
                        "code_executions": code_executions,
                        "iteration_trace": iteration_trace,
                        "iterations": iterations,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                    }

                local_keys = sorted((execution_result.get("locals") or {}).keys())
                visible_keys = ", ".join(local_keys[:12]) if local_keys else "none"
                messages.append({"role": "assistant", "content": f"```python\n{code}\n```"})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Code executed but `result` is missing. "
                            f"Current local keys: {visible_keys}. "
                            "Return corrected code that sets `result`."
                        ),
                    }
                )
                messages = self._trim_messages(messages)

            return {
                "success": False,
                "error": "Max iterations reached",
                "code_executions": code_executions,
                "iteration_trace": iteration_trace,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "code_executions": code_executions,
                "iteration_trace": iteration_trace,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }
