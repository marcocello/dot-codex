#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
import os
import re
import subprocess

root = Path.cwd()
guide = root / 'docs/harness/coding/writing.md'
assert guide.is_file() and guide.read_text().strip(), 'Missing writing reference'
skills = sorted((root / 'skills').glob('coding-*/SKILL.md'))
assert skills, 'No coding skills found'
validator = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills/.system/skill-creator/scripts/quick_validate.py'
for skill in skills:
    subprocess.run(['python3', str(validator), str(skill.parent)], check=True)
for source in [*skills, root / 'docs/harness/coding/proof.md', root / 'README.md']:
    links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', source.read_text())
    resolved = [(source.parent / link.split('#', 1)[0]).resolve() for link in links if '://' not in link]
    assert guide.resolve() in resolved, f'No canonical writing link in {source.relative_to(root)}'
    print(f'READABLE writing reference: {source.relative_to(root)}')
print('PASS: installed coding-skill metadata and canonical reference links')
PY
