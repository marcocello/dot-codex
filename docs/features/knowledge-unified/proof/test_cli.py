"""Public subprocess proof; isolated temporary profile state and no provider calls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[4]
CANONICAL = ROOT / "skills/knowledge-connect/scripts/knowledge_profile.py"
LEGACY = ROOT / "skills/knowledge-config/scripts/knowledge_profile.py"
SHARED = ROOT / "scripts/knowledge_profile.py"


class UnifiedProfiles(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = Path(self.temp.name) / "knowledge.toml"

    def cli(self, *args, path=CANONICAL, code=0):
        result = subprocess.run([sys.executable, str(path), "--config", str(self.config), *args],
                                text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, code, result.stderr)
        return json.loads(result.stdout if code == 0 else result.stderr)

    def create(self, path=CANONICAL, default=True):
        return self.cli("put", "work", "--provider", "clickup", "--connection", "clickup-main",
                        "--account", "123", "--workspace-id", "456", "--destination", "transcripts",
                        *( ["--default"] if default else []), path=path)

    def setup(self, *args, path=CANONICAL):
        result = self.cli(*args, path=path, code=3)
        self.assertEqual(result["code"], "SETUP_REQUIRED")
        self.assertEqual(result["skill"], "knowledge-connect")
        self.assertIn("knowledge-connect", result["message"])
        self.assertNotIn("knowledge-config", result["message"])

    def test_missing_configuration_routes_every_entrypoint_to_unified_skill(self):
        for path in (CANONICAL, LEGACY, SHARED):
            with self.subTest(path=path):
                self.setup("resolve", path=path)
        self.assertFalse(self.config.exists())

    def test_creation_readback_and_restart_through_all_entrypoints(self):
        created = self.create(path=LEGACY)
        self.assertEqual(created["provider"], "clickup")
        self.assertNotIn("tasks", created)
        for path in (CANONICAL, LEGACY, SHARED):
            with self.subTest(path=path):
                self.assertEqual(self.cli("resolve", path=path), created)
                self.assertEqual(self.cli("list", path=path)["default_profile"], "work")
        persisted = tomllib.loads(self.config.read_text())
        self.assertEqual(persisted["version"], 1)
        self.assertEqual(persisted["profiles"]["work"]["workspace_id"], "456")

    def test_missing_default_and_missing_api_credentials_route_setup(self):
        self.create(default=False)
        self.setup("resolve")
        self.setup("resolve", "--profile", "work", "--transport", "api")
        self.assertIsNone(self.cli("list")["default_profile"])

    def test_credential_binding_and_temporary_transport_preserve_identity_and_default(self):
        initial = self.create()
        attached = self.cli("credentials", "work", "--token-env", "UNIFIED_PROOF_TOKEN", path=SHARED)
        for key in ("account", "workspace_id", "destination", "connection"):
            self.assertEqual(attached[key], initial[key])
        before = self.config.read_bytes()
        temporary = self.cli("resolve", "--transport", "api")
        self.assertEqual(temporary["transport"], "api")
        self.assertEqual(temporary["token_env"], "UNIFIED_PROOF_TOKEN")
        self.assertEqual(self.config.read_bytes(), before)
        self.assertEqual(self.cli("resolve").get("transport", "mcp"), "mcp")
        self.cli("transport", "work", "api", path=LEGACY)
        self.assertEqual(self.cli("resolve", path=SHARED)["transport"], "api")
        private_path = str(Path(self.temp.name) / "private-token")
        replaced = self.cli("credentials", "work", "--token-file", private_path)
        self.assertNotIn("token_env", replaced)
        self.assertEqual(self.cli("resolve", path=LEGACY)["token_file"], private_path)
        saved = tomllib.loads(self.config.read_text())
        self.assertEqual(saved["default_profile"], "work")
        self.assertEqual(saved["profiles"]["work"]["token_file"], private_path)

    def test_none_and_markdown_remain_usable(self):
        self.cli("put", "off", "--provider", "none", "--default")
        self.assertEqual(self.cli("resolve", path=LEGACY), {"profile": "off", "provider": "none"})
        root = str(Path(self.temp.name) / "notes")
        self.cli("put", "local", "--provider", "markdown", "--root", root, path=SHARED)
        self.assertEqual(self.cli("resolve", "--profile", "local")["root"], root)
        self.assertEqual(self.cli("resolve")["profile"], "off")


if __name__ == "__main__":
    unittest.main(verbosity=2)
