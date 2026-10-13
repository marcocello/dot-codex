"""Verify the documented template using Git's actual ignore semantics."""
from pathlib import Path
import subprocess
import tempfile
import unittest


REFERENCE = Path(__file__).resolve().parents[1] / "references/stack-reference.md"


class GitignoreTemplateTests(unittest.TestCase):
    def test_nested_sources_and_runtime_artifacts(self):
        template = REFERENCE.read_text().split("```gitignore\n", 1)[1].split("```", 1)[0]
        visible = [
            ".gitignore", "README.md", "app/backend/package.json",
            "app/backend/package-lock.json", "app/backend/tsconfig.json",
            "app/backend/src/index.ts", "app/backend/pyproject.toml",
            "app/backend/requirements-dev.txt", "app/backend/main.py",
            "app/frontend/package.json", "app/frontend/src/App.tsx",
            "app/frontend/src/style.css", ".vscode/tasks.json",
            "app/backend/.env.example", "app/frontend/.env.local.example",
            "custom/existing/layout/main.py", "app/backend/src/index.mts",
            "app/backend/routes/web.php",
        ]
        ignored = [
            "app/backend/src/unclassified.bin", "app/backend/src/credentials.json",
            "app/backend/.env", "app/frontend/.env.local", "app/backend/.env.production",
            "app/backend/node_modules/pkg/index.js", ".venv/lib/module.py",
            "app/frontend/dist/index.js", "app/frontend/.next/server/page.js",
            "app/backend/__pycache__/module.py", "coverage/README.md",
            "app/backend/auth_info_baileys/creds.json", "app/backend/.auth/session.ts",
            "app/backend/sessions/session.js", "uploads/note.md",
            "app/backend/private.key", "app/backend/local.sqlite3",
            "app/backend/node_modules/pkg/.env.example",
        ]
        with tempfile.TemporaryDirectory(prefix="ignore-template-") as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            (Path(directory) / ".gitignore").write_text(template)
            for paths, expected in [(visible, 1), (ignored, 0)]:
                for path in paths:
                    with self.subTest(path=path):
                        result = subprocess.run(
                            ["git", "-C", directory, "check-ignore", "--no-index", "-q", path],
                            capture_output=True, text=True,
                        )
                        self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
