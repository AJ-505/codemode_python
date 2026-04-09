import unittest

from sandbox.executor import CodeExecutor
from tools.accounting_tools import create_transaction, state
from tools.business_tools import get_code_mode_api, get_code_mode_api_compact
from tools import get_tools


class CodeModeEfficiencyPrimitivesTests(unittest.TestCase):
    def setUp(self):
        state.reset()

    def tearDown(self):
        state.reset()

    def test_state_snapshot_restore_reverts_mutations(self):
        baseline = state.snapshot()
        create_transaction("expense", "rent", 2500, "Office rent", "checking")
        self.assertEqual(state.get_summary()["total_transactions"], 1)

        state.restore(baseline)
        summary = state.get_summary()
        self.assertEqual(summary["total_transactions"], 0)
        self.assertEqual(summary["accounts"]["checking"]["balance"], 10000.0)

    def test_compact_code_mode_api_is_smaller_and_keeps_core_tools(self):
        full_api = get_code_mode_api()
        compact_api = get_code_mode_api_compact()

        self.assertLess(len(compact_api), len(full_api))
        for tool_name in [
            "create_transaction",
            "create_invoice",
            "record_partial_payment",
            "get_financial_summary",
            "get_state_summary",
        ]:
            self.assertIn(tool_name, compact_api)
        self.assertNotIn("def create_customer", compact_api)
        self.assertIn("def discover", compact_api)

    def test_compact_api_documents_runtime_tools_instance_and_price_key(self):
        compact_api = get_code_mode_api_compact()
        self.assertIn("pre-initialized `tools` object", compact_api)
        self.assertIn("Do not call `Tools()`", compact_api)
        self.assertIn("Use key `price` exactly", compact_api)

    def test_sandbox_supports_dict_item_assignment_via_write_guard(self):
        executor = CodeExecutor(get_tools())
        execution = executor.execute('d = {"a": 1}\nd["a"] = 2\nresult = d["a"]')
        self.assertTrue(execution["success"], msg=execution.get("error"))
        self.assertEqual(execution["result"], 2)

    def test_lazy_direct_tool_requires_discovery(self):
        executor = CodeExecutor(get_tools())
        execution = executor.execute(
            'result = tools.create_customer("Acme", "ops@acme.test")'
        )
        self.assertFalse(execution["success"])
        self.assertIn("not discovered yet", execution.get("error", ""))

    def test_discover_unlocks_lazy_direct_tool(self):
        executor = CodeExecutor(get_tools())
        execution = executor.execute(
            'import json\n'
            'meta = json.loads(tools.discover("/crm/create_customer"))\n'
            'created = json.loads(tools.create_customer("Acme", "ops@acme.test"))\n'
            'result = {"discovered": meta["discovered_tools"], "customer_id": created["customer"]["id"]}'
        )
        self.assertTrue(execution["success"], msg=execution.get("error"))
        self.assertIn("create_customer", execution["result"]["discovered"])


if __name__ == "__main__":
    unittest.main()
