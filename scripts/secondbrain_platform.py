#!/usr/bin/env python3
"""One operator entry point for the bundled harness and second-brain components."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from install_state import InstallError

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"


def run(command, *, cwd=ROOT, env=None, plan=False):
    if plan:
        print(f"cd {shlex.quote(str(cwd))} && {shlex.join(map(str, command))}")
        return 0
    return subprocess.call(list(map(str, command)), cwd=cwd, env=env)


def executable(name):
    path = VENV / "bin" / name
    if not path.is_file():
        raise ValueError(f"{name} is not installed. Run ./secondbrain.sh setup first.")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("setup", "install", "vm", "codex", "context", "telegram", "whatsapp", "doctor"))
    argv = list(sys.argv[1:] if argv is None else argv) or ["setup"]
    args = parser.parse_args(argv[:1])
    rest = argv[1:]
    try:
        if args.command in ("install", "vm"):
            target = ROOT / ("install.sh" if args.command == "install" else "scripts/codex-vm.sh")
            return run([target, *rest])
        if args.command == "codex":
            from setup_tools import load_secrets
            state = Path(os.environ.get("SECOND_BRAIN_STATE", str(Path.home() / "projects/.secondbrain"))).expanduser()
            env = {**os.environ, **load_secrets(state)}
            env["PATH"] = str(VENV / "bin") + os.pathsep + str(Path.home() / ".local/bin") + os.pathsep + env.get("PATH", "")
            binary = Path.home() / ".local/bin/codex"
            return run([binary if binary.is_file() else "codex", *rest], env=env)
        if args.command == "setup":
            if "--component" not in rest and not any(value.startswith("--component=") for value in rest):
                from setup_platform import main as setup_main
                return setup_main(rest)
            setup = argparse.ArgumentParser(prog="secondbrain.sh setup")
            setup.add_argument("--plan", "--dry-run", action="store_true")
            setup.add_argument("--non-interactive", "--no-prompt", action="store_true")
            setup.add_argument("--component", choices=("core", "context", "telegram", "whatsapp", "all"), default="core")
            options = setup.parse_args(rest)
            python_components = [name for name in ("context", "telegram") if options.component in (name, "core", "all")]
            commands = []
            if python_components:
                if not VENV.exists():
                    commands.append(([sys.executable, "-m", "venv", VENV], ROOT))
                elif not (VENV / "bin/python").is_file():
                    raise ValueError("Existing .venv has no Python; inspect it before setup")
                commands.append(([VENV / "bin/python", "-m", "ensurepip", "--upgrade"], ROOT))
                pip = [VENV / "bin/python", "-m", "pip", "install"]
                for name in python_components:
                    pip += ["-e", str(ROOT / "backend" / name)]
                commands.append((pip, ROOT))
            if options.component in ("whatsapp", "all"):
                commands.append((["npm", "ci"], ROOT / "backend/whatsapp"))
            for command, cwd in commands:
                result = run(command, cwd=cwd, plan=options.plan)
                if result:
                    return result
            return 0
        if args.command in ("context", "telegram"):
            binary = "secondbrain-context" if args.command == "context" else "telegram-to-agents"
            return run([executable(binary), *rest])
        if args.command == "whatsapp":
            bot = argparse.ArgumentParser(prog="secondbrain.sh whatsapp")
            bot.add_argument("--plan", action="store_true")
            bot.add_argument("--enable-replies", action="store_true")
            options = bot.parse_args(rest)
            env = dict(os.environ)
            env["WHATSAPP_AUTO_REPLY"] = "1" if options.enable_replies else "0"
            env.setdefault("WHATSAPP_AUTH_DIR", str(Path.home() / "projects/.secondbrain/baileys"))
            if (VENV / "bin/python").exists():
                env.setdefault("WHATSAPP_PYTHON", str(VENV / "bin/python"))
            if options.plan:
                print(f"WHATSAPP_AUTO_REPLY={env['WHATSAPP_AUTO_REPLY']}")
            return run(["npm", "start"], cwd=ROOT / "backend/whatsapp", env=env, plan=options.plan)
        if rest:
            parser.error("doctor takes no arguments; use context doctor --config PATH for source checks")
        missing = False
        for name in ("git", "python3", "node", "npm", "codex", "wacli", "terraform", "az"):
            print(f"{name}: {'available' if shutil.which(name) else 'not installed'}")
        for name in ("secondbrain-context", "telegram-to-agents"):
            installed = (VENV / "bin" / name).is_file()
            print(f"{name}: {'installed in .venv' if installed else 'run ./secondbrain.sh setup'}")
            missing |= not installed
        print("No account, pairing, running service, or live provider connection was checked.")
        return int(missing)
    except (InstallError, ValueError, FileNotFoundError) as error:
        print(f"Secondbrain: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
