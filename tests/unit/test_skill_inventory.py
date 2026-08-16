from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import tomllib


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "skill_inventory.py"


def run_cli(
    manifest: Path,
    skills_root: Path,
    codex_bin: Path,
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT),
        "--manifest",
        str(manifest),
        "--skills-root",
        str(skills_root),
        "--codex-bin",
        str(codex_bin),
        *args,
    ]
    result = subprocess.run(command, text=True, capture_output=True, env=env)
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def make_git_skill(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "source-repo"
    skill = repo / "packages" / "external-skill"
    skill.mkdir(parents=True)
    git(repo, "init")
    git(repo, "config", "user.email", "proof@example.test")
    git(repo, "config", "user.name", "Proof")
    (skill / "SKILL.md").write_text("---\nname: external-skill\ndescription: v1\n---\n")
    git(repo, "add", "packages/external-skill/SKILL.md")
    git(repo, "commit", "-m", "v1")
    revision_one = git(repo, "rev-parse", "HEAD")
    (skill / "SKILL.md").write_text("---\nname: external-skill\ndescription: v2\n---\n")
    git(repo, "commit", "-am", "v2")
    revision_two = git(repo, "rev-parse", "HEAD")
    return repo, revision_one, revision_two


def make_fake_codex(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    binary = tmp_path / "fake-codex"
    state = tmp_path / "plugin-state.json"
    binary.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            import json
            import os
            from pathlib import Path
            import sys

            state_path = Path(os.environ["FAKE_CODEX_STATE"])
            state = json.loads(state_path.read_text()) if state_path.exists() else {}
            args = sys.argv[1:]
            if args == ["plugin", "list", "--json"]:
                installed = [
                    {
                        "pluginId": selector,
                        "version": values["version"],
                        "installed": True,
                        "enabled": values["enabled"],
                    }
                    for selector, values in sorted(state.items())
                ]
                print(json.dumps({"installed": installed, "available": []}))
                raise SystemExit(0)
            if len(args) == 4 and args[:2] == ["plugin", "add"] and args[3] == "--json":
                selector = args[2]
                state[selector] = {"version": "1.2.3", "enabled": True}
                state_path.write_text(json.dumps(state))
                print(json.dumps({"pluginId": selector}))
                raise SystemExit(0)
            if len(args) == 4 and args[:2] == ["plugin", "remove"] and args[3] == "--json":
                selector = args[2]
                state.pop(selector, None)
                state_path.write_text(json.dumps(state))
                print(json.dumps({"pluginId": selector}))
                raise SystemExit(0)
            print(f"unsupported fake codex invocation: {args}", file=sys.stderr)
            raise SystemExit(2)
            """
        )
    )
    binary.chmod(0o755)
    return binary, {**os.environ, "FAKE_CODEX_STATE": str(state)}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def start_http(directory: Path) -> tuple[ThreadingHTTPServer, str]:
    handler = lambda *args, **kwargs: QuietHandler(  # noqa: E731
        *args, directory=str(directory), **kwargs
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}/SKILL.md"


def write_manifest(path: Path, body: str = "") -> None:
    path.write_text(f"schema = 1\n{body}")


def test_sync_bootstraps_current_sources_and_plugin_without_pruning(tmp_path: Path) -> None:
    git(tmp_path, "init")
    skills_root = tmp_path / "skills"
    (skills_root / "owned").mkdir(parents=True)
    (skills_root / "owned" / "SKILL.md").write_text("owned")
    (skills_root / "extra").mkdir()
    (skills_root / "extra" / "SKILL.md").write_text("preserve me")
    source_repo, _, _ = make_git_skill(tmp_path)
    http_root = tmp_path / "http"
    http_root.mkdir()
    http_content = b"---\nname: url-skill\ndescription: pinned\n---\n"
    (http_root / "SKILL.md").write_bytes(http_content)
    server, url = start_http(http_root)
    fake_codex, env = make_fake_codex(tmp_path)
    manifest = tmp_path / "skills.toml"
    write_manifest(
        manifest,
        textwrap.dedent(
            f"""
            [[skills]]
            name = "owned"
            kind = "owned"
            path = "owned"

            [[skills]]
            name = "external-skill"
            kind = "git"
            repository = "{source_repo}"
            source_path = "packages/external-skill"
            path = "external-skill"

            [[skills]]
            name = "url-skill"
            kind = "url"
            url = "{url}"
            sha256 = "{hashlib.sha256(http_content).hexdigest()}"
            path = "url-skill"

            [[skills]]
            name = "demo-plugin"
            kind = "plugin"
            selector = "demo-plugin@test-market"
            enabled = true
            """
        ),
    )
    try:
        first = run_cli(manifest, skills_root, fake_codex, "sync", env=env)
        second = run_cli(manifest, skills_root, fake_codex, "sync", env=env)
        doctor = run_cli(manifest, skills_root, fake_codex, "doctor", env=env)
    finally:
        server.shutdown()
    assert "installed git skill external-skill" in first.stdout
    assert "installed URL skill url-skill" in first.stdout
    assert "installed plugin demo-plugin@test-market" in first.stdout
    assert "already synchronized" in second.stdout
    assert "doctor: healthy" in doctor.stdout
    assert "description: v2" in (skills_root / "external-skill" / "SKILL.md").read_text()
    assert (skills_root / "url-skill" / "SKILL.md").read_bytes() == http_content
    assert (skills_root / "extra" / "SKILL.md").read_text() == "preserve me"
    generated_ignore = (tmp_path / ".gitignore").read_text()
    assert generated_ignore.count("# BEGIN skill_inventory.py managed skills") == 1
    assert "skills/external-skill/" in generated_ignore
    assert "skills/url-skill/" in generated_ignore

    state_path = Path(env["FAKE_CODEX_STATE"])
    state_path.write_text(
        json.dumps({"demo-plugin@test-market": {"version": "9.9.9", "enabled": True}})
    )
    version_change = run_cli(manifest, skills_root, fake_codex, "doctor", env=env)
    assert "doctor: healthy" in version_change.stdout
    state_path.write_text(
        json.dumps({"demo-plugin@test-market": {"version": "1.2.3", "enabled": False}})
    )
    enablement_drift = run_cli(
        manifest, skills_root, fake_codex, "doctor", check=False, env=env
    )
    assert enablement_drift.returncode != 0
    assert "plugin enabled=False, expected True" in enablement_drift.stderr


def test_add_update_remove_and_list_persist_manifest(tmp_path: Path) -> None:
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    source_repo, revision_one, revision_two = make_git_skill(tmp_path)
    git(source_repo, "reset", "--hard", revision_one)
    fake_codex, env = make_fake_codex(tmp_path)
    manifest = tmp_path / "skills.toml"
    write_manifest(manifest)

    run_cli(
        manifest,
        skills_root,
        fake_codex,
        "add",
        "external-skill",
        "--kind",
        "git",
        "--repository",
        str(source_repo),
        "--source-path",
        "packages/external-skill",
        "--path",
        "external-skill",
        env=env,
    )
    assert "description: v1" in (skills_root / "external-skill" / "SKILL.md").read_text()
    git(source_repo, "reset", "--hard", revision_two)
    run_cli(
        manifest,
        skills_root,
        fake_codex,
        "update",
        "external-skill",
        env=env,
    )
    assert "description: v2" in (skills_root / "external-skill" / "SKILL.md").read_text()
    listing = run_cli(manifest, skills_root, fake_codex, "list", env=env)
    assert f"external-skill\tgit\t{source_repo}" in listing.stdout
    run_cli(manifest, skills_root, fake_codex, "remove", "external-skill", env=env)
    assert not (skills_root / "external-skill").exists()
    assert tomllib.loads(manifest.read_text()).get("skills", []) == []

    run_cli(
        manifest,
        skills_root,
        fake_codex,
        "add",
        "demo-plugin",
        "--kind",
        "plugin",
        "--selector",
        "demo-plugin@test-market",
        env=env,
    )
    state_path = Path(env["FAKE_CODEX_STATE"])
    assert "demo-plugin@test-market" in json.loads(state_path.read_text())
    state_path.write_text(
        json.dumps({"demo-plugin@test-market": {"version": "9.9.9", "enabled": True}})
    )
    run_cli(manifest, skills_root, fake_codex, "update", "demo-plugin", env=env)
    assert json.loads(state_path.read_text())["demo-plugin@test-market"]["version"] == "1.2.3"
    manifest_entries = tomllib.loads(manifest.read_text())["skills"]
    assert all("revision" not in entry and "version" not in entry for entry in manifest_entries)
    run_cli(manifest, skills_root, fake_codex, "remove", "demo-plugin", env=env)
    assert json.loads(state_path.read_text()) == {}


def test_invalid_or_unsafe_state_fails_without_overwrite(tmp_path: Path) -> None:
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    fake_codex, env = make_fake_codex(tmp_path)
    manifest = tmp_path / "skills.toml"
    write_manifest(
        manifest,
        """
[[skills]]
name = "bad"
kind = "git"
repository = "https://example.test/repo.git"
revision = "main"
source_path = "skill"
path = "../escape"
""",
    )
    result = run_cli(manifest, skills_root, fake_codex, "doctor", check=False, env=env)
    assert result.returncode != 0
    assert "revision is not allowed in skills.toml" in result.stderr
    assert "safe relative path" in result.stderr

    write_manifest(
        manifest,
        """
[[skills]]
name = "missing-owned"
kind = "owned"
path = "missing-owned"
""",
    )
    result = run_cli(manifest, skills_root, fake_codex, "doctor", check=False, env=env)
    assert result.returncode != 0
    assert "missing-owned/SKILL.md" in result.stderr

    collision = skills_root / "collision"
    collision.mkdir()
    (collision / "SKILL.md").write_text("user content")
    source_repo, _, _ = make_git_skill(tmp_path / "second")
    write_manifest(
        manifest,
        textwrap.dedent(
            f"""
            [[skills]]
            name = "collision"
            kind = "git"
            repository = "{source_repo}"
            source_path = "packages/external-skill"
            path = "collision"
            """
        ),
    )
    result = run_cli(manifest, skills_root, fake_codex, "sync", check=False, env=env)
    assert result.returncode != 0
    assert "refusing to overwrite unmanaged destination" in result.stderr
    assert (collision / "SKILL.md").read_text() == "user content"

    outside_destination = tmp_path / "outside-destination"
    outside_destination.mkdir()
    (skills_root / "linked-parent").symlink_to(outside_destination, target_is_directory=True)
    write_manifest(
        manifest,
        textwrap.dedent(
            f"""
            [[skills]]
            name = "escaped-destination"
            kind = "git"
            repository = "{source_repo}"
            source_path = "packages/external-skill"
            path = "linked-parent/escaped-destination"
            """
        ),
    )
    result = run_cli(manifest, skills_root, fake_codex, "sync", check=False, env=env)
    assert result.returncode != 0
    assert "symlinked destination path" in result.stderr
    assert not (outside_destination / "escaped-destination").exists()

    outside_source = tmp_path / "outside-source"
    outside_source.mkdir()
    (outside_source / "SKILL.md").write_text("outside checkout")
    linked_repo = tmp_path / "linked-source-repo"
    (linked_repo / "packages").mkdir(parents=True)
    git(linked_repo, "init")
    git(linked_repo, "config", "user.email", "proof@example.test")
    git(linked_repo, "config", "user.name", "Proof")
    (linked_repo / "packages" / "linked-skill").symlink_to(
        outside_source, target_is_directory=True
    )
    git(linked_repo, "add", "packages/linked-skill")
    git(linked_repo, "commit", "-m", "linked source")
    write_manifest(
        manifest,
        textwrap.dedent(
            f"""
            [[skills]]
            name = "linked-source"
            kind = "git"
            repository = "{linked_repo}"
            source_path = "packages/linked-skill"
            path = "linked-source"
            """
        ),
    )
    result = run_cli(manifest, skills_root, fake_codex, "sync", check=False, env=env)
    assert result.returncode != 0
    assert "symlinked Git source" in result.stderr
    assert not (skills_root / "linked-source").exists()

    write_manifest(
        manifest,
        """
[[skills]]
name = "floating-plugin"
kind = "plugin"
selector = "floating-plugin@test-market"
version = "latest"
enabled = true
""",
    )
    result = run_cli(manifest, skills_root, fake_codex, "doctor", check=False, env=env)
    assert result.returncode != 0
    assert "version is not allowed in skills.toml" in result.stderr

    write_manifest(
        manifest,
        """
[[skills]]
name = "runtime-system"
kind = "system"
path = ".system/runtime-system"
""",
    )
    result = run_cli(manifest, skills_root, fake_codex, "doctor", check=False, env=env)
    assert result.returncode != 0
    assert "system skills are runtime-managed" in result.stderr

    write_manifest(manifest)
    result = run_cli(
        manifest,
        skills_root,
        fake_codex,
        "add",
        "runtime-system",
        "--kind",
        "system",
        "--path",
        ".system/runtime-system",
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "invalid choice: 'system'" in result.stderr

    result = run_cli(
        manifest,
        skills_root,
        fake_codex,
        "add",
        "documents",
        "--kind",
        "plugin",
        "--selector",
        "documents@openai-primary-runtime",
        check=False,
        env=env,
    )
    assert result.returncode != 0
    assert "openai-primary-runtime plugins are runtime-managed" in result.stderr
    assert tomllib.loads(manifest.read_text()).get("skills", []) == []


def test_repository_manifest_covers_only_user_managed_skills() -> None:
    data = tomllib.loads((ROOT / "skills.toml").read_text())
    assert len(data["skills"]) == 55
    assert all(
        "revision" not in entry and "version" not in entry for entry in data["skills"]
    )
    assert all(entry["kind"] != "system" for entry in data["skills"])
    assert all(
        not entry.get("selector", "").endswith("@openai-primary-runtime")
        for entry in data["skills"]
    )
    entries = {entry["name"]: entry for entry in data["skills"]}
    local_names = {
        path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")
    }
    owned_names = {name for name, entry in entries.items() if entry["kind"] == "owned"}
    raw_external_names = {
        name for name, entry in entries.items() if entry["kind"] in {"git", "url"}
    }
    assert local_names == owned_names | raw_external_names
    for name in raw_external_names:
        skill_file = ROOT / "skills" / entries[name]["path"] / "SKILL.md"
        ignored = subprocess.run(
            ["git", "check-ignore", str(skill_file)], cwd=ROOT, capture_output=True
        )
        assert ignored.returncode == 0, f"external skill is not ignored: {name}"

    assert entries["bento-slides"]["kind"] == "git"
    assert entries["impeccable"]["kind"] == "git"
    assert entries["remotion"]["selector"] == "remotion@openai-curated"
