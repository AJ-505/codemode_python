"""
Regular agent using OpenAI-compatible chat completions with tool calling.

This works with:
- OpenAI API
- OpenAI-compatible provider endpoints (e.g., GLM, Gemini OpenAI-compatible API)
"""

import json
import time
from typing import Dict, List, Any, Callable, Optional

from openai import OpenAI


class OpenAICompatibleRegularAgent:
    """Agent that uses OpenAI-compatible function/tool calling."""

    def __init__(
        self,
        api_key: str,
        tools: Dict[str, Callable],
        tool_schemas: List[Dict[str, Any]],
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        **_: Any,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        self.tools = tools
        self.openai_tools = self._convert_tool_schemas(tool_schemas)
        self.model_name = model_name or "gpt-4o-mini"

    def _convert_tool_schemas(self, schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style schemas to OpenAI tool schema format."""
        converted = []
        for schema in schemas:
            converted.append(
                {
                    "type": "function",
                    "function": {
                        "name": schema["name"],
                        "description": schema.get("description", ""),
                        "parameters": schema.get("input_schema", {"type": "object", "properties": {}, "required": []}),
                    },
                }
            )
        return converted

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_message}]
        tool_calls: List[Dict[str, Any]] = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0

        try:
            while iterations < max_iterations:
                iterations += 1

                if iterations > 1:
                    time.sleep(0.05)

                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=self.openai_tools,
                    tool_choice="auto",
                    max_tokens=4096,
                )

                if response.usage:
                    total_input_tokens += response.usage.prompt_tokens or 0
                    total_output_tokens += response.usage.completion_tokens or 0

                if not response.choices:
                    return {
                        "success": False,
                        "error": "No response choices returned by model",
                        "tool_calls": tool_calls,
                        "iterations": iterations,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                    }

                message = response.choices[0].message
                model_tool_calls = message.tool_calls or []

                if not model_tool_calls:
                    return {
                        "success": True,
                        "response": message.content or "",
                        "tool_calls": tool_calls,
                        "iterations": iterations,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                    }

                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [tc.model_dump() for tc in model_tool_calls],
                    }
                )

                for tool_call in model_tool_calls:
                    tool_name = tool_call.function.name
                    raw_args = tool_call.function.arguments or "{}"

                    try:
                        tool_input = json.loads(raw_args) if raw_args else {}
                    except json.JSONDecodeError as exc:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": f"Error: Invalid JSON tool arguments: {exc}",
                            }
                        )
                        continue

                    if tool_name not in self.tools:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": f"Error: Unknown tool: {tool_name}",
                            }
                        )
                        continue

                    try:
                        result = self.tools[tool_name](**tool_input)
                        tool_calls.append(
                            {
                                "name": tool_name,
                                "input": tool_input,
                                "result": result,
                            }
                        )
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": result,
                            }
                        )
                    except Exception as exc:
                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": f"Error: {exc}",
                            }
                        )

            return {
                "success": False,
                "error": "Max iterations reached",
                "tool_calls": tool_calls,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }
        except Exception as exc:
            return {
                "success": False,
                "error": str(exc),
                "tool_calls": tool_calls,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }
