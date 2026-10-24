"""Exercise the public installer in isolated user homes and check its consumers."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[4]


class InstallJourneys(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dot-codex install ")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.home = self.base / "user"
        self.home.mkdir()
        self.repo = self.base / "checkout with spaces"
        self.repo.mkdir()
        for name in ("install.sh", "config.template.toml", ".gitignore"):
            shutil.copy2(ROOT / name, self.repo / name)
        (self.repo / "scripts").mkdir()
        for name in ("install.py", "skill_inventory.py"):
            shutil.copy2(ROOT / "scripts" / name, self.repo / "scripts" / name)
        shutil.copytree(ROOT / "integrations", self.repo / "integrations")
        (self.repo / "skills.toml").write_text(
            'schema = 1\n\n[[skills]]\nname = "dot-codex-tools"\n'
            'kind = "plugin"\nselector = "dot-codex-tools@dot-codex"\nenabled = true\n'
        )
        (self.repo / "AGENTS.md").write_text("checkout instructions\n")
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(
            ["git", "add", "AGENTS.md", ".gitignore", "config.template.toml", "skills.toml"],
            cwd=self.repo, check=True,
        )
        self.initial_staged = subprocess.check_output(
            ["git", "diff", "--cached", "--binary"], cwd=self.repo,
        )
        self.env = dict(os.environ, HOME=str(self.home), SHELL="/bin/zsh")
        self.env.pop("CODEX_HOME", None)

    def install(self, answer="", *args, deps=False):
        command = ["bash", str(self.repo / "install.sh"), "--user-home", str(self.home)]
        if not deps:
            command += ["--skip-dependencies"]
        return subprocess.run(command + list(args), input=answer, text=True,
                              capture_output=True, env=self.env, cwd=self.repo)

    def good(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fresh_install_and_idempotent_rerun(self):
        (self.home / ".zshrc").write_text('export CODEX_HOME=/old/home\n')
        self.good(self.install())
        self.assertEqual((self.home / ".codex").resolve(), self.repo)
        config = self.repo / "config.toml"
        parsed = tomllib.loads(config.read_text())
        self.assertNotIn("mcp_servers", parsed)
        self.assertNotIn("notify", parsed)
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        config.write_text(config.read_text() + '\n# preserve local preference\n')
        before = config.read_bytes()
        self.good(self.install())
        self.assertEqual(config.read_bytes(), before)
        for name in (".profile", ".zshenv", ".bashrc"):
            self.assertEqual((self.home / name).read_text().count("# BEGIN dot-codex"), 1)
        read = subprocess.run(
            ["/bin/sh", "-c", '. "$HOME/.profile"; printf "%s" "$CODEX_HOME"'],
            env=self.env, text=True, capture_output=True, check=True,
        )
        self.assertEqual(read.stdout, str(self.repo))
        read = subprocess.run(
            ["/bin/sh", "-c", '. "$HOME/.zshenv"; . "$HOME/.zshrc"; printf "%s" "$CODEX_HOME"'],
            env=self.env, text=True, capture_output=True, check=True,
        )
        self.assertEqual(read.stdout, str(self.repo))

    def test_merge_preserves_conflicts_and_ignores_private_markdown(self):
        old = self.home / ".codex"
        (old / "skills" / "personal").mkdir(parents=True)
        (old / "skills/personal/SKILL.md").write_text("private skill")
        (old / "AGENTS.md").write_text("old instructions")
        (old / "config.toml").write_text('model = "personal"\n')
        (old / "history.jsonl").write_text('{"private": true}\n')
        self.good(self.install("merge\n"))
        self.assertEqual((self.repo / "skills/personal/SKILL.md").read_text(), "private skill")
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "checkout instructions\n")
        self.assertEqual(tomllib.loads((self.repo / "config.toml").read_text())["model"], "personal")
        snapshots = list((self.repo / ".install-backups").iterdir())
        self.assertEqual(len(snapshots), 1)
        self.assertEqual((snapshots[0] / "AGENTS.md").read_text(), "old instructions")
        for path in ("skills/personal/SKILL.md", "history.jsonl", "config.toml",
                     str(snapshots[0].relative_to(self.repo) / "AGENTS.md")):
            ignored = subprocess.run(["git", "check-ignore", "--no-index", path],
                                     cwd=self.repo, capture_output=True)
            self.assertEqual(ignored.returncode, 0, path)
        cached = subprocess.check_output(["git", "diff", "--cached", "--name-only"],
                                         cwd=self.repo, text=True)
        self.assertNotIn("personal", cached)
        self.assertEqual(subprocess.check_output(["git", "diff", "--cached", "--binary"],
                                                cwd=self.repo), self.initial_staged)
        self.assertNotEqual(subprocess.run(["git", "rev-parse", "--verify", "HEAD"],
                                          cwd=self.repo, capture_output=True).returncode, 0)

    def test_cancel_eof_and_discard_confirmation(self):
        old = self.home / ".codex"
        old.mkdir()
        (old / "private.md").write_text("keep")
        for answer in ("cancel\n", "", "discard\nno\n"):
            self.assertNotEqual(self.install(answer).returncode, 0)
            self.assertEqual((old / "private.md").read_text(), "keep")
            self.assertFalse((self.repo / "config.toml").exists())
        self.good(self.install("discard\nDELETE\n"))
        self.assertTrue(old.is_symlink())
        self.assertFalse((self.repo / "private.md").exists())

    def test_external_symlinks_are_not_overwritten(self):
        old = self.home / ".codex"
        old.mkdir()
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("unchanged")
        (old / "external").symlink_to(outside, target_is_directory=True)
        (old / "new-folder").mkdir()
        (old / "new-folder/nested-link").symlink_to(outside, target_is_directory=True)
        (self.repo / "data").symlink_to(outside, target_is_directory=True)
        (old / "data").mkdir()
        (old / "data/secret.md").write_text("incoming")
        self.good(self.install("merge\n"))
        self.assertEqual((outside / "secret.md").read_text(), "unchanged")
        self.assertFalse((self.repo / "external").exists())
        self.assertFalse((self.repo / "new-folder/nested-link").exists())
        snapshot = next((self.repo / ".install-backups").iterdir())
        self.assertTrue((snapshot / "external").is_symlink())

    def test_overlap_refused_before_mutation(self):
        old = self.home / ".codex"
        old.symlink_to(self.base, target_is_directory=True)
        result = self.install("discard\nDELETE\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(old.is_symlink())
        self.assertFalse((self.repo / "config.toml").exists())

    def test_missing_provider_is_reported_before_migration(self):
        old = self.home / ".codex"
        old.mkdir()
        (old / "private.md").write_text("keep")
        result = self.install("discard\nDELETE\n", "--codex-bin", "/missing/codex", deps=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((old / "private.md").read_text(), "keep")

    def test_discard_only_unlinks_an_external_home(self):
        old = self.home / ".codex"
        external = self.base / "previous-home"
        external.mkdir()
        (external / "history.jsonl").write_text("keep external target")
        old.symlink_to(external, target_is_directory=True)
        self.good(self.install("discard\nDELETE\n"))
        self.assertEqual((external / "history.jsonl").read_text(), "keep external target")

    def test_dependency_failure_is_not_success_and_retry_recovers(self):
        # The fake isolates an unavailable outer provider, not migration or plugin code.
        provider = self.base / "fake-codex"
        provider.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root = Path(os.environ["CODEX_HOME"])
args = sys.argv[1:]
if args[:2] == ["plugin", "list"]:
    installed = [] if not (root / ".provider-ready").exists() else [{"pluginId":"dot-codex-tools@dot-codex", "installed":True, "enabled":True}]
    print(json.dumps({"installed":installed}))
elif args[:2] == ["plugin", "add"]:
    if not (root / ".allow-provider").exists():
        print("simulated provider failure", file=sys.stderr)
        sys.exit(1)
    (root / ".provider-ready").touch()
else:
    print("{}")
''')
        provider.chmod(0o755)
        first = self.install("", "--codex-bin", str(provider), deps=True)
        self.assertNotEqual(first.returncode, 0)
        self.assertIn("dependency installation is incomplete", first.stderr)
        self.assertEqual((self.home / ".codex").resolve(), self.repo)
        (self.repo / ".allow-provider").touch()
        self.good(self.install("", "--codex-bin", str(provider), deps=True))

    def test_real_codex_plugin_lifecycle(self):
        codex = shutil.which("codex")
        self.assertIsNotNone(codex, "real Codex CLI is a proof prerequisite")
        self.good(self.install("", "--codex-bin", codex, deps=True))

        env = dict(self.env, CODEX_HOME=str(self.repo))
        result = subprocess.run([codex, "plugin", "list", "--json"],
                                env=env, text=True, capture_output=True, check=True)
        installed = json.loads(result.stdout)["installed"]
        plugin = next(item for item in installed if item["pluginId"] == "dot-codex-tools@dot-codex")
        self.assertTrue(plugin["installed"])
        self.assertTrue(plugin["enabled"])
        listed = subprocess.run([codex, "mcp", "list", "--json"], env=env,
                                text=True, capture_output=True, check=True)
        servers = {item["name"]: item for item in json.loads(listed.stdout)}
        self.assertEqual(set(servers), {"shadcn", "context7", "agentation", "openaiDeveloperDocs", "reui"})
        self.assertTrue(all(item["enabled"] for item in servers.values()))
        self.good(self.install("", "--codex-bin", codex, deps=True))

    def test_optional_plugin_prerequisite_and_activation(self):
        codex = shutil.which("codex")
        self.assertIsNotNone(codex)
        self.env.pop("ORIGINKIT_API_KEY", None)
        missing = self.install("", "--codex-bin", codex, "--with", "originkit", deps=True)
        self.assertNotEqual(missing.returncode, 0)
        self.assertFalse((self.home / ".codex").exists())
        self.assertIn("ORIGINKIT_API_KEY", missing.stderr)
        self.env["ORIGINKIT_API_KEY"] = "synthetic-local-proof-value"
        self.good(self.install("", "--codex-bin", codex, "--with", "originkit", deps=True))
        env = dict(self.env, CODEX_HOME=str(self.repo))
        listed = subprocess.run([codex, "mcp", "list", "--json"], env=env,
                                text=True, capture_output=True, check=True)
        servers = {item["name"]: item for item in json.loads(listed.stdout)}
        self.assertTrue(servers["originkit"]["enabled"])
        self.assertEqual(servers["originkit"]["transport"]["bearer_token_env_var"], "ORIGINKIT_API_KEY")
        self.assertNotIn("synthetic-local-proof-value", (self.repo / "config.toml").read_text())
        self.env.pop("ORIGINKIT_API_KEY")
        missing_again = self.install("", "--codex-bin", codex, deps=True)
        self.assertNotEqual(missing_again.returncode, 0)
        self.assertIn("ORIGINKIT_API_KEY", missing_again.stderr)


if __name__ == "__main__":
    unittest.main()
