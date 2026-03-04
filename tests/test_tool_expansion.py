import unittest

from tools.business_tools import get_tools


class ToolExpansionTests(unittest.TestCase):
    def test_tool_count_is_twenty_two(self):
        tools = get_tools()
        self.assertEqual(len(tools), 22)

    def test_failure_injection_tool_exists(self):
        tools = get_tools()
        self.assertIn("simulate_transient_failure", tools)


if __name__ == "__main__":
    unittest.main()
