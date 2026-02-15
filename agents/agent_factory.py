"""
Agent factory for creating agents with different models and providers.
"""

import importlib
from typing import Dict, List, Any, Callable, Optional


class AgentFactory:
    """Factory for creating agents with different models and modes."""

    SUPPORTED_MODELS = {
        "claude": {
            "name": "Claude Haiku (Anthropic)",
            "api_key_env": "ANTHROPIC_API_KEY",
            "regular_class": "agents.regular_agent.RegularAgent",
            "codemode_class": "agents.codemode_agent.CodeModeAgent",
            "model_name": "claude-3-haiku-20240307",
        },
        "gemini": {
            "name": "Gemini Flash (Google)",
            "api_key_env": "GOOGLE_API_KEY",
            "regular_class": "agents.gemini_regular_agent.GeminiRegularAgent",
            "codemode_class": "agents.gemini_codemode_agent.GeminiCodeModeAgent",
            "model_name": "gemini-2.0-flash-exp",
        },
        "opus_4_6": {
            "name": "Claude Opus 4.6 (Anthropic)",
            "api_key_env": "ANTHROPIC_API_KEY",
            "regular_class": "agents.regular_agent.RegularAgent",
            "codemode_class": "agents.codemode_agent.CodeModeAgent",
            "model_name": "claude-opus-4-6",
        },
        "gpt_5_2": {
            "name": "GPT-5.2 (OpenAI)",
            "api_key_env": "OPENAI_API_KEY",
            "regular_class": "agents.openai_compatible_regular_agent.OpenAICompatibleRegularAgent",
            "codemode_class": "agents.openai_compatible_codemode_agent.OpenAICompatibleCodeModeAgent",
            "model_name": "gpt-5.2",
        },
        "glm_5": {
            "name": "GLM-5 (ZhipuAI OpenAI-compatible)",
            "api_key_env": "ZHIPU_API_KEY",
            "regular_class": "agents.openai_compatible_regular_agent.OpenAICompatibleRegularAgent",
            "codemode_class": "agents.openai_compatible_codemode_agent.OpenAICompatibleCodeModeAgent",
            "model_name": "glm-5",
            "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        },
        "gemini_3_pro": {
            "name": "Gemini 3 Pro (Google OpenAI-compatible)",
            "api_key_env": "GOOGLE_API_KEY",
            "regular_class": "agents.openai_compatible_regular_agent.OpenAICompatibleRegularAgent",
            "codemode_class": "agents.openai_compatible_codemode_agent.OpenAICompatibleCodeModeAgent",
            "model_name": "gemini-3-pro-preview",
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        },
    }

    LATEST_MODEL_KEYS = ["opus_4_6", "gpt_5_2", "glm_5", "gemini_3_pro"]

    @classmethod
    def create_agent(
        cls,
        model: str,
        mode: str,
        api_key: str,
        tools: Dict[str, Callable],
        tool_schemas: Optional[List[Dict[str, Any]]] = None,
        tools_api: Optional[str] = None,
        model_name_override: Optional[str] = None,
    ):
        """
        Create an agent with the specified model and mode.

        Args:
            model: Model key (see SUPPORTED_MODELS)
            mode: Agent mode ("regular" or "codemode")
            api_key: API key for the model/provider
            tools: Dictionary of available tools
            tool_schemas: Tool schemas (for regular mode)
            tools_api: Tools API definition (for code mode)
            model_name_override: Optional direct model ID override
        """
        if model not in cls.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models: {', '.join(cls.SUPPORTED_MODELS.keys())}"
            )

        if mode not in ["regular", "codemode"]:
            raise ValueError(f"Unsupported mode: {mode}. Supported modes: regular, codemode")

        model_config = cls.SUPPORTED_MODELS[model]
        class_path_key = f"{mode}_class"
        agent_class = cls._resolve_class(model_config[class_path_key])

        init_kwargs: Dict[str, Any] = {
            "api_key": api_key,
            "tools": tools,
            "model_name": model_name_override or model_config.get("model_name"),
            "base_url": model_config.get("base_url"),
        }

        if mode == "regular":
            if tool_schemas is None:
                raise ValueError("tool_schemas is required for regular mode")
            init_kwargs["tool_schemas"] = tool_schemas
        else:
            if tools_api is None:
                raise ValueError("tools_api is required for codemode mode")
            init_kwargs["tools_api"] = tools_api

        try:
            return agent_class(**init_kwargs)
        except TypeError:
            # Backward-compatible fallback for agents that do not accept base_url.
            init_kwargs.pop("base_url", None)
            return agent_class(**init_kwargs)

    @classmethod
    def get_supported_models(cls) -> List[str]:
        """Get list of supported model keys."""
        return list(cls.SUPPORTED_MODELS.keys())

    @classmethod
    def get_latest_models(cls) -> List[str]:
        """Get latest research model keys requested for this benchmark."""
        return list(cls.LATEST_MODEL_KEYS)

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

    @staticmethod
    def _resolve_class(class_path: str):
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
