from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "scripts/proof_run_capture"
PROOF_INPUTS = (
    ("FEATURE.md", "docs/features/example/FEATURE.md", "FEATURE.md"),
    ("PROOF.md", "docs/features/example/PROOF.md", "PROOF.md"),
    ("run.sh", "docs/features/example/proof/run.sh", "run.sh"),
)


def make_feature(tmp_path: Path, runner_body: str) -> tuple[Path, Path]:
    repository = tmp_path / "repository"
    feature_dir = repository / "docs/features/example"
    proof_dir = feature_dir / "proof"
    proof_dir.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    (feature_dir / "FEATURE.md").write_text("# Feature\n", encoding="utf-8")
    (feature_dir / "PROOF.md").write_text("# Proof\n", encoding="utf-8")
    runner = proof_dir / "run.sh"
    runner.write_text(f"#!/bin/sh\nset -eu\n{runner_body}\n", encoding="utf-8")
    runner.chmod(0o755)
    return repository, feature_dir


def run_capture(repository: Path, timeout: str = "3") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(CAPTURE),
            "--feature-dir",
            "docs/features/example",
            "--timeout-seconds",
            timeout,
            "--note",
            "test attempt",
        ],
        cwd=repository,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )


def newest_attempt(feature_dir: Path) -> Path:
    attempts = sorted((feature_dir / "proof/runs").iterdir())
    assert attempts
    return attempts[-1]


def read_result(feature_dir: Path) -> tuple[Path, dict[str, object]]:
    attempt = newest_attempt(feature_dir)
    return attempt, json.loads((attempt / "result.json").read_text(encoding="utf-8"))


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def wait_for_process_exit(pid: int) -> bool:
    deadline = time.monotonic() + 2
    while process_exists(pid) and time.monotonic() < deadline:
        time.sleep(0.02)
    return not process_exists(pid)


def test_pass_captures_output_result_and_pre_run_inputs(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "printf 'observable output\\n'")

    completed = run_capture(repository)

    attempt, result = read_result(feature_dir)
    started = json.loads((attempt / "attempt-start.json").read_text(encoding="utf-8"))
    assert completed.returncode == 0
    assert started["status"] == "STARTED"
    assert started["runner_pid"] == result["runner_pid"]
    assert result["status"] == "PASS"
    assert result["runner_returncode"] == 0
    assert (attempt / "stdout.txt").read_text(encoding="utf-8") == "observable output\n"
    assert (attempt / "FEATURE.md").read_text(encoding="utf-8") == "# Feature\n"
    assert (attempt / "PROOF.md").read_text(encoding="utf-8") == "# Proof\n"
    assert (attempt / "run.sh").read_text(encoding="utf-8").endswith(
        "printf 'observable output\\n'\n"
    )


def test_failure_preserves_runner_return_code(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "printf 'failed evidence\\n' >&2\nexit 7")

    completed = run_capture(repository)

    attempt, result = read_result(feature_dir)
    assert completed.returncode == 7
    assert result["status"] == "FAIL"
    assert result["returncode"] == 7
    assert result["runner_returncode"] == 7
    assert "failed evidence" in (attempt / "stderr.txt").read_text(encoding="utf-8")


def test_timeout_kills_the_runner_process_group(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        "sleep 30 &\nchild=$!\nprintf '%s\\n' \"$child\" > child.pid\nwait \"$child\"",
    )

    completed = run_capture(repository, timeout="0.1")

    attempt, result = read_result(feature_dir)
    child_pid = int((repository / "child.pid").read_text(encoding="utf-8").strip())
    assert completed.returncode == 124
    assert result["status"] == "TIMEOUT"
    assert result["cleanup"]["status"] not in {"denied", "remaining"}
    assert wait_for_process_exit(child_pid)
    assert "timed out" in (attempt / "stderr.txt").read_text(encoding="utf-8")


