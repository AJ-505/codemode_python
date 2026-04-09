import unittest

from tools import get_tool_fs_manifest


class ToolFsManifestTests(unittest.TestCase):
    def test_manifest_has_expected_paths(self):
        manifest = get_tool_fs_manifest()
        self.assertIn("/accounting/create_invoice", manifest)
        self.assertIn("/system/simulate_transient_failure", manifest)
        self.assertEqual(manifest["/crm/create_customer"]["name"], "create_customer")
        self.assertFalse(manifest["/accounting/create_invoice"]["lazy"])
        self.assertTrue(manifest["/crm/create_customer"]["lazy"])


if __name__ == "__main__":
    unittest.main()
