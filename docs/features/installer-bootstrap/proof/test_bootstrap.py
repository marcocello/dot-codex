"""Real shell activation; only OS, package manager and final child are fixtures."""
import json
import os
from pathlib import Path
import pty
import select
import shlex
import shutil
import signal
import subprocess
import sys
import time

import pytest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))


class Shell:
    def __init__(self, tmp, os_name="Linux"):
        self.root, self.bin, self.home = tmp / "checkout with spaces", tmp / "bin", tmp / "home"
        (self.root / "scripts").mkdir(parents=True)
        self.bin.mkdir()
        self.home.mkdir()
        for name in ("secondbrain.sh", "install.sh", "scripts/setup_bootstrap.sh", "scripts/setup-plan.txt"):
            shutil.copy2(ROOT / name, self.root / name)
        self.log, self.ready = tmp / "packages", tmp / "python-ready"
        self.record = tmp / "child.json"
        self.env = {**os.environ, "HOME": str(self.home), "PATH": str(self.bin), "NO_COLOR": "1",
                    "RECORD": str(self.record), "PACKAGES": str(self.log), "READY": str(self.ready)}
        for key in ("SECOND_BRAIN_STATE", "SECOND_BRAIN_PYTHON"):
            self.env.pop(key, None)
        for name in ("bash", "dirname", "mktemp", "rm", "env"):
            (self.bin / name).symlink_to(shutil.which(name))
        self.script("uname", "printf '%s\\n' " + shlex.quote(os_name))
        self.script("cat", "if [[ ${1:-} == /etc/os-release ]]; then printf 'ID=ubuntu\\nVERSION_ID=\"24.04\"\\n'; else exec /bin/cat \"$@\"; fi")
        self.script("sudo", 'printf "sudo %s\\n" "$*" >> "$PACKAGES"; [[ ${1:-} != -n ]] || shift; exec "$@"')
        self.script("apt-get", 'printf "apt %s\\n" "$*" >> "$PACKAGES"; [[ ${1:-} != install ]] || : > "$READY"')
        self.script("brew", f'if [[ $1 == --prefix ]]; then printf "%s\\n" {shlex.quote(str(tmp / "brew"))}; else printf "brew %s\\n" "$*" >> "$PACKAGES"; : > "$READY"; fi')
        self.script("python3.12", '[[ -f "$READY" ]] || exit 1\nexec ' + shlex.quote(sys.executable) + ' "$@"')
        (self.root / "scripts/secondbrain_platform.py").write_text('''import json, os, sys
from pathlib import Path
Path(os.environ['RECORD']).write_text(json.dumps({'args':sys.argv[1:], 'tty':sys.stdin.isatty(), 'python':sys.executable}))
raise SystemExit(int(os.environ.get('CHILD_STATUS','0')))
''')
        self.choices = tmp / "choices.json"
        self.choices.write_text("{}")

    def script(self, name, body):
        target = self.bin / name
        target.write_text("#!/bin/bash\nset -eu\n" + body + "\n")
        target.chmod(0o700)

    def run(self, *args, entry="secondbrain.sh"):
        return subprocess.run(["/bin/bash", str(self.root / entry), *args], env=self.env,
                              text=True, capture_output=True, timeout=15, stdin=subprocess.DEVNULL)

    def unattended(self, *args, **kwargs):
        return self.run("setup", "--no-prompt", "--config", str(self.choices), *args, **kwargs)


@pytest.mark.parametrize("entry", ["secondbrain.sh", "install.sh"])
def test_help_plan_and_invalid_options_without_python(tmp_path, entry):
    shell = Shell(tmp_path)
    for args in (("setup", "--help"), ("setup", "--dry-run"), ("setup", "--plan", "--mode", "azure")):
        result = shell.run(*args, entry=entry)
        assert result.returncode == 0, result.stderr
        assert "setup" in result.stdout.lower()
        if "--help" not in args:
            assert all(value in result.stdout for value in ("Qdrant", "Pinecone", "backend/context", "backend/telegram"))
    for args in (("setup", "--mode"), ("setup", "--mode", "wrong"), ("setup", "--config"),
                 ("setup", "--wat"), ("setup", "--plan=true"), ("setup", "--component", "all", "--reconfigure")):
        result = shell.run(*args, entry=entry)
        assert result.returncode == 2
    assert not shell.log.exists()
    assert not shell.record.exists()
    assert list(shell.home.iterdir()) == []


