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
from typing import Dict, List, Any, Callable
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

    def __init__(self, api_key: str, tools: Dict[str, Callable], tools_api: str):
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
        # Using Claude 3 Haiku - fast and efficient for code generation
        self.model = "claude-3-haiku-20240307"

    def _create_system_prompt(self) -> str:
        """Create the system prompt for Code Mode."""
        return f"""You are an AI assistant that helps users by writing Python code to accomplish tasks.

You have access to the following tools through a Python API:

{self.tools_api}

STRATEGY:
When the user asks you to do something, write efficient Python code that:
1. Batches multiple tool calls together instead of making them one-by-one
2. Stores intermediate results in variables for reuse
3. Always stores the final user-facing result in a variable called 'result'
4. Uses the 'json' module to parse JSON responses from tools
5. Handles errors gracefully with try-except blocks when appropriate

IMPORTANT RULES:
- Your response should ONLY contain Python code wrapped in ```python code blocks
- Do NOT include any explanatory text outside the code block
- The code will be executed in a sandboxed environment with standard Python features
- All tool responses are JSON strings, so use json.loads() to parse them
- Take advantage of code's ability to batch operations and use loops/logic
- You can use augmented assignment operators (+=, -=, *=, etc.) and all standard builtins
- Make your code clear and well-commented for debugging
- DO NOT use type annotations (e.g., variable: Type = value). Use regular assignments instead (e.g., variable = value)
- The sandbox uses RestrictedPython which does not support type annotations

TYPE SAFETY:
The Tools API has TypedDict definitions showing exact response structures.
Pay close attention to the example return values in each function's docstring.
Key points:
- get_financial_summary() returns accounts as dict of account_name to float
  Access checking balance: json.loads(result)["accounts"]["checking"]
- create_invoice() returns nested invoice dict
  Access invoice ID: json.loads(result)["invoice"]["id"]
- get_invoices() returns list under invoices key
  Access invoices: json.loads(result)["invoices"]

EXAMPLES:

Example 1 - Simple query:
```python
import json

# Get weather data
weather_json = tools.get_weather("Tokyo", "celsius")
weather = json.loads(weather_json)

result = f"The temperature in Tokyo is {{weather['temperature']}}°C"
```

Example 2 - Batched operations (THIS IS THE POWER OF CODE MODE):
```python
import json

# Create multiple transactions efficiently in a loop
expenses = [
    ("rent", 2500, "Monthly rent"),
    ("utilities", 150, "Electricity"),
    ("internet", 100, "Internet service")
]

for category, amount, desc in expenses:
    tools.create_transaction("expense", category, amount, desc, "checking")

# Get summary once at the end
summary_json = tools.get_financial_summary()
summary = json.loads(summary_json)

result = f"Created {{len(expenses)}} expenses. Total: ${{summary['summary']['total_expenses']}}"
```
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

        while iterations < max_iterations:
            iterations += 1

            # Call the LLM
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self._create_system_prompt(),
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
            code_blocks = re.findall(r'```python\n(.*?)\n```', response_text, re.DOTALL)

            if not code_blocks:
                # No code to execute, return the response
                return {
                    "success": True,
                    "response": response_text,
                    "code_executions": code_executions,
                    "iterations": iterations,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                }

            # Execute the code
            code = code_blocks[0]  # Take the first code block
            execution_result = self.executor.execute(code)

            code_executions.append({
                "code": code,
                "execution_result": execution_result,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            })

            if not execution_result["success"]:
                # Code execution failed, ask the LLM to fix it
                error_message = f"""Code execution failed with error:
{execution_result['error']}

Please analyze the error and fix the code. Common issues:
- Make sure to parse JSON responses with json.loads()
- Check that variable names match the tool API
- Ensure all required parameters are provided
- Verify data types match expectations

Generate corrected code that will execute successfully."""
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": error_message})
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
                # No result yet, continue conversation
                result_message = f"Code executed successfully. Execution details: {json.dumps(execution_result['locals'])}\n\nPlease provide the final answer to the user."
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": result_message})

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
