"""
Agent factory for creating agents with different models.
"""

from typing import Dict, List, Any, Callable
from .regular_agent import RegularAgent
from .codemode_agent import CodeModeAgent
from .gemini_regular_agent import GeminiRegularAgent
from .gemini_codemode_agent import GeminiCodeModeAgent


class AgentFactory:
    """Factory for creating agents with different models and modes."""

    SUPPORTED_MODELS = {
        "claude": {
            "name": "Claude (Anthropic)",
            "api_key_env": "ANTHROPIC_API_KEY",
            "regular": RegularAgent,
            "codemode": CodeModeAgent,
        },
        "gemini": {
            "name": "Gemini (Google)",
            "api_key_env": "GOOGLE_API_KEY",
            "regular": GeminiRegularAgent,
            "codemode": GeminiCodeModeAgent,
        }
    }

    @classmethod
    def create_agent(
        cls,
        model: str,
        mode: str,
        api_key: str,
        tools: Dict[str, Callable],
        tool_schemas: List[Dict[str, Any]] = None,
        tools_api: str = None
    ):
        """
        Create an agent with the specified model and mode.

        Args:
            model: Model name ("claude" or "gemini")
            mode: Agent mode ("regular" or "codemode")
            api_key: API key for the model
            tools: Dictionary of available tools
            tool_schemas: Tool schemas (for regular mode)
            tools_api: Tools API definition (for code mode)

        Returns:
            Agent instance

        Raises:
            ValueError: If model or mode is not supported
        """
        if model not in cls.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {', '.join(cls.SUPPORTED_MODELS.keys())}"
            )

        if mode not in ["regular", "codemode"]:
            raise ValueError(f"Unsupported mode: {mode}. Supported modes: regular, codemode")

        agent_class = cls.SUPPORTED_MODELS[model][mode]

        if mode == "regular":
            if tool_schemas is None:
                raise ValueError("tool_schemas is required for regular mode")
            return agent_class(api_key, tools, tool_schemas)
        else:  # codemode
            if tools_api is None:
                raise ValueError("tools_api is required for codemode mode")
            return agent_class(api_key, tools, tools_api)

    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get list of supported model names."""
        return list(cls.SUPPORTED_MODELS.keys())

    @classmethod
    def get_model_info(cls, model: str) -> Dict[str, Any]:
        """Get information about a model."""
        if model not in cls.SUPPORTED_MODELS:
            raise ValueError(f"Unknown model: {model}")
        return cls.SUPPORTED_MODELS[model]

    @classmethod
    def get_required_api_key_env(cls, model: str) -> str:
        """Get the required environment variable name for a model's API key."""
        if model not in cls.SUPPORTED_MODELS:
            raise ValueError(f"Unknown model: {model}")
        return cls.SUPPORTED_MODELS[model]["api_key_env"]


def test_factory():
    """Test the agent factory."""
    import os
    from dotenv import load_dotenv
    from tools.business_tools import get_tools, get_tool_schemas, get_code_mode_api, get_state

    load_dotenv()

    # Test with both models if keys are available
    models_to_test = []

    claude_key = os.getenv("ANTHROPIC_API_KEY")
    if claude_key:
        models_to_test.append(("claude", claude_key))

    gemini_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        models_to_test.append(("gemini", gemini_key))

    if not models_to_test:
        print("Error: No API keys found. Set ANTHROPIC_API_KEY and/or GOOGLE_API_KEY")
        return

    tools = get_tools()
    tool_schemas = get_tool_schemas()
    tools_api = get_code_mode_api()
    state = get_state()

    test_query = "Record a $1000 expense for rent and show me the checking balance."

    for model_name, api_key in models_to_test:
        print(f"\n{'=' * 60}")
        print(f"Testing {model_name.upper()}")
        print(f"{'=' * 60}\n")

        # Test regular mode
        print(f"Testing {model_name} - Regular Mode:")
        state.reset()
        try:
            agent = AgentFactory.create_agent(
                model=model_name,
                mode="regular",
                api_key=api_key,
                tools=tools,
                tool_schemas=tool_schemas
            )
            result = agent.run(test_query)
            print(f"  Success: {result['success']}")
            print(f"  Iterations: {result.get('iterations', 'N/A')}")
            print(f"  Response preview: {result.get('response', '')[:100]}...")
        except Exception as e:
            print(f"  Error: {e}")

        print()

        # Test code mode
        print(f"Testing {model_name} - Code Mode:")
        state.reset()
        try:
            agent = AgentFactory.create_agent(
                model=model_name,
                mode="codemode",
                api_key=api_key,
                tools=tools,
                tools_api=tools_api
            )
            result = agent.run(test_query)
            print(f"  Success: {result['success']}")
            print(f"  Iterations: {result.get('iterations', 'N/A')}")
            print(f"  Response preview: {result.get('response', '')[:100]}...")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n{'=' * 60}")
    print("Supported models:", ", ".join(AgentFactory.get_supported_models()))


if __name__ == "__main__":
    test_factory()
