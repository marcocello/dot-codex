"""Read native skill metadata from the activated assistant profile; no model turn."""
from pathlib import Path
import os
import shutil

from telegram_to_agents.cli.codex_appserver_bridge import AppServer

ROOT = Path(__file__).resolve().parents[4]
BRAIN = Path(os.environ.get("SECOND_BRAIN_REPO", str(ROOT.parent / "secondbrain")))
STATE = Path(os.environ.get("SECOND_BRAIN_STATE", str(Path.home() / "projects/.secondbrain")))
os.environ["CODEX_HOME"] = str(STATE / "codex")
assert (STATE / "codex/.secondbrain-profile.json").is_file()

with AppServer(Path(shutil.which("codex")), transport="stdio", timeout_seconds=20) as server:
    result = server.request("skills/list", {"cwds": [str(STATE / "workspace")], "forceReload": True})
    groups = result.get("data", [])
    skills = [skill for group in groups for skill in group.get("skills", [])]
    errors = [error for group in groups for error in group.get("errors", [])]
    required = ["secondbrain-update", "secondbrain-review", "knowledge-capture", "knowledge-tool-connect"]
    found = {
        name: any(skill["name"] == name and Path(skill["path"]).resolve().is_relative_to((BRAIN / "skills").resolve()) for skill in skills)
        for name in required
    }
    print("Native discovery from secondbrain source:", found)
    print("Discovery errors:", len(errors))
    assert all(found.values()) and not errors
