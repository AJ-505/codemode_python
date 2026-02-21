import unittest
from types import SimpleNamespace

from agents.openai_compatible_codemode_agent import OpenAICompatibleCodeModeAgent


def _chat_response(text: str):
    return SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=5, completion_tokens=3),
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))],
    )


class _FakeExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, code: str):
        self.calls.append(code)
        return {"success": True, "result": "ok", "locals": {}, "tool_calls": []}


class _StubOpenAICodeModeAgent(OpenAICompatibleCodeModeAgent):
    def __init__(self, responses):
        self.tools = {}
        self.tools_api = ""
        self.executor = _FakeExecutor()
        self.model_name = "gpt-5.1"
        self.max_output_tokens = 4096
        self._token_limit_param = "max_completion_tokens"
        self._state_manager = None
        self._responses = list(responses)
        self._index = 0

    def _create_chat_completion(self, messages):
        response = self._responses[self._index]
        self._index += 1
        return response


class CodeModeResponseParsingTests(unittest.TestCase):
    def test_retries_instead_of_returning_success_when_response_has_no_code(self):
        agent = _StubOpenAICodeModeAgent(
            [
                _chat_response("I can help with that."),
                _chat_response("```python\nresult = 'ok'\n```"),
            ]
        )

        result = agent.run("Do the task", max_iterations=3)

        self.assertTrue(result["success"])
        self.assertEqual(result["iterations"], 2)
        self.assertEqual(len(result["code_executions"]), 1)
        self.assertEqual(result["response"], "ok")

    def test_accepts_plain_code_without_fence(self):
        agent = _StubOpenAICodeModeAgent(
            [
                _chat_response("import json\nresult = 'ok'"),
            ]
        )

        result = agent.run("Do the task", max_iterations=2)

        self.assertTrue(result["success"])
        self.assertEqual(result["iterations"], 1)
        self.assertEqual(len(result["code_executions"]), 1)
        self.assertEqual(result["response"], "ok")


if __name__ == "__main__":
    unittest.main()
