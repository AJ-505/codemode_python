"""
Code Mode agent - LLM writes code to call tools instead of using function calling.

This implementation follows the Code Mode pattern described in:
https://www.anthropic.com/research/building-effective-agents

Key benefits:
- Batches multiple tool calls in a single code execution
- Reduces iteration count and latency
- Lower token usage compared to traditional function calling
- Enables more complex control flow and data manipulation
"""

import anthropic
import json
import re
from typing import Dict, List, Any, Callable, Optional
from sandbox.executor import CodeExecutor


class CodeModeAgent:
    """
    Agent that generates Python code to call tools instead of using function calling.

    The agent leverages the LLM's code generation capabilities to:
    1. Write efficient Python code that calls multiple tools
    2. Use loops, conditionals, and variables for complex workflows
    3. Execute code in a sandboxed environment
    4. Iterate on errors with improved prompts
    """

    def __init__(
        self,
        api_key: str,
        tools: Dict[str, Callable],
        tools_api: str,
        model_name: Optional[str] = None,
        **_: Any,
    ):
        """
        Initialize the Code Mode agent.

        Args:
            api_key: Anthropic API key
            tools: Dictionary of available tools (name -> function)
            tools_api: Python API definition string with type hints and examples
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.tools = tools
        self.tools_api = tools_api
        self.executor = CodeExecutor(tools)
        self.model = model_name or "claude-3-haiku-20240307"
        self._state_manager = self._resolve_state_manager()

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
            "Use the pre-provided `tools` object directly; do not call `Tools()`.",
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
        """Create the system prompt for Code Mode."""
        return f"""Write Python that uses the provided tools to solve the user request.

Tools API:

{self.tools_api}

Rules:
- Respond with one ```python``` block only.
- Use only `import json`; other imports are blocked.
- Parse all tool responses via `json.loads(...)`.
- Set the final user-facing output in `result`.
- Use the pre-provided `tools` object directly; do not call `Tools()`.
- Do not use type annotations.
- Do not use private names (for example names starting with `_`) or `getattr`.
- Do not use `str.format`; use f-strings or `%` formatting.
- Prefer batched logic (loops/lists) over repeated single-step code.
- For invoice items, use `price` (not `unit_price`).
- Avoid duplicate financial side-effects:
  `record_partial_payment` and `update_invoice_status(..., "paid")` already record invoice-payment income.
"""

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the agent with Code Mode.

        The agent will:
        1. Generate Python code to accomplish the task
        2. Execute the code in a sandbox
        3. Iterate on errors if execution fails
        4. Return the final result when code executes successfully

        Args:
            user_message: The user's request
            max_iterations: Maximum number of code generation attempts (default: 10)

        Returns:
            Dictionary containing:
            - success: Whether the task completed successfully
            - response: Final response text
            - code_executions: List of code execution attempts
            - iterations: Number of iterations taken
            - input_tokens: Total input tokens used
            - output_tokens: Total output tokens used
            - error: Error message if max iterations reached
        """
        messages = [{"role": "user", "content": user_message}]
        code_executions = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0
        system_prompt = self._create_system_prompt()

        while iterations < max_iterations:
            iterations += 1

            # Call the LLM
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )

            total_input_tokens += response.usage.input_tokens
            total_output_tokens += response.usage.output_tokens

            # Extract the response text
            response_text = ""
            for block in response.content:
                if block.type == "text":
                    response_text += block.text

            # Check if response contains code
            code = self._extract_code_candidate(response_text)

            if not code:
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

            # Execute the code
            state_snapshot = self._snapshot_state()
            execution_result = self.executor.execute(code)

            code_executions.append({
                "code": code,
                "execution_result": execution_result,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            })

            if not execution_result["success"]:
                self._restore_state(state_snapshot)
                messages.append({"role": "assistant", "content": f"```python\n{code}\n```"})
                messages.append({"role": "user", "content": self._build_retry_prompt(execution_result.get("error"))})
                messages = self._trim_messages(messages)
                continue

            # Code executed successfully
            result = execution_result.get("result")

            if result is not None:
                # We have a final result
                # Format the result nicely
                if isinstance(result, str):
                    final_response = result
                else:
                    final_response = json.dumps(result, indent=2)

                return {
                    "success": True,
                    "response": final_response,
                    "code_executions": code_executions,
                    "iterations": iterations,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                }
            else:
                # No result yet, continue conversation with compact feedback
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
            "iterations": iterations,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
        }


def test_agent():
    """Test the Code Mode agent."""
    import os
    from dotenv import load_dotenv
    from tools.example_tools import get_tools, get_code_mode_api

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment")
        return

    agent = CodeModeAgent(api_key, get_tools(), get_code_mode_api())

    # Test query
    result = agent.run("What's the weather in Tokyo and how much is 25 celsius in fahrenheit?")

    print("Code Mode Agent Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    test_agent()
