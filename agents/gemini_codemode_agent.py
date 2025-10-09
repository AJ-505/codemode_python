"""
Code Mode agent using Gemini - LLM writes code to call tools.
"""

import google.generativeai as genai
import json
import re
from typing import Dict, List, Any, Callable
from sandbox.executor import CodeExecutor


class GeminiCodeModeAgent:
    """Agent that uses Gemini to generate and execute code to call tools."""

    def __init__(self, api_key: str, tools: Dict[str, Callable], tools_api: str):
        """
        Initialize the Gemini Code Mode agent.

        Args:
            api_key: Google API key
            tools: Dictionary of available tools
            tools_api: Python API definition string for code generation
        """
        genai.configure(api_key=api_key)
        self.tools = tools
        self.tools_api = tools_api
        self.executor = CodeExecutor(tools)
        self.model_name = "gemini-2.0-flash-exp"
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self._create_system_prompt()
        )

    def _create_system_prompt(self) -> str:
        """Create the system prompt for Code Mode."""
        return f"""You are an AI assistant that helps users by writing Python code to accomplish tasks.

You have access to the following tools through a Python API:

{self.tools_api}

When the user asks you to do something, you should:
1. Write Python code that uses the tools API to accomplish the task
2. Always store the final result in a variable called 'result'
3. Use the 'json' module to parse JSON responses from tools
4. Handle errors appropriately

IMPORTANT:
- Your response should ONLY contain Python code wrapped in ```python code blocks
- Do NOT include any explanatory text outside the code block
- The code will be executed in a sandboxed environment
- All tool responses are JSON strings, so use json.loads() to parse them
- DO NOT use type annotations (e.g., variable: Type = value). Use regular assignments instead (e.g., variable = value)
- The sandbox uses RestrictedPython which does not support type annotations

Example:
```python
import json

# Get account balance
balance_json = tools.get_account_balance("checking")
balance = json.loads(balance_json)

# Use the data
result = f"The checking account balance is ${{balance['balance']}}"
```
"""

    def run(self, user_message: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the agent with Code Mode.

        Args:
            user_message: The user's request
            max_iterations: Maximum number of iterations

        Returns:
            Dictionary with response, code executions, and metrics
        """
        chat = self.model.start_chat()
        code_executions = []
        iterations = 0
        total_input_tokens = 0
        total_output_tokens = 0

        try:
            while iterations < max_iterations:
                iterations += 1

                # Call the LLM
                response = chat.send_message(user_message)

                # Count tokens (approximate)
                if hasattr(response, 'usage_metadata'):
                    total_input_tokens += response.usage_metadata.prompt_token_count
                    total_output_tokens += response.usage_metadata.candidates_token_count

                # Extract the response text
                response_text = ""
                if response.candidates:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text

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
                })

                if not execution_result["success"]:
                    # Code execution failed, ask the LLM to fix it
                    user_message = f"Code execution failed with error: {execution_result['error']}\n\nPlease fix the code and try again."
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
                    user_message = f"Code executed successfully. Execution details: {json.dumps(execution_result['locals'])}\n\nPlease provide the final answer to the user."

            return {
                "success": False,
                "error": "Max iterations reached",
                "code_executions": code_executions,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code_executions": code_executions,
                "iterations": iterations,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
            }


def test_agent():
    """Test the Gemini Code Mode agent."""
    import os
    from dotenv import load_dotenv
    from tools.business_tools import get_tools, get_code_mode_api, get_state

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment")
        return

    # Reset state
    state = get_state()
    state.reset()

    agent = GeminiCodeModeAgent(api_key, get_tools(), get_code_mode_api())

    # Test query
    result = agent.run("Record a $2500 rent expense and a $5000 consulting income. Then show me the checking account balance.")

    print("Gemini Code Mode Agent Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    test_agent()
