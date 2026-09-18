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
        (self.root / "backend/app").mkdir(parents=True)
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
        (self.root / "backend/app/main.py").write_text('print("backend started")\n')
        task = next(t for t in self.read_generated()["tasks"] if t["label"] == "backend:app")
        self.assertEqual(task["type"], "process")
        command = task["command"].replace("${workspaceFolder}", str(self.root))
        cwd = task["options"]["cwd"].replace("${workspaceFolder}", str(self.root))
        result = subprocess.run([command, *task["args"]], cwd=cwd, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "backend started")

    def test_fastapi_and_explicit_shell_override(self):
        (self.root / "backend/app/main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n")
        (self.root / "backend/requirements.txt").write_text("fastapi\nuvicorn\n")
        task = next(t for t in self.read_generated()["tasks"] if t["label"] == "backend:app")
        self.assertEqual(task["type"], "process")
        self.assertEqual(task["args"], ["-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"])
        override = "python custom.py && echo finished"
        task = next(t for t in self.read_generated("--backend-app-command", override)["tasks"] if t["label"] == "backend:app")
        self.assertEqual(task["type"], "shell")
        self.assertEqual(task["command"], override)

    def test_jsonc_preserves_strings_and_accepts_trailing_commas(self):
        custom = {"label": "custom", "command": 'echo "https://example.test/*path*/",}'}
        text = '{\n// VS Code task settings\n"version":"2.0.0",\n"tasks":[' + json.dumps(custom) + ',],/* comment */\n}'
        self.path.write_text(text)
        self.assertIn(custom, self.read_generated()["tasks"])

    def test_invalid_input_is_not_overwritten(self):
        for invalid in ('{"tasks": [}', '{/* unterminated', '{"tasks": null}', '{"tasks":[,]}', '{,}', '{"tasks":[ ,]}'):
            with self.subTest(invalid=invalid):
                self.path.write_text(invalid)
                self.assertNotEqual(self.generate().returncode, 0)
                self.assertEqual(self.path.read_text(), invalid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
