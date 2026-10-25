"""Exercise the public operator entry point without a live provider."""
import json
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]


class RuntimeJourney(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([str(ROOT / "secondbrain.sh"), *args], cwd=ROOT,
                              text=True, capture_output=True, check=True)

    def test_setup_plan(self):
        output = self.run_cli("setup", "--plan").stdout
        self.assertIn("backend/context", output)
        self.assertIn("backend/telegram", output)
        self.assertNotIn("az login", output)
        self.assertIn("--mode", self.run_cli("install", "--help").stdout)

    def test_vm_payloads(self):
        self.assertIn("vpn-setup", self.run_cli("vm", "help").stdout)
        with tempfile.TemporaryDirectory() as tmp:
            import os
            env = {**os.environ, "CODEX_VM_TEST_MODE": "1"}
            isolated = Path(tmp) / "clean-checkout"
            (isolated / "scripts").mkdir(parents=True)
            (isolated / "deployments/prod/tf").mkdir(parents=True)
            console = isolated / "scripts/codex-vm.sh"
            shutil.copy2(ROOT / "scripts/codex-vm.sh", console)
            extracted = Path(tmp) / "extracted"
            subprocess.run([str(console), "__extract-helpers", str(extracted)],
                           env=env, check=True, capture_output=True)
            self.assertEqual((extracted / "deployments").resolve(), (isolated / "deployments").resolve())
            helpers = list(extracted.rglob("*.sh"))
            self.assertGreater(len(helpers), 10)
            for helper in helpers:
                subprocess.run(["bash", "-n", str(helper)], check=True)
            bootstrap = (extracted / "scripts/telegram-to-agents-bootstrap.sh").read_text()
            self.assertIn("backend/telegram", bootstrap)
            self.assertIn("https://github.com/marcocello/dot-codex", bootstrap)
        self.assertTrue((ROOT / "deployments/prod/tf/main.tf").is_file())

    def test_private_runtime_and_bot_plan(self):
        output = self.run_cli("whatsapp", "--plan").stdout
        self.assertIn("WHATSAPP_AUTO_REPLY=0", output)
        manifest = json.loads((ROOT / "docs/harness/component-imports.json").read_text())
        self.assertEqual(len(manifest["components"]), 3)
        for component in manifest["components"]:
            if component["revision"] is not None:
                self.assertRegex(component["revision"], r"^[0-9a-f]{40}$")
            self.assertRegex(component["snapshot_sha256"], r"^[0-9a-f]{64}$")
        for directory in ("backend/telegram", "backend/whatsapp"):
            self.assertFalse((ROOT / directory / ".auth").exists())
            self.assertFalse((ROOT / directory / "AGENTS.md").exists())

    def test_remote_gateway_bootstrap(self):
        import os
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp).resolve()
            home, fake, remote, seed = [scratch / name for name in ("home", "bin", "remote-bin", "seed")]
            for directory in (home, fake, remote, seed):
                directory.mkdir()
            (seed / "backend/telegram").mkdir(parents=True)
            (seed / "backend/telegram/pyproject.toml").write_text('[project]\nname="gateway-fixture"\n')
            (seed / ".gitignore").write_text('.venv/\n')
            def git(*args):
                subprocess.run(["git", *map(str, args)], check=True, capture_output=True)
            git("init", "--initial-branch=main", seed)
            git("-C", seed, "add", ".")
            git("-C", seed, "-c", "user.name=Proof", "-c", "user.email=proof@example.invalid",
                "commit", "-m", "bootstrap fixture")
            origin = scratch / "origin.git"
            git("clone", "--bare", seed, origin)
            scripts = {
                fake / "uname": '#!/bin/sh\nprintf "Darwin\\n"\n',
                fake / "ssh": '''#!/usr/bin/env bash
set -euo pipefail
if [[ "$1" == "-o" ]]; then exit 0; fi
if [[ "$1" == "-t" ]]; then
  printf 'onboarding\n' >>"$BOOTSTRAP_LOG"
  mkdir -p "$REMOTE_HOME/.telegram-to-agents/config"
  printf '{}' >"$REMOTE_HOME/.telegram-to-agents/config/config.json"
  exit 0
fi
HOME="$REMOTE_HOME" PATH="$REMOTE_BIN:$PATH" bash -c "$2"
''',
                remote / "systemctl": '#!/bin/sh\nexit 0\n',
                remote / "python3": '''#!/usr/bin/env bash
set -euo pipefail
if [[ "$1 $2" == "-m venv" ]]; then
  mkdir -p "$3/bin"
  cp "$REMOTE_BIN/python3" "$3/bin/python"
elif [[ "$1 $2 $3 $4" == "-m pip install --upgrade" ]]; then
  [[ "$5" == "$HOME/projects/dot-codex/backend/telegram" && -f "$5/pyproject.toml" ]]
  printf 'installed-bundled-package\n' >>"$BOOTSTRAP_LOG"
  printf '#!/bin/sh\nprintf "%%s\\n" "$*" >>"$BOOTSTRAP_LOG"\n' >"$HOME/projects/dot-codex/.venv/bin/telegram-to-agents"
  chmod +x "$HOME/projects/dot-codex/.venv/bin/telegram-to-agents"
else
  exit 88
fi
''',
            }
            for path, content in scripts.items():
                path.write_text(content)
                path.chmod(0o700)
            env = {**os.environ, "CODEX_VM_TEST_MODE": "1", "REMOTE_HOME": str(home),
                   "REMOTE_BIN": str(remote), "BOOTSTRAP_LOG": str(scratch / "actions"),
                   "TELEGRAM_TO_AGENTS_REPOSITORY_URL": str(origin),
                   "PATH": str(fake) + os.pathsep + os.environ["PATH"]}
            bundle = scratch / "helpers"
            subprocess.run([str(ROOT / "scripts/codex-vm.sh"), "__extract-helpers", str(bundle)],
                           env=env, check=True, capture_output=True)
            helper = bundle / "scripts/telegram-to-agents-bootstrap.sh"
            for _ in range(2):
                result = subprocess.run([str(helper)], env=env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actions = (scratch / "actions").read_text().splitlines()
            self.assertEqual(actions.count("installed-bundled-package"), 2)
            self.assertEqual(actions.count("onboarding"), 1)
            self.assertEqual(actions.count("restart"), 1)
            self.assertTrue((home / ".local/bin/telegram-to-agents").is_symlink())


if __name__ == "__main__":
    unittest.main()