@pytest.mark.parametrize("os_name", ["Linux", "Darwin"])
def test_install_verify_and_reuse_interpreter(tmp_path, os_name):
    shell = Shell(tmp_path, os_name)
    shell.script("python3", "exit 1")  # An incompatible active Python must be preserved.
    original = (shell.bin / "python3").read_bytes()
    result = shell.unattended()
    assert result.returncode == 0, result.stderr
    calls = shell.log.read_text()
    assert ("apt install" if os_name == "Linux" else "brew install python@3.12") in calls
    if os_name == "Linux":
        assert "sudo -n" in calls
    observed = json.loads(shell.record.read_text())
    assert observed["args"][:2] == ["setup", "--non-interactive"]
    assert observed["tty"] is False
    assert (shell.bin / "python3").read_bytes() == original
    assert shell.unattended(entry="install.sh").returncode == 0
    assert shell.log.read_text() == calls
    assert list(shell.home.iterdir()) == []


def test_no_tty_and_missing_saved_choices_stop_before_bootstrap(tmp_path):
    shell = Shell(tmp_path)
    result = shell.run("setup")
    assert result.returncode != 0
    assert "terminal" in result.stderr.lower()
    shell.choices.unlink()
    result = shell.unattended()
    assert result.returncode != 0
    assert "config" in result.stderr.lower()
    assert not shell.log.exists()
    assert not shell.record.exists()


def test_bootstrap_failure_does_not_start_wizard(tmp_path):
    shell = Shell(tmp_path)
    shell.script("apt-get", "exit 42")
    result = shell.unattended()
    assert result.returncode != 0
    assert "Python" in result.stderr
    assert "repeat" in result.stderr.lower() or "rerun" in result.stderr.lower()
    assert not shell.record.exists()


@pytest.mark.parametrize("sig,status", [("INT", 130), ("TERM", 143)])
def test_interrupted_bootstrap_returns_resumable_failure(tmp_path, sig, status):
    shell = Shell(tmp_path)
    shell.script("apt-get", f'kill -{sig} "$PPID"\nexit 1')
    result = shell.unattended()
    assert result.returncode == status, result.stderr
    assert "repeat" in result.stderr.lower()
    assert not shell.record.exists()


def test_unsupported_host_and_failed_postinstall_verification(tmp_path):
    shell = Shell(tmp_path, "FreeBSD")
    assert shell.unattended().returncode != 0
    assert not shell.log.exists()
    shell.script("uname", "printf 'Linux\\n'")
    shell.script("python3.12", "exit 1")
    assert shell.unattended().returncode != 0
    assert not shell.record.exists()


def test_unknown_linux_and_missing_homebrew_need_operator_prerequisite(tmp_path):
    shell = Shell(tmp_path)
    shell.script("cat", "printf 'ID=debian\\nVERSION_ID=12\\n'")
    result = shell.unattended()
    assert result.returncode != 0 and "Ubuntu 24.04" in result.stderr
    shell.script("uname", "printf 'Darwin\\n'")
    (shell.bin / "brew").unlink()
    result = shell.unattended()
    assert result.returncode != 0 and "https://brew.sh" in result.stderr
    assert not shell.log.exists()
    assert not shell.record.exists()


def test_child_status_and_arguments_are_preserved(tmp_path):
    shell = Shell(tmp_path)
    shell.ready.touch()
    shell.env["CHILD_STATUS"] = "23"
    result = shell.unattended("--state", str(tmp_path / "private state"), "--reconfigure")
    assert result.returncode == 23
    assert json.loads(shell.record.read_text())["args"][-3:] == ["--state", str(tmp_path / "private state"), "--reconfigure"]
    assert not shell.log.exists()


