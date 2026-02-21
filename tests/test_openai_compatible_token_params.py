import unittest
from types import SimpleNamespace

from agents.openai_compatible_codemode_agent import OpenAICompatibleCodeModeAgent
from agents.openai_compatible_regular_agent import OpenAICompatibleRegularAgent


def _response(content: str):
    return SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1),
        choices=[SimpleNamespace(message=SimpleNamespace(content=content, tool_calls=[]))],
    )


class _FakeCompletions:
    def __init__(self, unsupported_param=None, response_content="ok"):
        self.unsupported_param = unsupported_param
        self.response_content = response_content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.unsupported_param and self.unsupported_param in kwargs:
            raise Exception(
                "Error code: 400 - {'error': {'message': "
                f"\"Unsupported parameter: '{self.unsupported_param}' is not supported with this model. "
                "Use 'max_completion_tokens' instead.\", "
                "'type': 'invalid_request_error', "
                f"'param': '{self.unsupported_param}', "
                "'code': 'unsupported_parameter'}}"
            )
        return _response(self.response_content)


class _FakeClient:
    def __init__(self, completions):
        self.chat = SimpleNamespace(completions=completions)


class OpenAICompatibleTokenParamTests(unittest.TestCase):
    def test_regular_agent_falls_back_to_max_completion_tokens(self):
        completions = _FakeCompletions(unsupported_param="max_tokens", response_content="done")
        agent = OpenAICompatibleRegularAgent(
            api_key="test-key",
            tools={},
            tool_schemas=[],
            model_name="glm-5",
        )
        agent.client = _FakeClient(completions)

        result = agent.run("hello")

        self.assertTrue(result["success"])
        self.assertEqual(result["response"], "done")
        self.assertEqual(len(completions.calls), 2)
        self.assertIn("max_tokens", completions.calls[0])
        self.assertIn("max_completion_tokens", completions.calls[1])

    def test_codemode_agent_prefers_max_completion_tokens_for_gpt5(self):
        completions = _FakeCompletions(response_content="```python\nresult = 'ok'\n```")
        agent = OpenAICompatibleCodeModeAgent(
            api_key="test-key",
            tools={},
            tools_api="",
            model_name="gpt-5.2",
        )
        agent.client = _FakeClient(completions)

        result = agent.run("hello")

        self.assertTrue(result["success"])
        self.assertEqual(result["response"], "ok")
        self.assertEqual(len(completions.calls), 1)
        self.assertIn("max_completion_tokens", completions.calls[0])
        self.assertNotIn("max_tokens", completions.calls[0])


if __name__ == "__main__":
    unittest.main()
