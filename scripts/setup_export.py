"""Export the reviewed checkout, excluding ignored runtime and credentials."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

from setup_support import SetupError, command, save_json

# Only bundled surfaces of this refactor supplement Git-owned files during review.
SUPPLEMENT = ["secondbrain.sh", "context.template.toml", "scripts/secondbrain_platform.py", "scripts/codex-vm.sh",
              "scripts/setup_*.py", "scripts/setup_bootstrap.sh", "scripts/setup-plan.txt",
              "backend/context", "backend/telegram", "backend/whatsapp", "deployments/prod",
              "docs/harness/secondbrain-platform.md", "docs/harness/component-imports.json"]


def setup_files(root):
    tracked = command(["git", "-C", root, "ls-files", "-z", "--cached"], capture=True).stdout.split("\0")
    extras = command(["git", "-C", root, "ls-files", "-z", "--others", "--exclude-standard", "--", *SUPPLEMENT], capture=True).stdout.split("\0")
    return sorted(set(filter(None, [*tracked, *extras])))


def bundle(root, directory):
    files = setup_files(root)
    git_bundle = directory / "source.bundle"
    command(["git", "-C", root, "bundle", "create", git_bundle, "HEAD"], capture=True)
    manifest = {}
    archive = directory / "source.tar.gz"
    with tarfile.open(archive, "w:gz") as output:
        output.add(git_bundle, arcname="source.bundle")
        for name in files:
            source = root / name
            if source.is_symlink():
                raise SetupError(f"Review source symlink before exporting: {name}")
            original = subprocess.run(["git", "-C", str(root), "show", "HEAD:" + name], capture_output=True)
            if not source.is_file():
                if not source.exists() and not original.returncode:
                    manifest[name] = {"sha256":None, "base":hashlib.sha256(original.stdout).hexdigest()}
                continue
            manifest[name] = {"sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                              "base": hashlib.sha256(original.stdout).hexdigest() if not original.returncode else None}
            output.add(source, arcname="files/" + name)
        path = directory / "manifest.json"
        save_json(path, manifest)
        output.add(path, arcname="manifest.json")
    archive.chmod(0o600)
    return archive


# Executed by Python 3.12 on the remote Ubuntu VM. It receives no credentials.
APPLY = r'''
import fcntl, hashlib, json, os, pathlib, shutil, subprocess, sys, tarfile, tempfile
archive, destination, origin, receipt = sys.argv[1:]
archive, destination, receipt = map(pathlib.Path, (archive, destination, receipt))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(path):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise SystemExit("Refusing a source destination through symlinks")
safe(destination)
safe(receipt)
receipt.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
lock_fd = os.open(receipt.parent / "setup.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit("Remote setup is active; source files were not changed")
with tempfile.TemporaryDirectory(prefix="secondbrain-source-") as tmp:
    tmp = pathlib.Path(tmp)
    with tarfile.open(archive) as source: source.extractall(tmp, filter="data")
    incoming = json.loads((tmp / "manifest.json").read_text())
    previous = json.loads(receipt.read_text()) if receipt.is_file() else {}
    if not destination.exists():
        subprocess.run(["git", "clone", "--quiet", str(tmp / "source.bundle"), str(destination)], check=True)
        subprocess.run(["git", "-C", str(destination), "remote", "set-url", "origin", origin], check=True)
    if not (destination / ".git").is_dir(): raise SystemExit("Existing destination is not a checkout")
    for name, record in incoming.items():
        relative = pathlib.PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts: raise SystemExit("Invalid source member")
        target = destination / name
        safe(target)
        if record["sha256"] is not None and digest(tmp / "files" / name) != record["sha256"]: raise SystemExit("Source checksum mismatch")
        if target.exists() and (not target.is_file() or digest(target) not in {record["sha256"], record["base"], previous.get(name)}):
            raise SystemExit("Remote file has independent changes: " + name)
    for name in incoming:
        target = destination / name
        if incoming[name]["sha256"] is None:
            target.unlink(missing_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tmp / "files" / name, target)
    receipt.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    stage = receipt.with_name(receipt.name + ".tmp")
    stage.write_text(json.dumps({name: row["sha256"] for name, row in incoming.items()}))
    stage.chmod(0o600)
    os.replace(stage, receipt)
'''
