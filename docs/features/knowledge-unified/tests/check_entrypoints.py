"""Supporting API referrals and relocation link checks; no real credentials."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path.cwd()
with tempfile.TemporaryDirectory() as tmp:
    missing = str(Path(tmp)/"missing.toml")
    for cli in ["skills/knowledge-connect/scripts/clickup_api.py",
                "skills/knowledge-connect/scripts/notion_api.py",
                "skills/knowledge-config/scripts/clickup_api.py"]:
        p = subprocess.run([sys.executable,cli,"--config",missing,"check"],capture_output=True,text=True)
        assert p.returncode == 3, p.stderr
        assert json.loads(p.stderr)["skill"] == "knowledge-connect"
for directory in ["skills/knowledge-connect","skills/knowledge-capture","skills/knowledge-review"]:
    for p in Path(directory).rglob("*.md"):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if target.startswith(("http:", "https:", "#")) or "$" in target:
                continue
            target = target.split("#",1)[0]
            if target:
                assert (p.parent/target).exists(), (str(p),target)
assert not Path("skills/knowledge-config/SKILL.md").exists()
print("API setup referrals and relocated links: PASS")
