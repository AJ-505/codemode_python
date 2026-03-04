"""
Regular agent using OpenAI-compatible chat completions with tool calling.

This works with:
- OpenAI API
- OpenAI-compatible provider endpoints (e.g., GLM, Gemini OpenAI-compatible API)
"""

import json
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
        self.client = (
            OpenAI(api_key=api_key, base_url=base_url)
            if base_url
            else OpenAI(api_key=api_key)
        )
        self.tools = tools
        self.openai_tools = self._convert_tool_schemas(tool_schemas)
        if not model_name:
            raise ValueError("model_name is required for OpenAICompatibleRegularAgent")
        self.model_name = model_name
        self.max_output_tokens = 4096
        self._token_limit_param = (
            "max_completion_tokens"
            if self.model_name.lower().startswith("gpt-5")
            else "max_tokens"
        )
        self._use_responses_api = "codex" in self.model_name.lower()

    @staticmethod
    def _is_unsupported_parameter_error(exc: Exception, param_name: str) -> bool:
        """Check whether the provider rejected a specific request parameter."""
        message = str(exc).lower()
        unsupported = "unsupported parameter" in message
        mentions_param = (
            f"'{param_name}'" in message
            or f'"{param_name}"' in message
            or f" {param_name}" in message
        )
        return unsupported and mentions_param

    def _create_chat_completion(self, messages: List[Dict[str, Any]]):
        """Create a chat completion with compatibility fallback for token-limit params."""
        base_kwargs: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "tools": self.openai_tools,
            "tool_choice": "auto",
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
    def _is_not_chat_model_error(exc: Exception) -> bool:
        text = str(exc).lower()
        return "not a chat model" in text and "chat/completions" in text

    def _responses_tools(self) -> List[Dict[str, Any]]:
        payload: List[Dict[str, Any]] = []
        for tool in self.openai_tools:
            fn = tool.get("function", {})
            payload.append(
                {
                    "type": "function",
                    "name": fn.get("name"),
                    "description": fn.get("description", ""),
                    "parameters": fn.get(
                        "parameters",
                        {"type": "object", "properties": {}, "required": []},
                    ),
                }
            )
        return payload

    @staticmethod
    def _response_usage_tokens(response: Any) -> tuple[int, int]:
        usage = getattr(response, "usage", None)
        if usage is None:
            return (0, 0)
        in_tokens = (
            getattr(usage, "input_tokens", None)
            or getattr(usage, "prompt_tokens", None)
            or 0
        )
        out_tokens = (
            getattr(usage, "output_tokens", None)
            or getattr(usage, "completion_tokens", None)
            or 0
        )
        return (int(in_tokens), int(out_tokens))

    @staticmethod
    def _response_text(response: Any) -> str:
        text = getattr(response, "output_text", None)
        if isinstance(text, str):
            return text
        chunks: List[str] = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) != "message":
                continue
            for content in getattr(item, "content", []) or []:
                value = getattr(content, "text", None)
                if isinstance(value, str):
                    chunks.append(value)
        return "".join(chunks)

    @staticmethod
    def _response_tool_calls(response: Any) -> List[Dict[str, Any]]:
        calls: List[Dict[str, Any]] = []
        for item in getattr(response, "output", []) or []:
            if getattr(item, "type", None) != "function_call":
                continue
            calls.append(
                {
                    "name": getattr(item, "name", None),
                    "arguments": getattr(item, "arguments", "{}") or "{}",
                    "call_id": getattr(item, "call_id", None)
                    or getattr(item, "id", None),
                }
            )
        return calls

    def _run_with_responses(
        self, user_message: str, max_iterations: int, tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        total_input_tokens = 0
        total_output_tokens = 0
        iterations = 0
        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": user_message},
            ],
            tools=self._responses_tools(),
            tool_choice="auto",
            max_output_tokens=self.max_output_tokens,
        )

        while iterations < max_iterations:
            iterations += 1
            in_tokens, out_tokens = self._response_usage_tokens(response)
            total_input_tokens += in_tokens
            total_output_tokens += out_tokens
            model_tool_calls = self._response_tool_calls(response)

            if not model_tool_calls:
                return {
                    "success": True,
                    "response": self._response_text(response),
                    "tool_calls": tool_calls,
                    "iterations": iterations,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                }

            function_outputs = []
            for tool_call in model_tool_calls:
                tool_name = tool_call.get("name")
                raw_args = tool_call.get("arguments") or "{}"
                call_id = tool_call.get("call_id")
                try:
                    tool_input = json.loads(raw_args) if raw_args else {}
                except json.JSONDecodeError as exc:
                    function_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": f"Error: Invalid JSON tool arguments: {exc}",
                        }
                    )
                    continue

                if tool_name not in self.tools:
                    function_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": f"Error: Unknown tool: {tool_name}",
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
                    function_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": result,
                        }
                    )
                except Exception as exc:
                    function_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": f"Error: {exc}",
                        }
                    )

            response = self.client.responses.create(
                model=self.model_name,
                previous_response_id=getattr(response, "id", None),
                input=function_outputs,
                tools=self._responses_tools(),
                tool_choice="auto",
                max_output_tokens=self.max_output_tokens,
            )

        return {
            "success": False,
            "error": "Max iterations reached",
            "tool_calls": tool_calls,
            "iterations": iterations,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
        }

    def _convert_tool_schemas(
        self, schemas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert Anthropic-style schemas to OpenAI tool schema format."""
        converted = []
        for schema in schemas:
            converted.append(
                {
                    "type": "function",
                    "function": {
                        "name": schema["name"],
                        "description": schema.get("description", ""),
                        "parameters": schema.get(
                            "input_schema",
                            {"type": "object", "properties": {}, "required": []},
                        ),
                    },
                }
            )
        return converted

    @staticmethod
    def _system_prompt() -> str:
        return (
            "You are a tool-grounded workflow agent. "
            "Execute all explicitly requested operations with tool calls, do not skip steps, "
            "and do not claim completion without tool evidence. "
            "When the task asks for state summaries/balances, call the relevant read tools before final response."
        )

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": user_message},
        ]
        tool_calls: List[Dict[str, Any]] = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0

        try:
            if self._use_responses_api:
                return self._run_with_responses(user_message, max_iterations, tool_calls)

            while iterations < max_iterations:
                iterations += 1

                try:
                    response = self._create_chat_completion(messages)
                except Exception as exc:
                    if self._is_not_chat_model_error(exc):
                        self._use_responses_api = True
                        return self._run_with_responses(
                            user_message, max_iterations, tool_calls
                        )
                    raise

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
