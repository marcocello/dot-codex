from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE = (
    REPO_ROOT
    / "skills/second-brain-capture-interactions/scripts/capture_interactions.py"
)


def run(*command: str, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)


def initialize_repository(repo: Path, worktree: Path) -> None:
    run("git", "init", "-q", str(repo))
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    run("git", "-C", str(repo), "add", "README.md")
    run(
        "git",
        "-C",
        str(repo),
        "-c",
        "user.name=Capture Proof",
        "-c",
        "user.email=capture@example.invalid",
        "commit",
        "-qm",
        "fixture",
    )
    run("git", "-C", str(repo), "worktree", "add", "--detach", str(worktree))


def write_session(
    path: Path,
    task_id: str,
    cwd: Path,
    completed_messages: list[tuple[str, str]],
    incomplete_message: str | None = None,
) -> None:
    events: list[dict[str, object]] = [
        {
            "timestamp": "2026-07-28T00:00:00Z",
            "type": "session_meta",
            "payload": {
                "id": task_id,
                "cwd": str(cwd),
                "originator": "Codex Desktop",
                "source": "vscode",
            },
        }
    ]
    for number, (user_text, assistant_text) in enumerate(completed_messages, start=1):
        events.extend(
            [
                {
                    "type": "event_msg",
                    "payload": {"type": "task_started", "turn_id": f"turn-{number}"},
                },
                {
                    "type": "event_msg",
                    "payload": {"type": "user_message", "message": user_text},
                },
                {
                    "type": "event_msg",
                    "payload": {
                        "type": "agent_message",
                        "message": assistant_text,
                        "phase": "final_answer",
                    },
                },
                {"type": "event_msg", "payload": {"type": "task_complete"}},
            ]
        )
    if incomplete_message is not None:
        events.extend(
            [
                {
                    "type": "event_msg",
                    "payload": {"type": "task_started", "turn_id": "turn-in-progress"},
                },
                {
                    "type": "event_msg",
                    "payload": {"type": "user_message", "message": incomplete_message},
                },
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(event) + "\n" for event in events),
        encoding="utf-8",
    )


def write_fake_codex(path: Path) -> None:
    path.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import os
            import sys

            manifest_path = os.environ["FAKE_CODEX_THREADS"]
            for line in sys.stdin:
                request = json.loads(line)
                method = request.get("method")
                if method == "initialize":
                    print(json.dumps({"id": request["id"], "result": {"userAgent": "fake"}}), flush=True)
                elif method == "thread/list":
                    params = request["params"]
                    if params.get("archived") is not False:
                        raise SystemExit("thread/list must request archived=false")
                    if params.get("sourceKinds") != ["vscode"]:
                        raise SystemExit("thread/list must request vscode app chats")
                    threads = json.loads(open(manifest_path, encoding="utf-8").read())
                    cursor = int(params.get("cursor") or 0)
                    page = threads[cursor : cursor + 1]
                    next_cursor = str(cursor + 1) if cursor + 1 < len(threads) else None
                    result = {"data": page, "nextCursor": next_cursor}
                    print(json.dumps({"id": request["id"], "result": result}), flush=True)
            """
        ),
        encoding="utf-8",
    )
    path.chmod(0o755)


def invoke_capture(
    repo: Path, fake_codex: Path, state: Path, manifest: Path
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["FAKE_CODEX_THREADS"] = str(manifest)
    return subprocess.run(
        [
            sys.executable,
            str(CAPTURE),
            "project",
            "--project-root",
            str(repo),
            "--codex-bin",
            str(fake_codex),
            "--workspace-state",
            str(state),
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def seed_stale_record(repo: Path) -> None:
    threads = repo / "docs/interactions/threads"
    threads.mkdir(parents=True)
    (threads / "stale.json").write_text("{}\n", encoding="utf-8")
    (repo / "docs/interactions/index.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "records": [
                    {
                        "task_id": "stale",
                        "path": "threads/stale.json",
                        "state": "complete",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_project_sync_mirrors_visible_chats_updates_and_archives(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    worktree = tmp_path / "worktree"
    initialize_repository(repo, worktree)
    root_session = tmp_path / "sessions/root.jsonl"
    worktree_session = tmp_path / "sessions/worktree.jsonl"
    root_id = "root-chat"
    worktree_id = "worktree-chat"
    write_session(root_session, root_id, repo, [("root question", "root answer")])
    write_session(
        worktree_session,
        worktree_id,
        worktree,
        [("worktree question", "worktree answer")],
    )

    manifest = tmp_path / "visible.json"
    manifest.write_text(
        json.dumps(
            [
                {"id": root_id, "cwd": str(repo), "path": str(root_session)},
                {
                    "id": worktree_id,
                    "cwd": str(worktree),
                    "path": str(worktree_session),
                },
            ]
        ),
        encoding="utf-8",
    )
    state = tmp_path / "app-state.json"
    state.write_text(
        json.dumps({"thread-workspace-root-hints": {worktree_id: str(repo)}}),
        encoding="utf-8",
    )
    fake_codex = tmp_path / "codex"
    write_fake_codex(fake_codex)
    seed_stale_record(repo)

    initial = invoke_capture(repo, fake_codex, state, manifest)
    assert initial.returncode == 0, (initial.stdout, initial.stderr)
    assert "captured=2" in initial.stdout
    assert "removed=1" in initial.stdout
    index_path = repo / "docs/interactions/index.json"
    initial_index = json.loads(index_path.read_text(encoding="utf-8"))
    assert [record["task_id"] for record in initial_index["records"]] == [
        root_id,
        worktree_id,
    ]
    record_files = sorted(
        path.name for path in (repo / "docs/interactions/threads").glob("*.json")
    )
    assert record_files == [f"{root_id}.json", f"{worktree_id}.json"]

    write_session(
        root_session,
        root_id,
        repo,
        [("root question", "root answer"), ("new question", "new answer")],
        incomplete_message="do not capture this turn yet",
    )
    manifest.write_text(
        json.dumps([{"id": root_id, "cwd": str(repo), "path": str(root_session)}]),
        encoding="utf-8",
    )

    updated = invoke_capture(repo, fake_codex, state, manifest)
    assert updated.returncode == 0, (updated.stdout, updated.stderr)
    assert "updated=1" in updated.stdout
    assert "removed=1" in updated.stdout
    final_index = json.loads(index_path.read_text(encoding="utf-8"))
    assert [record["task_id"] for record in final_index["records"]] == [root_id]
    root_record = json.loads(
        (repo / f"docs/interactions/threads/{root_id}.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(root_record["turns"]) == 2
    assert root_record["capture"]["state"] == "partial"
    assert root_record["capture"]["incomplete_turn_ids"] == ["turn-in-progress"]
    assert not (repo / f"docs/interactions/threads/{worktree_id}.json").exists()
    assert not (repo / "interactions").exists()
