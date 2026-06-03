#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_URL = "https://github.com/marcocello/dot-codex"
DEFAULT_BRANCH = "main"
DIRTY_WORKTREE_EXIT = 2


class SyncError(Exception):
    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clone or fast-forward the marcocello/dot-codex checkout."
    )
    parser.add_argument("--repo-dir", help="Path to the dot-codex checkout.")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="Repository URL to pull.")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help="Branch to pull.")
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow Git to pull even when the worktree has local changes.",
    )
    return parser.parse_args()


def git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        command = "git " + " ".join(args)
        raise SyncError(f"{command} failed: {detail}")
    return result


def inferred_repo_from_skill() -> Path | None:
    candidate = Path(__file__).resolve().parents[3]
    if (candidate / ".git").exists():
        return candidate
    return None


def resolve_repo_dir(raw_repo_dir: str | None) -> Path:
    if raw_repo_dir:
        return Path(raw_repo_dir).expanduser().resolve()

    env_repo = os.environ.get("DOT_CODEX_REPO")
    if env_repo:
        return Path(env_repo).expanduser().resolve()

    inferred = inferred_repo_from_skill()
    if inferred:
        return inferred

    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidate = Path(codex_home).expanduser().resolve()
        if (candidate / ".git").exists():
            return candidate

    return (Path.home() / "software" / "marcocello" / "dot-codex").resolve()


def normalize_remote(value: str) -> str:
    normalized = value.strip().removesuffix("/")
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.removeprefix("git@github.com:")
    return normalized.removesuffix(".git").lower()


def same_remote(actual: str, expected: str) -> bool:
    if "://" not in expected and not expected.startswith("git@"):
        try:
            return Path(actual).expanduser().resolve() == Path(expected).expanduser().resolve()
        except OSError:
            return actual == expected
    return normalize_remote(actual) == normalize_remote(expected)


def require_expected_remote(repo_dir: Path, repo_url: str) -> None:
    actual = git(["remote", "get-url", "origin"], repo_dir).stdout.strip()
    if not same_remote(actual, repo_url):
        raise SyncError(
            "origin does not match the requested dot-codex repo:\n"
            f"  origin: {actual}\n"
            f"  expected: {repo_url}"
        )


def require_clean_worktree(repo_dir: Path) -> None:
    status = git(["status", "--porcelain"], repo_dir).stdout.strip()
    if status:
        raise SyncError(
            "local changes prevent pull; commit, stash, or discard them first:\n" + status,
            DIRTY_WORKTREE_EXIT,
        )


def clone_repo(repo_url: str, repo_dir: Path, branch: str) -> None:
    if repo_dir.exists():
        raise SyncError(f"target exists but is not a Git checkout: {repo_dir}")

    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    git(["clone", "--branch", branch, repo_url, str(repo_dir)])
    print(f"cloned {repo_url} into {repo_dir}")


def fast_forward_repo(repo_url: str, repo_dir: Path, branch: str, allow_dirty: bool) -> None:
    if not (repo_dir / ".git").exists():
        raise SyncError(f"target exists but is not a Git checkout: {repo_dir}")

    require_expected_remote(repo_dir, repo_url)
    if not allow_dirty:
        require_clean_worktree(repo_dir)

    before = git(["rev-parse", "--short", "HEAD"], repo_dir).stdout.strip()
    git(["fetch", "origin", branch], repo_dir)
    git(["pull", "--ff-only", "origin", branch], repo_dir)
    after = git(["rev-parse", "--short", "HEAD"], repo_dir).stdout.strip()
    print(f"fast-forwarded {repo_dir} from {before} to {after}")


def main() -> int:
    args = parse_args()
    repo_dir = resolve_repo_dir(args.repo_dir)

    try:
        if repo_dir.exists():
            fast_forward_repo(args.repo_url, repo_dir, args.branch, args.allow_dirty)
        else:
            clone_repo(args.repo_url, repo_dir, args.branch)
    except SyncError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
