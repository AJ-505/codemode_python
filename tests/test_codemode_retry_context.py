import unittest

from agents.openai_compatible_codemode_agent import OpenAICompatibleCodeModeAgent


class RetryContextTests(unittest.TestCase):
    def test_reset_retry_context_keeps_only_three_messages(self):
        messages = OpenAICompatibleCodeModeAgent._reset_retry_context(
            "do the task",
            "```python\nresult = 'x'\n```",
            "fix it",
        )

        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[0]["content"], "do the task")
        self.assertEqual(messages[1]["role"], "assistant")
        self.assertEqual(messages[2]["role"], "user")

    def test_reset_retry_context_preserves_original_task(self):
        prompt = "record the expenses and summarize balances"
        messages = OpenAICompatibleCodeModeAgent._reset_retry_context(
            prompt,
            "```python\npass\n```",
            "return one corrected block",
        )

        self.assertEqual(messages[0]["content"], prompt)


if __name__ == "__main__":
    unittest.main()
