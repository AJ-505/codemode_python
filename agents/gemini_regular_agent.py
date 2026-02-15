"""
Regular agent using Gemini with traditional function/tool calling.
"""

import google.generativeai as genai
import json
from typing import Dict, List, Any, Callable, Optional


class GeminiRegularAgent:
    """Agent that uses Gemini's function calling."""

    def __init__(
        self,
        api_key: str,
        tools: Dict[str, Callable],
        tool_schemas: List[Dict[str, Any]],
        model_name: Optional[str] = None,
        **_: Any,
    ):
        """
        Initialize the Gemini regular agent.

        Args:
            api_key: Google API key
            tools: Dictionary of available tools
            tool_schemas: Tool schemas in Anthropic format (will be converted)
        """
        genai.configure(api_key=api_key)
        self.tools = tools
        self.tool_schemas = self._convert_schemas_to_gemini(tool_schemas)
        self.model_name = model_name or "gemini-2.0-flash-exp"
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=self.tool_schemas
        )

    def _convert_schemas_to_gemini(self, anthropic_schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic tool schemas to Gemini format."""
        gemini_tools = []

        for schema in anthropic_schemas:
            # Extract parameters from Anthropic's input_schema
            input_schema = schema.get("input_schema", {})
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])

            # Convert to Gemini format
            gemini_params = self._convert_properties(properties)

            gemini_tool = {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": {
                    "type": "OBJECT",
                    "properties": gemini_params,
                    "required": required
                }
            }

            gemini_tools.append(gemini_tool)

        return gemini_tools

    def _convert_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively convert property definitions to Gemini format."""
        gemini_params = {}

        for prop_name, prop_def in properties.items():
            param = {
                "type": self._convert_type(prop_def.get("type")),
                "description": prop_def.get("description", "")
            }

            # Handle enums
            if "enum" in prop_def:
                param["enum"] = prop_def["enum"]

            # Handle arrays
            if prop_def.get("type") == "array" and "items" in prop_def:
                items_def = prop_def["items"]
                items_type = items_def.get("type", "string")

                if items_type == "object":
                    # Handle array of objects - recursively convert nested properties
                    nested_properties = items_def.get("properties", {})
                    nested_required = items_def.get("required", [])
                    param["items"] = {
                        "type": "OBJECT",
                        "properties": self._convert_properties(nested_properties),
                        "required": nested_required
                    }
                else:
                    # Simple array type
                    param["items"] = {
                        "type": self._convert_type(items_type)
                    }

            # Handle nested objects (not in arrays)
            elif prop_def.get("type") == "object" and "properties" in prop_def:
                nested_properties = prop_def.get("properties", {})
                nested_required = prop_def.get("required", [])
                param["properties"] = self._convert_properties(nested_properties)
                param["required"] = nested_required

            gemini_params[prop_name] = param

        return gemini_params

    def _convert_type(self, anthropic_type: str) -> str:
        """Convert Anthropic type to Gemini type (uppercase enum)."""
        type_map = {
            "string": "STRING",
            "number": "NUMBER",
            "integer": "INTEGER",
            "boolean": "BOOLEAN",
            "array": "ARRAY",
            "object": "OBJECT"
        }
        return type_map.get(anthropic_type, "STRING")

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the agent with traditional tool calling.

        Args:
            user_message: The user's request
            max_iterations: Maximum number of tool calling iterations

        Returns:
            Dictionary with response, tool calls, and metrics
        """
        chat = self.model.start_chat(enable_automatic_function_calling=False)
        tool_calls = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0

        try:
            response = chat.send_message(user_message)

            while iterations < max_iterations:
                iterations += 1

                # Count tokens (approximate)
                if hasattr(response, 'usage_metadata'):
                    total_input_tokens += response.usage_metadata.prompt_token_count
                    total_output_tokens += response.usage_metadata.candidates_token_count

                # Check if there are function calls
                if not response.candidates:
                    break

                candidate = response.candidates[0]

                # Check for function calls in parts
                function_calls_in_response = []
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls_in_response.append(part.function_call)

                if not function_calls_in_response:
                    # No more function calls, get final text
                    final_text = ""
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            final_text += part.text

                    return {
                        "success": True,
                        "response": final_text,
                        "tool_calls": tool_calls,
                        "iterations": iterations,
                        "input_tokens": total_input_tokens,
                        "output_tokens": total_output_tokens,
                    }

                # Execute function calls
                function_responses = []
                for func_call in function_calls_in_response:
                    tool_name = func_call.name
                    tool_args = dict(func_call.args)

                    # Execute the tool
                    if tool_name in self.tools:
                        try:
                            result = self.tools[tool_name](**tool_args)
                            function_responses.append(
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=tool_name,
                                        response={"result": result}
                                    )
                                )
                            )

                            # Track tool call
                            tool_calls.append({
                                "name": tool_name,
                                "input": tool_args,
                                "result": result,
                            })
                        except Exception as e:
                            function_responses.append(
                                genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=tool_name,
                                        response={"error": str(e)}
                                    )
                                )
                            )
                    else:
                        function_responses.append(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"error": f"Unknown tool: {tool_name}"}
                                )
                            )
                        )

                # Send function responses back
                response = chat.send_message(function_responses)

            return {
                "success": False,
                "error": "Max iterations reached",
                "tool_calls": tool_calls,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_calls": tool_calls,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }


def test_agent():
    """Test the Gemini regular agent."""
    import os
    from dotenv import load_dotenv
    from tools.business_tools import get_tools, get_tool_schemas, get_state

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        return

    # Reset state
    state = get_state()
    state.reset()

    agent = GeminiRegularAgent(api_key, get_tools(), get_tool_schemas())

    # Test query
    result = agent.run("Record a $2500 rent expense and a $5000 consulting income. Then show me the checking account balance.")

    print("Gemini Regular Agent Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    test_agent()
