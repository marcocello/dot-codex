"""Public installer journeys; isolate only package/account/service providers."""

import hashlib
import fcntl
import json
import os
from pathlib import Path
import pty
import plistlib
import select
import shutil
import signal
import subprocess
import tarfile
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[4]
WIZARD_PHASES = ["copy", "cli", "harness", "dependencies", "login", "service", "pair", "doctor"]
FAKE_CODEX = '''#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path
args = sys.argv[1:]
if os.environ.get("FAKE_CODEX_LOG"):
    with open(os.environ["FAKE_CODEX_LOG"], "a") as log:
        log.write(json.dumps(args) + "\\n")
if args == ["--version"]:
    if os.environ.get("FAKE_BLOCK_VERSION"):
        Path(os.environ["HOME"], ".version-running").touch()
        time.sleep(120)
    print("codex-cli __VERSION__")
elif args == ["login", "status"]:
    sys.exit(0 if Path(os.environ["HOME"], ".signed-in").exists() else 1)
elif args == ["login", "--device-auth"]:
    if os.environ.get("FAKE_BLOCK_LOGIN"):
        Path(os.environ["HOME"], ".login-running").touch()
        time.sleep(120)
    Path(os.environ["HOME"], ".signed-in").touch()
elif args[:2] == ["remote-control", "start"]:
    print(json.dumps({"status": os.environ.get("FAKE_REMOTE_STATUS", "connected"),
      "timedOut": os.environ.get("FAKE_TIMED_OUT") == "1",
      "environmentId": "fixture-env", "daemon": {"status": "alreadyRunning"}}))
elif args[:2] == ["remote-control", "pair"]:
    print("PAIRING-SECRET-FIXTURE")
elif args[:2] == ["plugin", "add"]:
    marker = Path(os.environ["CODEX_HOME"], ".test-plugin")
    installed = json.loads(marker.read_text()) if marker.exists() else []
    installed.append(next(arg for arg in args[2:] if "@" in arg))
    marker.write_text(json.dumps(installed))
    print("{}")
elif args[:2] == ["plugin", "list"]:
    marker = Path(os.environ["CODEX_HOME"], ".test-plugin")
    installed = [{"pluginId": item, "installed":True, "enabled":True}
      for item in json.loads(marker.read_text())] if marker.exists() else []
    print(json.dumps({"installed":installed}))
elif args == ["app-server", "daemon", "version"] and os.environ.get("FAKE_DAEMON_MISSING"):
    sys.exit(4)
elif args[:3] == ["plugin", "marketplace", "add"] and os.environ.get("FAKE_MARKETPLACE_FAIL"):
    sys.exit(9)
else:
    print("{}")
'''


