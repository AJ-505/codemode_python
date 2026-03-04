import os
import unittest

from agents.agent_factory import AgentFactory


class AgentFactoryRoutingTests(unittest.TestCase):
    def setUp(self):
        self._env_backup = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self._env_backup)

    def test_glm_uses_openrouter_by_default(self):
        os.environ["OPENROUTER_API_KEY"] = "or-key"
        cfg = AgentFactory.resolve_runtime_config("glm_5")
        self.assertEqual(cfg["api_key_env"], "OPENROUTER_API_KEY")
        self.assertEqual(cfg["provider_path"], "openrouter_or_native")
        self.assertEqual(cfg["model_name"], "z-ai/glm-5")

    def test_glm_prefers_direct_provider_when_direct_key_exists(self):
        os.environ["OPENROUTER_API_KEY"] = "or-key"
        os.environ["ZHIPU_API_KEY"] = "zhipu-key"
        cfg = AgentFactory.resolve_runtime_config("glm_5")
        self.assertEqual(cfg["api_key_env"], "ZHIPU_API_KEY")
        self.assertEqual(cfg["provider_path"], "direct")
        self.assertEqual(cfg["model_name"], "glm-5")

    def test_latest_models_excludes_opus_by_default(self):
        latest = AgentFactory.get_latest_models()
        self.assertNotIn("opus_4_6", latest)
        with_opus = AgentFactory.get_latest_models(include_opus=True)
        self.assertEqual(with_opus[0], "opus_4_6")


if __name__ == "__main__":
    unittest.main()
