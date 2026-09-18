"""Check local documentation fragment navigation after moving lifecycle guidance."""
from pathlib import Path
import re
from urllib.parse import unquote

root = Path(__file__).resolve().parents[4]
files = [root / 'AGENTS.md', root / 'README.md', * (root / 'docs/harness').rglob('*.md')]
files += list((root / 'skills').glob('coding-*/**/*.md'))
errors = []
checked = 0
for source in files:
    for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', source.read_text()):
        if '://' in target or '#' not in target:
            continue
        path, fragment = target.split('#', 1)
        if not fragment:
            continue
        destination = (source.parent / unquote(path)).resolve() if path else source
        if not destination.is_file() or destination.suffix != '.md':
            continue
        anchors = set()
        duplicates = {}
        for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', destination.read_text(), re.M):
            slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
            count = duplicates.get(slug, 0)
            duplicates[slug] = count + 1
            anchors.add(slug if count == 0 else f'{slug}-{count}')
        checked += 1
        if unquote(fragment) not in anchors:
            errors.append(f'{source.relative_to(root)} -> {target}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {checked} local Markdown fragment links resolve')