class GuidedInstallJourneys(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="guided install ")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.home = self.base / "home"
        self.home.mkdir()
        self.repo = self.base / "source checkout"
        (self.repo / "scripts").mkdir(parents=True)
        for name in ("install.sh", "config.template.toml", ".gitignore", "skills.toml"):
            shutil.copy2(ROOT / name, self.repo / name)
        for name in ("install.py", "install_runtime.py", "install_state.py", "install_service.py", "skill_inventory.py"):
            if (ROOT / "scripts" / name).exists():
                shutil.copy2(ROOT / "scripts" / name, self.repo / "scripts" / name)
        shutil.copytree(ROOT / "integrations", self.repo / "integrations")
        (self.repo / "skills.toml").write_text(
            'schema = 1\n\n[[skills]]\nname = "dot-codex-tools"\n'
            'kind = "plugin"\nselector = "dot-codex-tools@dot-codex"\nenabled = true\n')
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "add", "-f", "install.sh", "scripts", "integrations",
                        "config.template.toml", ".gitignore", "skills.toml"], cwd=self.repo, check=True)
        self.env = dict(os.environ, HOME=str(self.home), FAKE_CODEX_LOG=str(self.base / "calls"))
        self.env.pop("CODEX_HOME", None)
        self.provider = self.base / "codex-provider"
        self.provider.write_text(FAKE_CODEX.replace("__VERSION__", "1.2.3"))
        self.provider.chmod(0o755)

    def command(self, *args):
        return ["bash", str(self.repo / "install.sh"), "--user-home", str(self.home), *args]

    def run_install(self, *args, answer="", env=None):
        return subprocess.run(self.command(*args), input=answer, text=True, capture_output=True,
                              env=env or self.env, cwd=self.repo, timeout=30)

    def good(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def old_home(self):
        old = self.home / ".codex"
        old.mkdir()
        (old / "history.jsonl").write_text("private history")
        return old

    def package(self, version="1.2.3", unsafe=False):
        root = self.base / ("package-" + version)
        for name in ("bin/codex", "bin/codex-code-mode-host", "codex-path/rg"):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(FAKE_CODEX.replace("__VERSION__", version) if name == "bin/codex"
                            else "#!/bin/sh\nexit 0\n")
            path.chmod(0o755)
        (root / "codex-package.json").write_text(json.dumps({"version": version}))
        archive = self.base / (version + ".tar.gz")
        with tarfile.open(archive, "w:gz") as stream:
            stream.add(root, arcname=".")
            if unsafe:
                item = tarfile.TarInfo("../../escaped")
                stream.addfile(item)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        return ["cli", "--version", version, "--package-file", str(archive), "--sha256", digest,
                "--yes"]

    def checkpoint(self):
        return json.loads((self.home / ".local/state/dot-codex/install.json").read_text())

    def test_dry_run_and_doctor_do_not_mutate(self):
        before = sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*"))
        result = self.run_install("all", "--dry-run")
        self.good(result)
        self.assertIn("pair", result.stdout)
        self.assertEqual(before, sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*")))
        missing = self.run_install("doctor", "--codex-bin", str(self.base / "missing"))
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(before, sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*")))

    def test_copy_is_separate_and_excludes_private_state(self):
        (self.repo / "auth.json").write_text("secret")
        destination = self.base / "prepared harness"
        self.good(self.run_install("copy", "--destination", str(destination), "--yes"))
        self.assertTrue((destination / "install.sh").is_file())
        self.assertTrue((destination / ".git").is_dir())
        self.assertFalse((destination / "auth.json").exists())
        self.assertFalse((self.home / ".codex").exists())
        self.assertNotEqual(self.run_install("copy", "--destination", str(destination), "--yes").returncode, 0)

    def test_copy_of_uncommitted_installer_runtime_is_usable(self):
        subprocess.run(["git", "rm", "--cached", "-q", "scripts/install_runtime.py"], cwd=self.repo, check=True)
        destination = self.base / "review copy"
        self.good(self.run_install("copy", "--destination", str(destination), "--yes"))
        result = subprocess.run(["bash", str(destination / "install.sh"), "--help"],
                                env=self.env, capture_output=True, text=True, timeout=10)
        self.good(result)

    def test_merge_preserves_internal_package_links_and_cli(self):
        old = self.old_home()
        release = old / "packages/standalone/releases/v1"
        (release / "bin").mkdir(parents=True)
        shutil.copy2(self.provider, release / "bin/codex")
        (release / "codex").symlink_to("bin/codex")
        (old / "packages/standalone/current").symlink_to(release)
        binary = self.home / ".local/bin/codex"
        binary.parent.mkdir(parents=True)
        binary.symlink_to(old / "packages/standalone/current/bin/codex")
        outside = self.base / "private-external"
        outside.write_text("keep")
        (old / "foreign").symlink_to(outside)
        result = self.run_install("harness", "--mode", "merge", "--yes")
        self.good(result)
        self.assertEqual(subprocess.check_output([str(binary), "--version"], text=True).strip(),
                         "codex-cli 1.2.3")
        self.assertEqual((old / "history.jsonl").read_text(), "private history")
        self.assertTrue((old / "packages/standalone/current").is_symlink())
        self.assertFalse((self.repo / "foreign").exists())
        self.assertEqual(outside.read_text(), "keep")

    def test_replace_and_restore_keep_prior_home(self):
        old = self.old_home()
        self.good(self.run_install("harness", "--mode", "replace", "--yes"))
        self.assertEqual(old.resolve(), self.repo)
        self.assertFalse((self.repo / "history.jsonl").exists())
        self.good(self.run_install("restore", "--yes"))
        self.assertFalse(old.is_symlink())
        self.assertEqual((old / "history.jsonl").read_text(), "private history")
        self.assertFalse((self.home / ".profile").exists())

    def test_rerun_retains_original_restore_and_refuses_later_shell_edits(self):
        self.old_home()
        self.good(self.run_install("harness", "--mode", "merge", "--yes"))
        receipt = self.home / ".local/state/dot-codex/last-activation.json"
        before = receipt.read_bytes()
        self.good(self.run_install("harness", "--yes"))
        self.assertEqual(receipt.read_bytes(), before)
        profile = self.home / ".profile"
        profile.write_text(profile.read_text() + "\n# later edit\n")
        refused = self.run_install("restore", "--yes")
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("later edit", profile.read_text())

    def test_copy_then_activate_uses_destination(self):
        destination = self.base / "installed harness"
        self.good(self.run_install("--steps", "copy,harness", "--destination", str(destination),
                                   "--mode", "merge", "--yes"))
        self.assertEqual((self.home / ".codex").resolve(), destination)
        self.assertIn(str(destination), (self.home / ".profile").read_text())

    def test_cli_publication_fresh_repeat_upgrade_and_bad_digest(self):
        args = self.package()
        self.good(self.run_install(*args))
        binary = self.home / ".local/bin/codex"
        self.good(self.run_install(*args))
        upgraded = self.package("1.2.4")
        self.good(self.run_install(*upgraded))
        self.assertEqual(subprocess.check_output([str(binary), "--version"], text=True).strip(),
                         "codex-cli 1.2.4")
        self.assertIn(".local/share/dot-codex/cli", str(binary.resolve()))
        env = dict(self.env, PATH="/usr/bin:/bin")
        shell = subprocess.run(["/bin/sh", "-c", '. "$HOME/.profile"; command -v codex'],
                               env=env, capture_output=True, text=True, check=True)
        self.assertEqual(shell.stdout.strip(), str(binary))
        self.assertEqual((self.home / ".profile").read_text().count("# BEGIN managed Codex CLI"), 1)
        bad = args.copy()
        bad[bad.index("--sha256") + 1] = "0" * 64
        self.assertNotEqual(self.run_install(*bad).returncode, 0)
        self.assertEqual(subprocess.check_output([str(binary), "--version"], text=True).strip(),
                         "codex-cli 1.2.4")
        self.assertFalse(list((self.home / ".local/share/dot-codex/cli").rglob(".current.*")))

    def test_archive_traversal_is_rejected(self):
        result = self.run_install(*self.package(unsafe=True))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / ".local/bin/codex").exists())
        self.assertFalse((self.base / "escaped").exists())

    def test_interrupted_package_validation_keeps_published_cli(self):
        self.good(self.run_install(*self.package()))
        process = subprocess.Popen(self.command(*self.package("1.2.4")),
                                   env=dict(self.env, FAKE_BLOCK_VERSION="1"),
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_process, process)
        deadline = time.monotonic() + 10
        while not (self.home / ".version-running").exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue((self.home / ".version-running").exists())
        process.send_signal(signal.SIGINT)
        process.communicate(timeout=5)
        self.assertEqual(process.returncode, 130)
        binary = self.home / ".local/bin/codex"
        self.assertEqual(subprocess.check_output([str(binary), "--version"], text=True).strip(),
                         "codex-cli 1.2.3")
        self.assertEqual(self.checkpoint()["phases"]["cli"], "interrupted")

    def interrupt_activation(self, sig):
        old = self.old_home()
        bulky = old / "sessions"
        bulky.mkdir()
        for number in range(1500):
            (bulky / str(number)).write_bytes(b"state" * 4096)
        process = subprocess.Popen(self.command("harness", "--mode", "merge", "--yes"),
                                   env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        self.addCleanup(self.stop_process, process)
        pending = self.home / ".local/state/dot-codex/pending.json"
        deadline = time.monotonic() + 10
        while (old.exists() or not pending.exists()) and time.monotonic() < deadline:
            if process.poll() is not None:
                self.fail("Activation completed before the filesystem interruption boundary")
            time.sleep(0.001)
        process.send_signal(sig)
        process.communicate(timeout=5)
        return old, process

    @staticmethod
    def stop_process(process):
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
            process.communicate(timeout=5)

    def test_ctrl_c_during_activation_rolls_back_files_and_environment(self):
        old, process = self.interrupt_activation(signal.SIGINT)
        self.assertEqual(process.returncode, 130)
        self.assertFalse(old.is_symlink())
        self.assertEqual((old / "history.jsonl").read_text(), "private history")
        self.assertFalse((self.home / ".profile").exists())
        self.assertFalse((self.repo / "sessions").exists())
        self.assertFalse((self.home / ".local/state/dot-codex/pending.json").exists())

    def test_next_run_recovers_a_killed_filesystem_phase(self):
        old, process = self.interrupt_activation(signal.SIGKILL)
        self.assertEqual(process.returncode, -signal.SIGKILL)
        self.good(self.run_install("resume", "--yes"))
        self.assertTrue(old.is_symlink())
        self.assertEqual((old / "history.jsonl").read_text(), "private history")
        self.assertEqual(len(list((old / "sessions").iterdir())), 1500)
        self.assertFalse((self.home / ".local/state/dot-codex/pending.json").exists())

    def test_concurrent_installers_are_refused(self):
        state = self.home / ".local/state/dot-codex"
        state.mkdir(parents=True)
        with (state / "install.lock").open("w") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.run_install("harness", "--yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Another installer", result.stderr)
        self.assertFalse((self.home / ".codex").exists())

    def test_replace_rolls_back_if_previously_working_cli_breaks(self):
        old = self.old_home()
        binary = old / "codex"
        shutil.copy2(self.provider, binary)
        result = self.run_install("harness", "--mode", "replace", "--codex-bin", str(binary), "--yes")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(old.is_symlink())
        self.assertTrue(binary.is_file())
        self.assertFalse((self.home / ".profile").exists())

    def test_plain_wizard_selection_and_eof(self):
        answers = "\n" * 7 + "y\ny\n"
        result = self.run_install("--wizard", answer=answers)
        self.assertIn("harness", result.stdout.lower())
        self.assertFalse((self.home / ".codex").exists())
        cancelled = self.run_install("--wizard", answer="")
        self.assertNotEqual(cancelled.returncode, 0)
        self.assertFalse((self.home / ".local/state/dot-codex/install.json").exists())

    def test_wizard_executes_only_the_confirmed_phase(self):
        self.good(self.run_install("--wizard", "--codex-bin", str(self.provider),
                                   answer="\n\ny\n" + "\n" * 5 + "y\n"))
        self.assertEqual((self.home / ".codex").resolve(), self.repo)
        self.assertEqual(self.checkpoint()["phases"], {"harness": "done"})

    def test_wizard_defaults_skip_every_phase_without_mutation(self):
        self.old_home()
        before = sorted(str(path.relative_to(self.home)) for path in self.home.rglob("*"))
        result = self.run_install("--wizard", answer="\n" * 8)
        self.good(result)
        self.assertEqual(result.stdout.count("Run this step? [y/N]"), 8)
        self.assertIn("No phases selected", result.stdout)
        self.assertEqual(before, sorted(str(path.relative_to(self.home)) for path in self.home.rglob("*")))
        self.assertFalse((self.base / "calls").exists())

    def test_wizard_final_confirmation_defaults_to_no(self):
        self.old_home()
        result = self.run_install("--wizard", answer="\n\ny\n" + "\n" * 6)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Run this plan? [y/N]", result.stdout)
        self.assertFalse((self.home / ".codex").is_symlink())
        self.assertFalse((self.home / ".local/state/dot-codex/install.json").exists())

    def test_wizard_retries_invalid_answer_and_restricts_explicit_steps(self):
        result = self.run_install("--wizard", "--steps", "cli,doctor", answer="maybe\n\n\n")
        self.good(result)
        self.assertEqual(result.stdout.count("Run this step? [y/N]"), 3)
        self.assertNotIn("Sign in to Codex", result.stdout)
        self.assertFalse((self.home / ".local").exists())

    def test_wizard_colors_can_be_forced_disabled_or_suppressed(self):
        env = dict(self.env, TERM="xterm-256color")
        env.pop("NO_COLOR", None)
        forced = self.run_install("--wizard", "--color", "always", answer="\n" * 8, env=env)
        self.good(forced)
        self.assertIn("\x1b[1;38;2;51;153;255m", forced.stdout)
        self.assertIn("\x1b[38;2;102;178;255mRun this step?", forced.stdout)
        self.assertIn("\x1b[38;2;255;176;32m!", forced.stdout)
        self.assertIn("dot-codex Installer", forced.stdout)
        self.assertIn("[1/8] Copy the harness", forced.stdout)
        self.assertNotIn("╭", forced.stdout)  # Redirected output uses the simple banner.
        selected = self.run_install("--wizard", "--steps", "harness", "--color", "always",
                                    answer="y\n\n", env=env)
        self.assertNotEqual(selected.returncode, 0)
        self.assertIn("\x1b[38;2;0;229;204m✓", selected.stdout)
        self.assertIn("Install plan", selected.stdout)
        self.assertIn("\x1b[38;2;90;100;128mUser home:", selected.stdout)
        self.assertIn("\x1b[38;2;230;57;70m✗", selected.stderr)
        for options, selected_env in [([], env), (["--color", "never"], env),
                                      (["--color", "always"], dict(env, NO_COLOR="1"))]:
            result = self.run_install("--wizard", *options, answer="\n" * 8, env=selected_env)
            self.good(result)
            self.assertNotIn("\x1b[", result.stdout + result.stderr)

    def test_automatic_colors_in_a_real_terminal_respect_term_and_no_color(self):
        for term, no_color, columns, expected in [
            ("xterm-256color", False, 80, True), ("dumb", False, 80, False),
            ("xterm-256color", True, 80, False), ("xterm-256color", False, 30, True),
        ]:
            with self.subTest(term=term, no_color=no_color, columns=columns):
                env = dict(self.env, TERM=term)
                env["COLUMNS"] = str(columns)
                env.pop("NO_COLOR", None)
                if no_color:
                    env["NO_COLOR"] = "1"
                master, slave = pty.openpty()
                process = subprocess.Popen(self.command("--wizard"), stdin=slave, stdout=slave,
                                           stderr=slave, env=env, start_new_session=True)
                os.close(slave)
                output = b""
                try:
                    os.write(master, b"\n" * 8)
                    deadline = time.monotonic() + 10
                    while time.monotonic() < deadline:
                        if select.select([master], [], [], 0.2)[0]:
                            try:
                                chunk = os.read(master, 8192)
                            except OSError:
                                break
                            if not chunk:
                                break
                            output += chunk
                    self.assertEqual(process.wait(timeout=5), 0)
                    self.assertIn(b"No phases selected", output)
                    self.assertEqual(b"\x1b[" in output, expected)
                    self.assertEqual("╭".encode() in output, term != "dumb" and columns == 80)
                finally:
                    os.close(master)
                    self.stop_process(process)

    def test_ctrl_c_in_terminal_menu_leaves_home_unchanged(self):
        old = self.old_home()
        master, slave = pty.openpty()
        process = subprocess.Popen(self.command("--wizard"), stdin=slave, stdout=slave,
                                   stderr=slave, env=self.env, start_new_session=True)
        os.close(slave)
        self.addCleanup(os.close, master)
        output = b""
        deadline = time.monotonic() + 10
        while b"Run this step?" not in output and time.monotonic() < deadline:
            if select.select([master], [], [], 0.2)[0]:
                output += os.read(master, 8192)
        self.assertIn(b"Run this step?", output)
        process.send_signal(signal.SIGINT)
        self.assertEqual(process.wait(timeout=5), 130)
        self.assertEqual((old / "history.jsonl").read_text(), "private history")

    def test_interrupted_login_can_resume_without_repeating_completed_home(self):
        env = dict(self.env, FAKE_BLOCK_LOGIN="1")
        process = subprocess.Popen(self.command("--steps", "harness,login", "--mode", "merge",
                                   "--yes", "--codex-bin", str(self.provider)), env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_process, process)
        deadline = time.monotonic() + 10
        while not (self.home / ".login-running").exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue((self.home / ".login-running").exists())
        process.send_signal(signal.SIGINT)
        output = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 130, str(output))
        self.assertEqual((self.home / ".codex").resolve(), self.repo)
        self.assertEqual(self.checkpoint()["phases"]["login"], "interrupted")
        self.good(self.run_install("resume", "--codex-bin", str(self.provider), "--yes"))
        self.assertTrue((self.home / ".signed-in").exists())
        self.assertEqual(self.checkpoint()["phases"]["login"], "done")

    def test_pair_requires_connected_response_and_does_not_store_code(self):
        (self.home / ".signed-in").touch()
        env = dict(self.env, FAKE_REMOTE_STATUS="connecting")
        result = self.run_install("pair", "--codex-bin", str(self.provider), "--yes", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("PAIRING-SECRET-FIXTURE", result.stdout)
        result = self.run_install("pair", "--codex-bin", str(self.provider), "--yes")
        self.good(result)
        self.assertIn("PAIRING-SECRET-FIXTURE", result.stdout)
        self.assertNotIn("PAIRING-SECRET-FIXTURE", json.dumps(self.checkpoint()))
        timed = self.run_install("pair", "--codex-bin", str(self.provider), "--yes",
                                 env=dict(self.env, FAKE_TIMED_OUT="1"))
        self.assertNotEqual(timed.returncode, 0)

    def test_resume_keeps_optional_integrations_selected_before_provider_failure(self):
        env = dict(self.env, ORIGINKIT_API_KEY="fixture-only-value")
        result = self.run_install("dependencies", "--with", "originkit", "--codex-bin", str(self.provider),
                                  "--yes", env=dict(env, FAKE_MARKETPLACE_FAIL="1"))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.checkpoint()["options"]["with_integration"], ["originkit"])
        self.good(self.run_install("resume", "--yes", env=env))
        self.assertIn("originkit@dot-codex", (self.repo / "skills.toml").read_text())
        self.assertNotIn("fixture-only-value", json.dumps(self.checkpoint()))

    def test_resume_respects_explicit_default_version_override(self):
        broken = self.package()
        broken[broken.index("--sha256") + 1] = "0" * 64
        self.assertNotEqual(self.run_install(*broken).returncode, 0)
        replacement = self.package("0.151.0")
        self.good(self.run_install("resume", *replacement[1:]))
        binary = self.home / ".local/bin/codex"
        self.assertEqual(subprocess.check_output([str(binary), "--version"], text=True).strip(),
                         "codex-cli 0.151.0")

    def test_resume_requires_custom_url_again_without_storing_its_secret(self):
        bindir = self.base / "download-bin"
        bindir.mkdir()
        curl = bindir / "curl"
        curl.write_text("#!/bin/sh\nexit 8\n")
        curl.chmod(0o755)
        env = dict(self.env, PATH=str(bindir) + os.pathsep + self.env["PATH"])
        first = self.run_install("cli", "--package-url", "https://example.invalid/package?token=fixture-secret",
                                 "--sha256", "0" * 64, "--yes", env=env)
        self.assertNotEqual(first.returncode, 0)
        self.assertNotIn("fixture-secret", json.dumps(self.checkpoint()))
        second = self.run_install("resume", "--yes", env=env)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("original --package-url", second.stderr)

    def fake_service_manager(self, linger="yes", failed=False):
        bindir = self.base / "system-bin"
        bindir.mkdir(exist_ok=True)
        for name in ("systemctl", "loginctl", "launchctl"):
            path = bindir / name
            path.write_text("#!/bin/sh\n" +
                ("echo " + linger + "\n" if name == "loginctl" else
                 "case \"$*\" in *is-active*) exit " + ("1" if failed else "0") + ";; esac\n"))
            path.chmod(0o755)
        return dict(self.env, PATH=str(bindir) + os.pathsep + self.env["PATH"])

    def test_service_definition_and_missing_linger_or_connection_fail(self):
        (self.home / ".signed-in").touch()
        self.good(self.run_install("harness", "--mode", "merge", "--yes"))
        args = ("service", "--service-manager", "systemd", "--codex-bin", str(self.provider), "--yes")
        no_linger = self.run_install(*args, env=self.fake_service_manager(linger="no"))
        self.assertNotEqual(no_linger.returncode, 0)
        self.assertIn("linger", no_linger.stdout + no_linger.stderr)
        self.good(self.run_install(*args, env=self.fake_service_manager()))
        service = (self.home / ".config/systemd/user/codex-remote-control.service").read_text()
        self.assertIn(str(self.provider), service)
        self.assertIn("--bootstrap", service)
        self.assertIn(str(self.repo), service)
        result = self.run_install(*args, env=dict(self.fake_service_manager(), FAKE_REMOTE_STATUS="connecting"))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotEqual(self.run_install(*args, env=self.fake_service_manager(failed=True)).returncode, 0)

    def test_launchagent_and_persisted_health_runner(self):
        (self.home / ".signed-in").touch()
        self.good(self.run_install("harness", "--mode", "merge", "--yes"))
        self.good(self.run_install("service", "--service-manager", "launchd", "--yes",
                                   "--codex-bin", str(self.provider), env=self.fake_service_manager()))
        path = self.home / "Library/LaunchAgents/com.marcocello.codex-remote-control.plist"
        value = plistlib.loads(path.read_bytes())
        self.assertTrue(value["RunAtLoad"])
        self.assertTrue(value["KeepAlive"])
        helper = Path(value["ProgramArguments"][1])
        self.assertNotIn(str(self.repo), str(helper))
        command = value["ProgramArguments"][:-1]
        good = subprocess.run(command, env=self.env, capture_output=True, text=True, timeout=10)
        self.assertEqual(good.returncode, 0, good.stderr)
        bad = subprocess.run(command, env=dict(self.env, FAKE_REMOTE_STATUS="connecting"),
                             capture_output=True, text=True, timeout=10)
        self.assertNotEqual(bad.returncode, 0)

    def test_doctor_detects_service_bound_to_previous_harness(self):
        (self.home / ".signed-in").touch()
        self.good(self.run_install("harness", "--mode", "merge", "--yes"))
        env = self.fake_service_manager()
        self.good(self.run_install("service", "--service-manager", "systemd", "--yes",
                                   "--codex-bin", str(self.provider), env=env))
        self.good(self.run_install("--steps", "copy,harness", "--destination", str(self.base / "new harness"),
                                   "--mode", "merge", "--codex-bin", str(self.provider), "--yes"))
        result = self.run_install("doctor", "--codex-bin", str(self.provider), env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another Codex Home", result.stderr)

    def test_all_composes_install_activation_dependencies_login_service_pair_and_doctor(self):
        package = self.package()
        result = self.run_install("all", *package[1:], "--mode", "merge", "--service-manager", "systemd",
                                  env=self.fake_service_manager())
        self.good(result)
        self.assertEqual(self.checkpoint()["phases"], {
            name: "done" for name in ["cli", "harness", "dependencies", "login", "service", "pair", "doctor"]})
        self.assertTrue((self.repo / ".test-plugin").exists())
        self.assertTrue((self.home / ".signed-in").exists())
        self.assertIn("PAIRING-SECRET-FIXTURE", result.stdout)
        self.assertNotIn("PAIRING-SECRET-FIXTURE", json.dumps(self.checkpoint()))

    def test_resume_completes_a_failed_final_doctor(self):
        package = self.package()
        env = self.fake_service_manager()
        first = self.run_install("all", *package[1:], "--mode", "merge", "--service-manager", "systemd",
                                 env=dict(env, FAKE_DAEMON_MISSING="1"))
        self.assertNotEqual(first.returncode, 0)
        self.assertEqual(self.checkpoint()["phases"]["doctor"], "failed")
        self.good(self.run_install("resume", "--yes", env=env))
        self.assertTrue(all(status == "done" for status in self.checkpoint()["phases"].values()))


if __name__ == "__main__":
    unittest.main()
