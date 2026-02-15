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
        self.executor = CodeExecutor(tools)
        self.model_name = model_name or "gpt-4o-mini"

    def _create_system_prompt(self) -> str:
        return f"""You are an AI assistant that helps users by writing Python code to accomplish tasks.

You have access to the following tools through a Python API:

{self.tools_api}

When the user asks you to do something, write efficient Python code that:
1. Batches multiple tool calls together when possible
2. Stores intermediate results in variables for reuse
3. Always stores the final user-facing result in a variable called 'result'
4. Uses the 'json' module to parse JSON responses from tools

IMPORTANT:
- Your response should ONLY contain Python code wrapped in ```python code blocks
- Do NOT include any explanatory text outside the code block
- The code will run in a restricted sandbox
- All tool responses are JSON strings, so use json.loads()
- DO NOT use type annotations (e.g., variable: Type = value)
"""

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_message}]
        code_executions = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0

        try:
            while iterations < max_iterations:
                iterations += 1

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self._create_system_prompt()},
                        *messages,
                    ],
                    max_tokens=4096,
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

                code_blocks = re.findall(r"```python\n(.*?)\n```", response_text, re.DOTALL)
                if not code_blocks:
                    return {
                        "success": True,
                        "response": response_text,
                        "code_executions": code_executions,
                        "iterations": iterations,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                    }

                code = code_blocks[0]
                execution_result = self.executor.execute(code)
                code_executions.append(
                    {
                        "code": code,
                        "execution_result": execution_result,
                    }
                )

                if not execution_result["success"]:
                    messages.append({"role": "assistant", "content": response_text})
                    messages.append(
                        {
                            "role": "user",
                            "content": (
                                "Code execution failed with error:\n"
                                f"{execution_result['error']}\n\n"
                                "Fix the code and return only corrected Python code."
                            ),
                        }
                    )
                    continue

                result = execution_result.get("result")
                if result is not None:
                    return {
                        "success": True,
                        "response": result if isinstance(result, str) else json.dumps(result, indent=2),
                        "code_executions": code_executions,
                        "iterations": iterations,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                    }

                messages.append({"role": "assistant", "content": response_text})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Code executed but 'result' is missing.\n"
                            f"Locals: {json.dumps(execution_result.get('locals', {}))}\n\n"
                            "Provide corrected code that sets the final result variable."
                        ),
                    }
                )

            return {
                "success": False,
                "error": "Max iterations reached",
                "code_executions": code_executions,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "code_executions": code_executions,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }
