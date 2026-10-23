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
            ".gitignore", "docs/README.md", "backend/package.json",
            "backend/package-lock.json", "backend/tsconfig.json",
            "backend/src/index.ts", "backend/pyproject.toml",
            "backend/requirements-dev.txt", "backend/main.py",
            "frontend/app/package.json", "frontend/app/src/App.tsx",
            "frontend/app/src/style.css", ".vscode/tasks.json",
            "deployments/dev/.env.example", "frontend/app/.env.local.example",
            "custom/existing/layout/main.py", "backend/src/index.mts",
            "backend/routes/web.php",
        ]
        ignored = [
            "backend/src/unclassified.bin", "backend/src/credentials.json",
            "deployments/dev/.env", "frontend/app/.env.local", "backend/.env.production",
            "backend/node_modules/pkg/index.js", ".venv/lib/module.py",
            "frontend/app/dist/index.js", "frontend/app/.next/server/page.js",
            "backend/__pycache__/module.py", "coverage/README.md",
            "backend/auth_info_baileys/creds.json", "backend/.auth/session.ts",
            "backend/sessions/session.js", "uploads/note.md",
            "backend/private.key", "backend/local.sqlite3",
            "backend/node_modules/pkg/.env.example",
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