def test_successful_runner_cleans_up_orphan_child(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        "sleep 30 &\nchild=$!\nprintf '%s\\n' \"$child\" > child.pid\nexit 0",
    )

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    child_pid = int((repository / "child.pid").read_text(encoding="utf-8").strip())
    assert completed.returncode == 0
    assert result["status"] == "PASS"
    assert result["cleanup"]["status"] not in {"denied", "remaining"}
    assert wait_for_process_exit(child_pid)


def test_sigterm_retains_interrupted_result_and_cleans_up(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "printf '%s\\n' \"$$\" > runner.pid\nsleep 30")
    process = subprocess.Popen(
        [
            str(CAPTURE),
            "--feature-dir",
            "docs/features/example",
            "--timeout-seconds",
            "10",
            "--note",
            "interrupt attempt",
        ],
        cwd=repository,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 3
    while not (repository / "runner.pid").exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert (repository / "runner.pid").exists()

    process.send_signal(signal.SIGTERM)
    stdout, stderr = process.communicate(timeout=5)

    attempt, result = read_result(feature_dir)
    runner_pid = int((repository / "runner.pid").read_text(encoding="utf-8").strip())
    assert process.returncode == 128 + signal.SIGTERM
    assert result["status"] == "INTERRUPTED"
    assert result["signal"] == signal.SIGTERM
    assert result["cleanup"]["status"] not in {"denied", "remaining"}
    assert wait_for_process_exit(runner_pid)
    assert stderr == ""
    assert "interrupted by signal" in (attempt / "stderr.txt").read_text(encoding="utf-8")
    assert "proof_run_capture:" in stdout


def test_rejects_feature_path_outside_repository(tmp_path: Path) -> None:
    repository, _ = make_feature(tmp_path, "exit 0")

    completed = subprocess.run(
        [
            str(CAPTURE),
            "--feature-dir",
            "../outside",
            "--timeout-seconds",
            "1",
            "--note",
            "invalid attempt",
        ],
        cwd=repository,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "escapes repository root" in completed.stderr


def test_rejects_non_executable_runner_without_attempt(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "exit 0")
    (feature_dir / "proof/run.sh").chmod(0o644)

    completed = run_capture(repository)

    assert completed.returncode == 2
    assert "runner not executable" in completed.stderr
    assert not (feature_dir / "proof/runs").exists()


def test_rejects_missing_runner_without_attempt(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "exit 0")
    (feature_dir / "proof/run.sh").unlink()

    completed = run_capture(repository)

    assert completed.returncode == 2
    assert "missing proof/run.sh" in completed.stderr
    assert not (feature_dir / "proof/runs").exists()


def test_rejects_symlinked_runner_outside_repository_without_attempt(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "exit 0")
    outside_runner = tmp_path / "outside-runner.sh"
    outside_runner.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    outside_runner.chmod(0o755)
    runner = feature_dir / "proof/run.sh"
    runner.unlink()
    runner.symlink_to(outside_runner)

    completed = run_capture(repository)

    assert completed.returncode == 2
    assert "proof input escapes repository root: proof/run.sh" in completed.stderr
    assert not (feature_dir / "proof/runs").exists()


def test_rejects_symlinked_attempt_base_outside_repository_without_write(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "exit 0")
    outside_runs = tmp_path / "outside-runs"
    outside_runs.mkdir()
    runs = feature_dir / "proof/runs"
    runs.symlink_to(outside_runs, target_is_directory=True)

    completed = run_capture(repository)

    assert completed.returncode == 2
    assert "attempt directory escapes repository root" in completed.stderr
    assert list(outside_runs.iterdir()) == []


def test_rejects_in_repository_symlinked_proof_input_without_attempt(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "exit 0")
    target = repository / "feature-contract.md"
    target.write_text("# Feature\n", encoding="utf-8")
    feature = feature_dir / "FEATURE.md"
    feature.unlink()
    feature.symlink_to(target)

    completed = run_capture(repository)

    assert completed.returncode == 2
    assert "proof input must not use symlinks: FEATURE.md" in completed.stderr
    assert not (feature_dir / "proof/runs").exists()


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_mutated_proof_input_turns_would_be_pass_into_capture_failure(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        f"printf '# Changed\\n' > {live_path}",
    )

    completed = run_capture(repository)

    attempt, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["returncode"] == 126
    assert result["runner_returncode"] == 0
    assert result["input_changes"] == [result_label]
    assert f"proof input changed during run: {result_label}" in (
        attempt / "stderr.txt"
    ).read_text(encoding="utf-8")
    assert (attempt / retained_name).read_text(encoding="utf-8") != "# Changed\n"


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_mutating_live_and_retained_inputs_cannot_manufacture_pass(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        "attempt=$(find docs/features/example/proof/runs -mindepth 1 -maxdepth 1 -type d | sort | tail -1)\n"
        f"printf '# Changed\\n' > \"$attempt/{retained_name}\"; "
        f"printf '# Changed\\n' > {live_path}",
    )

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["input_changes"] == [result_label, f"retained/{result_label}"]


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_change_then_restore_of_proof_input_cannot_manufacture_pass(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        f"cp {live_path} original-input; "
        f"printf '# Temporary change\\n' > {live_path}; "
        f"cp original-input {live_path}; rm original-input",
    )

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["input_changes"] == [result_label]


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_mode_only_mutation_of_proof_input_cannot_manufacture_pass(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(tmp_path, f"chmod 600 {live_path}")

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["input_changes"] == [result_label]


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_inode_replacement_of_proof_input_cannot_manufacture_pass(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        f"cp -p {live_path} replacement-input; mv replacement-input {live_path}",
    )

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["input_changes"] == [result_label]


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_change_then_restore_of_retained_input_cannot_manufacture_pass(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        "attempt=$(find docs/features/example/proof/runs -mindepth 1 -maxdepth 1 -type d | sort | tail -1); "
        f"cp \"$attempt/{retained_name}\" original-retained; "
        f"printf '# Temporary change\\n' > \"$attempt/{retained_name}\"; "
        f"cp original-retained \"$attempt/{retained_name}\"; rm original-retained",
    )

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["input_changes"] == [f"retained/{result_label}"]


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_mode_only_mutation_of_retained_input_cannot_manufacture_pass(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        "attempt=$(find docs/features/example/proof/runs -mindepth 1 -maxdepth 1 -type d | sort | tail -1); "
        f"chmod 600 \"$attempt/{retained_name}\"",
    )

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["input_changes"] == [f"retained/{result_label}"]


@pytest.mark.parametrize(("result_label", "live_path", "retained_name"), PROOF_INPUTS)
def test_inode_replacement_of_retained_input_cannot_manufacture_pass(
    tmp_path: Path, result_label: str, live_path: str, retained_name: str
) -> None:
    repository, feature_dir = make_feature(
        tmp_path,
        "attempt=$(find docs/features/example/proof/runs -mindepth 1 -maxdepth 1 -type d | sort | tail -1); "
        f"cp -p \"$attempt/{retained_name}\" retained-replacement; "
        f"mv retained-replacement \"$attempt/{retained_name}\"",
    )

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 126
    assert result["status"] == "FAIL"
    assert result["input_changes"] == [f"retained/{result_label}"]


def test_runner_signal_is_retained_as_interruption_evidence(tmp_path: Path) -> None:
    repository, feature_dir = make_feature(tmp_path, "kill -TERM $$")

    completed = run_capture(repository)

    _, result = read_result(feature_dir)
    assert completed.returncode == 128 + signal.SIGTERM
    assert result["status"] == "INTERRUPTED"
    assert result["runner_returncode"] == -signal.SIGTERM
    assert result["signal"] == signal.SIGTERM
