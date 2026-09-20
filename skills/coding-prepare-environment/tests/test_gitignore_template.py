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
            ".gitignore", "README.md", "backend/app/package.json",
            "backend/app/package-lock.json", "backend/app/tsconfig.json",
            "backend/app/src/index.ts", "backend/pyproject.toml",
            "backend/requirements-dev.txt", "backend/app/main.py",
            "frontend/app/package.json", "frontend/app/src/App.tsx",
            "frontend/app/src/style.css", ".vscode/tasks.json",
            "backend/.env.example", "frontend/app/.env.local.example",
            "custom/existing/layout/main.py", "backend/app/src/index.mts",
            "backend/app/routes/web.php",
        ]
        ignored = [
            "backend/app/src/unclassified.bin", "backend/app/src/credentials.json",
            "backend/.env", "frontend/app/.env.local", "backend/.env.production",
            "backend/app/node_modules/pkg/index.js", ".venv/lib/module.py",
            "frontend/app/dist/index.js", "frontend/app/.next/server/page.js",
            "backend/app/__pycache__/module.py", "coverage/README.md",
            "backend/app/auth_info_baileys/creds.json", "backend/app/.auth/session.ts",
            "backend/app/sessions/session.js", "uploads/note.md",
            "backend/app/private.key", "backend/app/local.sqlite3",
            "backend/app/node_modules/pkg/.env.example",
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
