"""
Regular agent using traditional function/tool calling.

This is the baseline implementation using Anthropic's native tool calling
feature for comparison with Code Mode.
"""

import anthropic
import json
import time
from typing import Dict, List, Any, Callable


class RegularAgent:
    """
    Agent that uses traditional LLM tool calling.

    This agent uses Anthropic's native function calling feature where:
    1. The LLM decides which tools to call
    2. Tools are called one at a time (or in parallel if supported)
    3. Results are fed back to the LLM
    4. The cycle continues until the task is complete
    """

    def __init__(self, api_key: str, tools: Dict[str, Callable], tool_schemas: List[Dict[str, Any]]):
        """
        Initialize the regular agent.

        Args:
            api_key: Anthropic API key
            tools: Dictionary of available tools (name -> function)
            tool_schemas: Tool schemas in Anthropic's format for the LLM
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.tools = tools
        self.tool_schemas = tool_schemas
        # Using Claude 3 Haiku - fast and efficient
        self.model = "claude-3-haiku-20240307"

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the agent with traditional tool calling.

        The agent will:
        1. Send the user message to the LLM with available tools
        2. Execute any tools the LLM requests
        3. Send results back to the LLM
        4. Repeat until the LLM provides a final response

        Args:
            user_message: The user's request
            max_iterations: Maximum number of tool calling iterations (default: 10)

        Returns:
            Dictionary containing:
            - success: Whether the task completed successfully
            - response: Final response text
            - tool_calls: List of tool call details
            - iterations: Number of iterations taken
            - input_tokens: Total input tokens used
            - output_tokens: Total output tokens used
            - error: Error message if something went wrong
        """
        messages = [{"role": "user", "content": user_message}]
        tool_calls = []
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Add small delay after first iteration to avoid rate limits
            if iterations > 1:
                time.sleep(0.1)

            # Call the LLM
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=self.tool_schemas,
                messages=messages
            )

            # Check if we're done
            if response.stop_reason == "end_turn":
                # Extract final text response
                final_text = ""
                for block in response.content:
                    if block.type == "text":
                        final_text += block.text

                return {
                    "success": True,
                    "response": final_text,
                    "tool_calls": tool_calls,
                    "iterations": iterations,
                    "input_tokens": sum(tc.get("input_tokens", 0) for tc in tool_calls) + response.usage.input_tokens,
                    "output_tokens": sum(tc.get("output_tokens", 0) for tc in tool_calls) + response.usage.output_tokens,
                }

            # Process tool calls
            if response.stop_reason == "tool_use":
                # Add assistant message to conversation
                messages.append({"role": "assistant", "content": response.content})

                # Execute tools and collect results
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_id = block.id

                        # Execute the tool
                        if tool_name in self.tools:
                            try:
                                result = self.tools[tool_name](**tool_input)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,
                                    "content": result
                                })

                                # Track tool call
                                tool_calls.append({
                                    "name": tool_name,
                                    "input": tool_input,
                                    "result": result,
                                    "input_tokens": response.usage.input_tokens,
                                    "output_tokens": response.usage.output_tokens,
                                })
                            except Exception as e:
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,
                                    "content": f"Error: {str(e)}",
                                    "is_error": True
                                })
                        else:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": f"Unknown tool: {tool_name}",
                                "is_error": True
                            })

                # Add tool results to conversation
                messages.append({"role": "user", "content": tool_results})

            else:
                # Unexpected stop reason
                return {
                    "success": False,
                    "error": f"Unexpected stop reason: {response.stop_reason}",
                    "tool_calls": tool_calls,
                    "iterations": iterations
                }

        return {
            "success": False,
            "error": "Max iterations reached",
            "tool_calls": tool_calls,
            "iterations": iterations
        }


def test_agent():
    """Test the regular agent."""
    import os
    from dotenv import load_dotenv
    from tools.example_tools import get_tools, get_tool_schemas

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not found in environment")
        return

    agent = RegularAgent(api_key, get_tools(), get_tool_schemas())

    # Test query
    result = agent.run("What's the weather in Tokyo and how much is 25 celsius in fahrenheit?")

    print("Regular Agent Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    test_agent()
