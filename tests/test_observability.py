import json
import unittest

from observability import build_codemode_observability


class ObservabilityTests(unittest.TestCase):
    def test_builds_tool_level_expected_actual_discrepancies(self):
        scenario = {
            "id": 1,
            "name": "Demo",
            "expected_state": {"min_transactions": 1},
            "expected_tool_flow": [{"tool": "create_transaction", "min_calls": 1}],
        }
        result = {
            "code_executions": [
                {
                    "execution_result": {
                        "success": True,
                        "tool_calls": [
                            {
                                "tool": "create_transaction",
                                "kwargs_structured": {
                                    "transaction_type": "expense",
                                    "category": "rent",
                                    "amount": 100,
                                    "account": "checking",
                                },
                                "state_delta": {"total_transactions": 1.0},
                                "success": True,
                                "result_structured": json.dumps(
                                    {
                                        "status": "success",
                                        "transaction": {
                                            "type": "expense",
                                            "category": "rent",
                                            "amount": 100,
                                            "account": "checking",
                                        },
                                    }
                                ),
                            }
                        ],
                    }
                }
            ]
        }

        obs = build_codemode_observability(scenario=scenario, result=result)
        self.assertEqual(obs["iteration_failures"], 0)
        self.assertEqual(obs["tool_discrepancy_count"], 0)
        self.assertEqual(len(obs["tool_trace"]), 1)
        self.assertTrue(obs["tool_trace"][0]["ok"])

    def test_detects_missing_expected_tool(self):
        scenario = {
            "id": 1,
            "name": "Demo",
            "expected_state": {},
            "expected_tool_flow": [{"tool": "create_invoice", "min_calls": 1}],
        }
        result = {"code_executions": [{"execution_result": {"success": True, "tool_calls": []}}]}
        obs = build_codemode_observability(scenario=scenario, result=result)
        self.assertEqual(len(obs["flow_discrepancies"]["missing_tools"]), 1)

    def test_reads_positional_args_from_codemode_trace(self):
        scenario = {
            "id": 6,
            "name": "Demo",
            "expected_state": {},
            "expected_tool_flow": [{"tool": "create_transaction", "min_calls": 1}],
        }
        result = {
            "code_executions": [
                {
                    "execution_result": {
                        "success": True,
                        "tool_calls": [
                            {
                                "tool": "create_transaction",
                                "args_structured": [
                                    "income",
                                    "consulting",
                                    12000,
                                    "Month 1 consulting income",
                                ],
                                "kwargs_structured": {},
                                "state_delta": {"total_transactions": 1.0},
                                "success": True,
                                "result_structured": json.dumps(
                                    {
                                        "status": "success",
                                        "transaction": {
                                            "type": "income",
                                            "category": "consulting",
                                            "amount": 12000,
                                            "account": "checking",
                                        },
                                    }
                                ),
                            }
                        ],
                    }
                }
            ]
        }

        obs = build_codemode_observability(scenario=scenario, result=result)
        self.assertEqual(obs["tool_discrepancy_count"], 0)
        self.assertTrue(obs["tool_trace"][0]["ok"])


if __name__ == "__main__":
    unittest.main()