@pytest.mark.parametrize("version,bootstrap", [("3,10,0", True), ("3,11,0", False), ("3,13,0", False), ("3,14,0", True)])
def test_runtime_compatibility_probe_checks_both_bounds(tmp_path, version, bootstrap):
    shell = Shell(tmp_path)
    probe = f"import sys; sys.version_info=({version}); exec(sys.argv[1])"
    shell.script("python3", 'if [[ ${1:-} == -c ]]; then exec ' + shlex.quote(sys.executable)
                 + ' -c ' + shlex.quote(probe) + ' "$2"; else exec ' + shlex.quote(sys.executable) + ' "$@"; fi')
    result = shell.unattended()
    assert result.returncode == 0, result.stderr
    assert shell.log.exists() is bootstrap


def test_current_source_export_includes_new_bootstrap():
    from setup_export import setup_files
    files = setup_files(ROOT)
    assert all(name in files for name in ("scripts/setup_bootstrap.sh", "scripts/setup-plan.txt", "secondbrain.sh"))


def test_redirected_stdin_uses_controlling_terminal(tmp_path):
    shell = Shell(tmp_path)
    shell.ready.touch()
    pid, master = pty.fork()
    if pid == 0:
        os.close(0)
        os.open(os.devnull, os.O_RDONLY)
        os.execve("/bin/bash", ["bash", str(shell.root / "secondbrain.sh"), "setup"], shell.env)
    deadline = time.monotonic() + 10
    status = None
    output = b""
    try:
        while time.monotonic() < deadline:
            selected, _, _ = select.select([master], [], [], 0.1)
            if selected:
                try:
                    output += os.read(master, 4096)
                except OSError:
                    pass
            finished, status = os.waitpid(pid, os.WNOHANG)
            if finished:
                break
        else:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            pytest.fail("Terminal handoff blocked")
        assert os.waitstatus_to_exitcode(status) == 0, output.decode(errors="replace")
        assert json.loads(shell.record.read_text())["tty"] is True
    finally:
        os.close(master)


def test_public_aliases_reach_real_plan(tmp_path):
    for entry in ("secondbrain.sh", "install.sh"):
        result = subprocess.run([str(ROOT / entry), "setup", "--dry-run", "--no-prompt"],
                                env={**os.environ, "HOME":str(tmp_path)}, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert "ALL" in result.stdout and "verification" in result.stdout.lower()
    assert list(tmp_path.iterdir()) == []


def test_journal_summarizes_verified_and_incomplete_work(tmp_path, capsys):
    from setup_support import Journal, SetupError
    journal = Journal(tmp_path)
    journal.phase("installed", lambda: "Installed")
    def failed():
        raise SetupError("Login still needed")
    journal.phase("login", failed)
    journal.phase("dependent", lambda: pytest.fail("Must not execute"), requires=("login",))
    assert journal.finish() is True
    data = json.loads((tmp_path / "setup-status.json").read_text())
    assert data["status"] == "incomplete"
    assert data["phases"]["dependent"]["status"] == "pending"
    output = capsys.readouterr().out
    assert "installed: verified" in output
    assert "login" in output and "dependent" in output


def test_download_policy_and_unattended_sudo(monkeypatch, tmp_path):
    import setup_support as support
    calls = []
    monkeypatch.setattr(support.subprocess, "run", lambda args, **kwargs: calls.append((args, kwargs)) or subprocess.CompletedProcess(args, 0))
    support.download("https://example.org/archive", tmp_path / "archive")
    args, _ = calls.pop()
    assert all(flag in args for flag in ("--connect-timeout", "--max-time", "--retry-max-time", "--proto-redir"))
    for flag in ("--connect-timeout", "--max-time", "--retry-max-time"):
        assert 0 < int(args[args.index(flag) + 1]) <= 600
    support.command(["sudo", "loginctl", "enable-linger", "123"], env={"SECOND_BRAIN_NO_PROMPT":"1"})
    args, kwargs = calls.pop()
    assert args[:2] == ["sudo", "-n"]
    assert kwargs["stdin"] == subprocess.DEVNULL
