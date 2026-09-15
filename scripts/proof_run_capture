#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import signal
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import FrameType
from typing import Any


class CaptureSignal(Exception):
    def __init__(self, signum: int) -> None:
        self.signum = signum


def positive_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be positive") from exc
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be finite and positive")
    return seconds


def nonempty_note(value: str) -> str:
    note = value.strip()
    if not note:
        raise argparse.ArgumentTypeError("note must not be empty")
    return note


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Capture an official feature proof or a regression command in a contained "
            "process group, retaining separate execution evidence."
        ),
        epilog=(
            "Output: prints the retained attempt directory. Exit status: runner status; "
            "2 for invalid input, 124 for timeout, 125 for cleanup failure, or 128+signal "
            "for interruption; 126 when a would-be passing runner changes accepted proof inputs."
        ),
    )
    parser.add_argument(
        "--feature-dir",
        required=True,
        type=Path,
        help="Feature directory containing FEATURE.md and PROOF.md; proof mode also requires proof/run.sh.",
    )
    parser.add_argument(
        "--timeout-seconds",
        required=True,
        type=positive_seconds,
        help="Finite positive wall-clock limit for the complete command.",
    )
    parser.add_argument(
        "--note",
        required=True,
        type=nonempty_note,
        help="Non-empty reason retained with this attempt.",
    )
    parser.add_argument("--kind", choices=("proof", "regression"), default="proof")
    parser.add_argument("--cwd", type=Path, help="Regression working directory within the repository; defaults to its root.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Regression command and arguments after --; executed without an implicit shell.")
    args = parser.parse_args()
    if args.command[:1] == ["--"]:
        args.command = args.command[1:]
    if args.kind == "proof" and (args.command or args.cwd is not None):
        parser.error("proof mode uses proof/run.sh from the repository root; command and --cwd are regression-only")
    if args.kind == "regression" and (not args.command or not args.command[0].strip()):
        parser.error("regression mode requires a command after --")
    return args


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def repository_root(cwd: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else cwd.resolve()


def resolves_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except (OSError, ValueError):
        return False
    return True


def uses_symlink(path: Path) -> bool:
    try:
        return path.absolute() != path.resolve()
    except OSError:
        return True


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def runtime_context() -> dict[str, str]:
    return {
        "capture_python": sys.version.split()[0],
        "capture_python_executable": sys.executable,
        "machine": platform.machine(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "shell": os.environ.get("SHELL", ""),
    }


def process_group_exists(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return False
    return True


def wait_for_group_exit(pgid: int, seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while process_group_exists(pgid) and time.monotonic() < deadline:
        time.sleep(0.02)
    return not process_group_exists(pgid)


def cleanup_process_group(pgid: int) -> dict[str, bool | str]:
    cleanup: dict[str, bool | str] = {
        "kill_sent": False,
        "status": "clear",
        "term_sent": False,
    }
    if not process_group_exists(pgid):
        return cleanup

    cleanup["term_sent"] = True
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return cleanup
    except PermissionError:
        cleanup["status"] = "denied"
        return cleanup
    if wait_for_group_exit(pgid, 1):
        cleanup["status"] = "terminated"
        return cleanup

    cleanup["kill_sent"] = True
    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        cleanup["status"] = "terminated"
        return cleanup
    except PermissionError:
        cleanup["status"] = "denied"
        return cleanup
    cleanup["status"] = "killed" if wait_for_group_exit(pgid, 1) else "remaining"
    return cleanup


def signal_handler(signum: int, _frame: FrameType | None) -> None:
    raise CaptureSignal(signum)


def install_signal_handlers() -> dict[int, Any]:
    watched = (signal.SIGHUP, signal.SIGTERM, signal.SIGQUIT)
    previous = {signum: signal.getsignal(signum) for signum in watched}
    for signum in watched:
        signal.signal(signum, signal_handler)
    return previous


def restore_signal_handlers(previous: dict[int, Any]) -> None:
    for signum, handler in previous.items():
        signal.signal(signum, handler)


FileState = tuple[bytes, int, int, int]
InputBaselines = dict[str, tuple[FileState, FileState]]


def file_state(path: Path) -> FileState:
    with path.open("rb") as handle:
        content = handle.read()
        stat = os.fstat(handle.fileno())
    return content, stat.st_mode & 0o777, stat.st_ino, stat.st_ctime_ns


def capture_input_baselines(
    run_dir: Path, inputs: tuple[tuple[str, Path], ...]
) -> InputBaselines:
    return {
        label: (file_state(current), file_state(run_dir / label))
        for label, current in inputs
    }


def changed_proof_inputs(
    run_dir: Path,
    inputs: tuple[tuple[str, Path], ...],
    baselines: InputBaselines,
) -> list[str]:
    changed: list[str] = []
    for label, current in inputs:
        retained = run_dir / label
        try:
            if file_state(current) != baselines[label][0]:
                changed.append(label)
        except OSError:
            changed.append(label)
        try:
            if file_state(retained) != baselines[label][1]:
                changed.append(f"retained/{label}")
        except OSError:
            changed.append(f"retained/{label}")
    return changed


def main() -> int:
    args = parse_args()
    root = repository_root(Path.cwd())
    unresolved_feature = (
        args.feature_dir if args.feature_dir.is_absolute() else root / args.feature_dir
    )
    feature_dir = unresolved_feature.resolve()
    try:
        feature_dir.relative_to(root)
    except ValueError:
        print("proof_run_capture: feature directory escapes repository root", file=sys.stderr)
        return 2
    if uses_symlink(unresolved_feature):
        print("proof_run_capture: feature directory must not use symlinks", file=sys.stderr)
        return 2

    cwd = root
    if args.cwd is not None:
        requested_cwd = args.cwd if args.cwd.is_absolute() else root / args.cwd
        if not requested_cwd.is_dir() or not resolves_within(requested_cwd, root) or uses_symlink(requested_cwd):
            print("proof_run_capture: cwd must be an existing non-symlink directory within the repository", file=sys.stderr)
            return 2
        cwd = requested_cwd.resolve()

    feature = feature_dir / "FEATURE.md"
    proof = feature_dir / "PROOF.md"
    runner = feature_dir / "proof" / "run.sh"
    inputs = (("FEATURE.md", feature), ("PROOF.md", proof))
    if args.kind == "proof":
        inputs += (("run.sh", runner),)
    for label, path in inputs:
        if not path.is_file():
            print(f"proof_run_capture: missing {label}: {path}", file=sys.stderr)
            return 2
        if not resolves_within(path, root):
            print(
                f"proof_run_capture: proof input escapes repository root: {label}",
                file=sys.stderr,
            )
            return 2
        if uses_symlink(path):
            print(
                f"proof_run_capture: proof input must not use symlinks: {label}",
                file=sys.stderr,
            )
            return 2
    if args.kind == "proof" and not runner.stat().st_mode & 0o111:
        print(f"proof_run_capture: runner not executable: {runner}", file=sys.stderr)
        return 2

    evidence_area = "proof" if args.kind == "proof" else "tests"
    unresolved_attempt_base = feature_dir / evidence_area / "runs"
    attempt_base = unresolved_attempt_base.resolve()
    if not resolves_within(attempt_base, root):
        print("proof_run_capture: attempt directory escapes repository root", file=sys.stderr)
        return 2
    if uses_symlink(unresolved_attempt_base):
        print("proof_run_capture: attempt directory must not use symlinks", file=sys.stderr)
        return 2
    run_dir = attempt_base / timestamp()
    run_dir.mkdir(parents=True)
    command = [runner.relative_to(root).as_posix()] if args.kind == "proof" else args.command
    started_at = now()
    started_clock = time.monotonic()
    execution: dict[str, Any] = {
        "capture_pid": os.getpid(),
        "kind": args.kind,
        "command": command,
        "cwd": str(cwd),
        "runtime": runtime_context(),
        "started_at": started_at,
        "timeout_seconds": args.timeout_seconds,
    }
    write_json(run_dir / "attempt-start.json", {**execution, "status": "STARTED"})
    for label, path in inputs:
        shutil.copy2(path, run_dir / label)
    (run_dir / "notes.md").write_text(args.note + "\n", encoding="utf-8")
    input_baselines = capture_input_baselines(run_dir, inputs)

    stdout_path = run_dir / "stdout.txt"
    stderr_path = run_dir / "stderr.txt"
    process: subprocess.Popen[bytes] | None = None
    runner_returncode: int | None = None
    final_returncode = 126
    status = "FAIL"
    interrupted_signal: int | None = None
    cleanup: dict[str, bool | str] = {
        "kill_sent": False,
        "status": "not_started",
        "term_sent": False,
    }

    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        previous_handlers = install_signal_handlers()
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
            )
            execution["runner_pid"] = process.pid
            execution["runner_pgid"] = process.pid
            write_json(run_dir / "attempt-start.json", {**execution, "status": "STARTED"})
            try:
                runner_returncode = process.wait(timeout=args.timeout_seconds)
            except subprocess.TimeoutExpired:
                status = "TIMEOUT"
                final_returncode = 124
                stderr.write(
                    f"proof_run_capture: timed out after {args.timeout_seconds:g} seconds\n".encode()
                )
            except KeyboardInterrupt:
                interrupted_signal = signal.SIGINT
            except CaptureSignal as exc:
                interrupted_signal = exc.signum
        except OSError as exc:
            stderr.write(f"proof_run_capture: cannot execute runner: {exc}\n".encode())
        finally:
            restore_signal_handlers(previous_handlers)
            if process is not None:
                cleanup = cleanup_process_group(process.pid)
                if process.poll() is None:
                    try:
                        runner_returncode = process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        cleanup["status"] = "remaining"

        if interrupted_signal is not None:
            status = "INTERRUPTED"
            final_returncode = 128 + interrupted_signal
            stderr.write(
                f"proof_run_capture: interrupted by signal {interrupted_signal}\n".encode()
            )
        elif status != "TIMEOUT" and runner_returncode is not None:
            if runner_returncode == 0:
                status = "PASS"
                final_returncode = 0
            elif runner_returncode < 0:
                interrupted_signal = abs(runner_returncode)
                status = "INTERRUPTED"
                final_returncode = 128 + interrupted_signal
            else:
                status = "FAIL"
                final_returncode = runner_returncode

        if cleanup["status"] in {"denied", "remaining"}:
            status = "FAIL"
            final_returncode = 125
            stderr.write(b"proof_run_capture: process group cleanup failed\n")

    input_changes = changed_proof_inputs(run_dir, inputs, input_baselines)
    if input_changes:
        with stderr_path.open("ab") as stderr:
            stderr.write(
                (
                    "proof_run_capture: proof input changed during run: "
                    + ", ".join(input_changes)
                    + "\n"
                ).encode()
            )
        if status == "PASS":
            status = "FAIL"
            final_returncode = 126

    result: dict[str, Any] = {
        **execution,
        "cleanup": cleanup,
        "duration_seconds": round(time.monotonic() - started_clock, 6),
        "ended_at": now(),
        "returncode": final_returncode,
        "runner_returncode": runner_returncode,
        "status": status,
    }
    if interrupted_signal is not None:
        result["signal"] = interrupted_signal
    if input_changes:
        result["input_changes"] = input_changes
    write_json(run_dir / "result.json", result)
    print(f"proof_run_capture: {run_dir}")
    return final_returncode


if __name__ == "__main__":
    sys.exit(main())
