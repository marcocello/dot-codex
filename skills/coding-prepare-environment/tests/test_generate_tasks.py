"""Exercise the setup CLI against existing and newly generated task files."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


GENERATOR = Path(__file__).resolve().parents[1] / "scripts/generate_tasks.py"


class GenerateTasksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="task-generator-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project with spaces"
        (self.root / ".vscode").mkdir(parents=True)
        (self.root / "app/backend").mkdir(parents=True)
        (self.root / "app/frontend").mkdir()
        (self.root / "app/frontend/package.json").write_text(
            json.dumps({"scripts": {"dev": "vite"}})
        )
        self.path = self.root / ".vscode/tasks.json"

    def generate(self, *args):
        return subprocess.run(
            [sys.executable, str(GENERATOR), str(self.root), *args],
            text=True, capture_output=True, timeout=10,
        )

    def read_generated(self, *args):
        result = self.generate(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(self.path.read_text())

    def test_preserves_shared_settings_and_is_idempotent(self):
        existing = {
            "version": "2.0.0",
            "inputs": [{"id": "target", "type": "promptString", "description": "Target"}],
            "options": {"env": {"TARGET": "${input:target}"}},
            "linux": {"options": {"cwd": "/tmp"}},
            "tasks": [{"label": "custom", "type": "shell", "command": "echo ${input:target}"}],
        }
        self.path.write_text(json.dumps(existing))
        actual = self.read_generated()
        for key in ("version", "inputs", "options", "linux"):
            self.assertEqual(actual.get(key), existing[key])
        self.assertIn(existing["tasks"][0], actual["tasks"])
        self.assertEqual(actual, self.read_generated())

    def test_backend_process_starts_in_workspace_with_spaces(self):
        (self.root / ".venv/bin").mkdir(parents=True)
        (self.root / ".venv/bin/python").symlink_to(sys.executable)
        (self.root / "app/backend/main.py").write_text('print("backend started")\n')
        task = next(t for t in self.read_generated()["tasks"] if t["label"] == "backend:app")
        self.assertEqual(task["type"], "process")
        command = task["command"].replace("${workspaceFolder}", str(self.root))
        cwd = task["options"]["cwd"].replace("${workspaceFolder}", str(self.root))
        result = subprocess.run([command, *task["args"]], cwd=cwd, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "backend started")

    def test_fastapi_and_explicit_shell_override(self):
        (self.root / "app/backend/main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
        (self.root / "app/backend/requirements.txt").write_text("fastapi\nuvicorn\n")
        task = next(t for t in self.read_generated()["tasks"] if t["label"] == "backend:app")
        self.assertEqual(task["type"], "process")
        self.assertEqual(task["args"], ["-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"])
        override = "python custom.py && echo finished"
        task = next(t for t in self.read_generated("--replace", "--backend-app-command", override)["tasks"] if t["label"] == "backend:app")
        self.assertEqual(task["type"], "shell")
        self.assertEqual(task["command"], override)

    def test_jsonc_preserves_strings_and_accepts_trailing_commas(self):
        custom = {"label": "custom", "command": 'echo "https://example.test/*path*/",}'}
        text = '{\n// VS Code task settings\n"version":"2.0.0",\n"tasks":[' + json.dumps(custom) + ',],/* comment */\n}'
        self.path.write_text(text)
        self.assertIn(custom, self.read_generated()["tasks"])

    def test_packaged_fastapi_uses_component_working_directory(self):
        (self.root / "app/backend/app").mkdir()
        (self.root / "app/backend/app/main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()\n"
        )
        (self.root / "app/backend/pyproject.toml").write_text(
            '[project]\ndependencies = ["fastapi", "uvicorn"]\n'
        )
        tasks = self.read_generated()["tasks"]
        backend = next(t for t in tasks if t["label"] == "backend:app")
        self.assertEqual(backend["options"]["cwd"], "${workspaceFolder}/app/backend")
        self.assertEqual(backend["args"][2], "app.main:app")
        frontend = next(t for t in tasks if t["label"] == "frontend")
        self.assertEqual(frontend["options"]["cwd"], "${workspaceFolder}/app/frontend")

    def test_existing_layout_can_be_selected_without_relocation(self):
        legacy = self.root / "backend/app"
        legacy.mkdir(parents=True)
        (legacy / "main.py").write_text('print("existing backend")\n')
        (self.root / ".venv/bin").mkdir(parents=True)
        (self.root / ".venv/bin/python").symlink_to(sys.executable)
        tasks = self.read_generated(
            "--backend-cwd", "${workspaceFolder}/backend/app",
            "--frontend-cwd", "${workspaceFolder}/frontend/app",
        )["tasks"]
        task = next(t for t in tasks if t["label"] == "backend:app")
        command = task["command"].replace("${workspaceFolder}", str(self.root))
        cwd = task["options"]["cwd"].replace("${workspaceFolder}", str(self.root))
        result = subprocess.run([command, *task["args"]], cwd=cwd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "existing backend")
        self.assertTrue((legacy / "main.py").is_file())

    def test_invalid_input_is_not_overwritten(self):
        for invalid in ('{"tasks": [}', '{/* unterminated', '{"tasks": null}', '{"tasks":[,]}', '{,}', '{"tasks":[ ,]}'):
            with self.subTest(invalid=invalid):
                self.path.write_text(invalid)
                self.assertNotEqual(self.generate().returncode, 0)
                self.assertEqual(self.path.read_text(), invalid)

    def test_local_fullstack_does_not_require_a_tunnel(self):
        tasks = {t["label"]: t for t in self.read_generated()["tasks"]}
        self.assertNotIn("backend:ngrok", tasks)
        self.assertEqual(tasks["backend"]["dependsOn"], ["backend:app"])
        self.assertEqual(tasks["fullstack"]["dependsOn"], ["frontend", "backend"])

    def test_existing_startup_dependencies_and_environment_are_preserved(self):
        backend = {"label": "backend:app", "type": "shell", "command": "existing backend",
                   "dependsOn": ["db:ready"], "options": {"cwd": "${workspaceFolder}/app/backend",
                   "env": {"CONFIG": "local"}}}
        ready = {"label": "db:ready", "command": "prepare database"}
        fullstack = {"label": "fullstack", "dependsOn": ["backend:app"], "dependsOrder": "sequence"}
        self.path.write_text(json.dumps({"tasks": [backend, ready, fullstack]}))
        actual = self.read_generated()["tasks"]
        for task in (backend, ready, fullstack):
            self.assertIn(task, actual)
        self.assertEqual(len([t for t in actual if t["label"] == "backend:app"]), 1)

    def test_single_component_projects_have_no_missing_component_dependency(self):
        (self.root / "app/frontend/package.json").unlink()
        (self.root / "app/frontend").rmdir()
        tasks = {t["label"]: t for t in self.read_generated()["tasks"]}
        self.assertNotIn("frontend", tasks)
        self.assertEqual(tasks["fullstack"]["dependsOn"], ["backend"])
        self.path.unlink()
        (self.root / "app/backend").rmdir()
        (self.root / "app/frontend").mkdir()
        (self.root / "app/frontend/package.json").write_text(json.dumps({"scripts": {"dev": "vite"}}))
        tasks = {t["label"]: t for t in self.read_generated()["tasks"]}
        self.assertNotIn("backend", tasks)
        self.assertNotIn("backend:app", tasks)
        self.assertEqual(tasks["fullstack"]["dependsOn"], ["frontend"])

    def test_package_manager_prerequisites_and_optional_compose_stop(self):
        (self.root / "app/frontend/package.json").write_text(
            json.dumps({"packageManager": "pnpm@10.0.0", "scripts": {"dev": "vite"}})
        )
        ready = {"label": "db:ready", "command": "prepare database"}
        self.path.write_text(json.dumps({"tasks": [ready]}))
        tasks = {t["label"]: t for t in self.read_generated(
            "--backend-app-command", "docker compose up backend",
            "--backend-down-command", "docker compose down",
            "--backend-ready-pattern", "Application startup complete",
            "--backend-depends-on", "db:ready",
        )["tasks"]}
        self.assertEqual(tasks["frontend"]["command"], "pnpm run dev")
        self.assertEqual(tasks["backend:app"]["dependsOn"], ["db:ready"])
        self.assertEqual(tasks["backend:down"]["command"], "docker compose down")
        self.assertNotIn("backend:down", tasks["backend"]["dependsOn"])
        self.assertIn("background", tasks["backend:app"]["problemMatcher"])

    def test_tunnel_task_is_included_only_when_selected(self):
        tasks = {t["label"]: t for t in self.read_generated(
            "--backend-ngrok-command", "ngrok http 8000",
        )["tasks"]}
        self.assertEqual(tasks["backend"]["dependsOn"], ["backend:app", "backend:ngrok"])

    def test_missing_package_script_does_not_overwrite_existing_file(self):
        original = '{"tasks":[{"label":"custom","command":"keep"}]}'
        self.path.write_text(original)
        (self.root / "app/frontend/package.json").write_text('{}')
        self.assertNotEqual(self.generate().returncode, 0)
        self.assertEqual(self.path.read_text(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
