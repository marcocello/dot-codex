"""Exercise scaffold layout, preservation, setup, rendering, and Git visibility."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/scaffold.py"


class ScaffoldTests(unittest.TestCase):
    def test_generated_root_and_private_setup(self):
        with tempfile.TemporaryDirectory(prefix="scaffold test ") as directory:
            target = Path(directory) / "new project"
            run = subprocess.run(
                [sys.executable, str(SCRIPT), str(target)], capture_output=True
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(
                {path.name for path in target.iterdir()},
                {".vscode", "backend", "frontend", "docs", "deployments", ".gitignore"},
            )
            for relative in (
                "backend/app/main.py",
                "backend/uv.lock",
                "backend/migrations/versions/0001_create_notes.py",
                "frontend/app/package-lock.json",
                "frontend/app/Dockerfile",
                "frontend/app/.dockerignore",
                "docs/README.md",
                "deployments/compose.base.yaml",
                "deployments/dev/compose.yaml",
                "deployments/dev/.env.example",
                "deployments/prod/compose.yaml",
                "deployments/prod/k8s/migrate.json",
                ".vscode/tasks.json",
            ):
                self.assertTrue((target / relative).is_file(), relative)
            self.assertFalse((target / ".venv").exists())
            self.assertFalse((target / "deployments/dev/.env").exists())
            self.assertFalse((target / ".github").exists())

            setup = [sys.executable, str(target / "deployments/setup.py")]
            subprocess.run(setup, check=True, capture_output=True)
            env_path = target / "deployments/dev/.env"
            env = env_path.read_bytes()
            subprocess.run(setup, check=True, capture_output=True)
            self.assertEqual(env_path.read_bytes(), env)
            self.assertEqual(env_path.stat().st_mode & 0o777, 0o600)
            subprocess.run(
                setup + ["--environment", "prod"], check=True, capture_output=True
            )
            prod = (target / "deployments/prod/.env").read_text()
            dev_name = next(
                line
                for line in env.decode().splitlines()
                if line.startswith("COMPOSE_PROJECT_NAME=")
            )
            prod_name = next(
                line
                for line in prod.splitlines()
                if line.startswith("COMPOSE_PROJECT_NAME=")
            )
            self.assertNotEqual(dev_name, prod_name)
            self.assertEqual(
                {path.name for path in target.iterdir()},
                {".vscode", "backend", "frontend", "docs", "deployments", ".gitignore"},
            )

            render_output = Path(directory) / "rendered"
            render = [
                sys.executable,
                str(target / "deployments/render_k8s.py"),
                "--backend-image",
                "registry.example/backend:r1",
                "--web-image",
                "registry.example/web:r1",
                "--domain",
                "app.example.com",
                "--namespace",
                "test-app",
                "--release",
                "r1",
                "--ingress-class",
                "nginx",
                "--output",
                str(render_output),
            ]
            subprocess.run(render, check=True, capture_output=True)
            manifests = [
                json.loads(path.read_text()) for path in render_output.glob("*.json")
            ]
            self.assertTrue(
                all(item["metadata"]["namespace"] == "test-app" for item in manifests)
            )
            job = next(item for item in manifests if item["kind"] == "Job")
            self.assertEqual(job["metadata"]["name"], "migrate-r1")
            self.assertEqual(
                job["spec"]["template"]["spec"]["containers"][0]["image"],
                "registry.example/backend:r1",
            )
            self.assertNotEqual(
                subprocess.run(render, capture_output=True).returncode, 0
            )
            other = render[:-1] + [
                str(Path(directory) / "missing-env"),
                "--environment",
                "other",
            ]
            self.assertNotEqual(
                subprocess.run(other, capture_output=True).returncode, 0
            )

            subprocess.run(["git", "init", "-q", str(target)], check=True)
            for relative in (
                "backend/app/main.py",
                "backend/uv.lock",
                "frontend/app/src/App.tsx",
                "frontend/app/.dockerignore",
                "deployments/dev/.env.example",
                "deployments/prod/k8s/web-config.json",
                ".vscode/tasks.json",
                "docs/README.md",
            ):
                self.assertEqual(
                    subprocess.run(
                        ["git", "check-ignore", "--no-index", relative],
                        cwd=target,
                        capture_output=True,
                    ).returncode,
                    1,
                    relative,
                )
            for relative in (
                "deployments/dev/.env",
                "frontend/app/node_modules/x.js",
                ".venv/lib/example.py",
            ):
                self.assertEqual(
                    subprocess.run(
                        ["git", "check-ignore", "--no-index", relative],
                        cwd=target,
                        capture_output=True,
                    ).returncode,
                    0,
                    relative,
                )

    def test_optional_github_actions_and_copy_refusal(self):
        with tempfile.TemporaryDirectory(prefix="scaffold options ") as directory:
            target = Path(directory) / "project"
            created = subprocess.run(
                [sys.executable, str(SCRIPT), str(target), "--github-actions"],
                capture_output=True,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertTrue((target / ".github/workflows/ci.yml").is_file())
            sentinel = target / "my-work.txt"
            sentinel.write_text("preserve")
            retry = subprocess.run(
                [sys.executable, str(SCRIPT), str(target)], capture_output=True
            )
            self.assertNotEqual(retry.returncode, 0)
            self.assertEqual(sentinel.read_text(), "preserve")
            alias = Path(directory) / "alias"
            alias.symlink_to(target, target_is_directory=True)
            self.assertNotEqual(
                subprocess.run(
                    [sys.executable, str(SCRIPT), str(alias)], capture_output=True
                ).returncode,
                0,
            )


if __name__ == "__main__":
    unittest.main()
