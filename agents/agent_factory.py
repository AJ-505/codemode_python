"""
Agent factory for creating agents with different models and providers.
"""

import importlib
import os
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
         "gpt_5_1": {
            "name": "GPT-5.1 (OpenAI)",
            "api_key_env": "OPENAI_API_KEY",
            "regular_class": "agents.openai_compatible_regular_agent.OpenAICompatibleRegularAgent",
            "codemode_class": "agents.openai_compatible_codemode_agent.OpenAICompatibleCodeModeAgent",
            "model_name": "gpt-5.1",
        },
        "glm_5": {
            "name": "GLM-5 (OpenRouter default, Zhipu direct optional)",
            "api_key_env": "OPENROUTER_API_KEY",
            "regular_class": "agents.openai_compatible_regular_agent.OpenAICompatibleRegularAgent",
            "codemode_class": "agents.openai_compatible_codemode_agent.OpenAICompatibleCodeModeAgent",
            "model_name": "z-ai/glm-5",
            "base_url": "https://openrouter.ai/api/v1",
            "direct_api_key_env": "ZHIPU_API_KEY",
            "direct_model_name": "glm-5",
            "direct_base_url": "https://open.bigmodel.cn/api/paas/v4/",
        },
        "minimax_m2_5": {
            "name": "MiniMax M2.5 (OpenRouter default, direct optional)",
            "api_key_env": "OPENROUTER_API_KEY",
            "regular_class": "agents.openai_compatible_regular_agent.OpenAICompatibleRegularAgent",
            "codemode_class": "agents.openai_compatible_codemode_agent.OpenAICompatibleCodeModeAgent",
            "model_name": "minimax/minimax-m2.5",
            "base_url": "https://openrouter.ai/api/v1",
            "direct_api_key_env": "MINIMAX_API_KEY",
            "direct_model_name": "MiniMax-M2.5",
            "direct_base_url": "https://api.minimax.io/v1",
        },
        "kimi_2_5": {
            "name": "Kimi 2.5 (OpenRouter default, direct optional)",
            "api_key_env": "OPENROUTER_API_KEY",
            "regular_class": "agents.openai_compatible_regular_agent.OpenAICompatibleRegularAgent",
            "codemode_class": "agents.openai_compatible_codemode_agent.OpenAICompatibleCodeModeAgent",
            "model_name": "moonshotai/kimi-k2",
            "base_url": "https://openrouter.ai/api/v1",
            "direct_api_key_env": "MOONSHOT_API_KEY",
            "direct_model_name": "kimi-k2-latest",
            "direct_base_url": "https://api.moonshot.ai/v1",
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

    LATEST_MODEL_KEYS = ["gpt_5_1", "gpt_5_2", "glm_5", "minimax_m2_5", "kimi_2_5", "gemini_3_pro"]

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
        base_url_override: Optional[str] = None,
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
            "base_url": base_url_override or model_config.get("base_url"),
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
    def get_latest_models(cls, include_opus: bool = False) -> List[str]:
        """Get latest research model keys requested for this benchmark."""
        keys = list(cls.LATEST_MODEL_KEYS)
        if include_opus:
            return ["opus_4_6", *keys]
        return keys

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

    @classmethod
    def get_all_known_api_key_envs(cls) -> List[str]:
        envs = set()
        for config in cls.SUPPORTED_MODELS.values():
            if config.get("api_key_env"):
                envs.add(config["api_key_env"])
            if config.get("direct_api_key_env"):
                envs.add(config["direct_api_key_env"])
        return sorted(envs)

    @classmethod
    def resolve_runtime_config(
        cls,
        model: str,
        api_keys: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Resolve runtime key/model/base_url with direct-provider override when available."""
        if model not in cls.SUPPORTED_MODELS:
            raise ValueError(f"Unknown model: {model}")

        config = cls.SUPPORTED_MODELS[model]
        provided = api_keys or {}

        default_env = config.get("api_key_env")
        default_key = provided.get(default_env) or os.getenv(default_env or "")
        direct_env = config.get("direct_api_key_env")
        direct_key = provided.get(direct_env) or os.getenv(direct_env or "")

        if direct_env and direct_key:
            return {
                "api_key": direct_key,
                "api_key_env": direct_env,
                "model_name": config.get("direct_model_name", config.get("model_name")),
                "base_url": config.get("direct_base_url", config.get("base_url")),
                "provider_path": "direct",
                "required_envs": [direct_env, default_env] if default_env else [direct_env],
            }

        return {
            "api_key": default_key,
            "api_key_env": default_env,
            "model_name": config.get("model_name"),
            "base_url": config.get("base_url"),
            "provider_path": "openrouter_or_native",
            "required_envs": [env for env in [default_env, direct_env] if env],
        }

    @staticmethod
    def _resolve_class(class_path: str):
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
