#!/usr/bin/env python3
"""Dedicated local discovery, preservation, semantic document and offline helper proof."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RETIRED = {'capture-note', 'second-brain-capture-raw-input', 'second-brain-external-sweep', 'zotero-capture-source'}
NEW = 'knowledge-capture'
errors = []
def check(ok, message):
    if not ok:
        errors.append(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def entries(path):
    values = tomllib.loads(path.read_text())['skills']
    check(len(values) == len({x['name'] for x in values}), 'duplicate inventory names')
    return {x['name']: x for x in values}

baseline = entries(HERE / 'baseline-skills.toml')
current = entries(ROOT / 'skills.toml')
check(len(baseline) == 47, 'baseline must retain 47 entries')
check(set(current) == set(baseline) - RETIRED | {NEW}, 'inventory differs from agreed 44-entry result')
for name in set(baseline) - RETIRED:
    check(current.get(name) == baseline[name], f'unrelated declaration changed: {name}')
for name in RETIRED:
    check(not (ROOT / 'skills' / name).exists(), f'retired folder remains discoverable: {name}')
check(current.get(NEW) == {'name': NEW, 'kind': 'owned', 'path': NEW}, 'new owned declaration invalid')
folder = ROOT / 'skills' / NEW
entrypoint = folder / 'SKILL.md'
if entrypoint.exists():
    text = entrypoint.read_text()
    header = text.split('---', 2)
    check(len(header) == 3 and re.search(r'^name:\s*[\'\"]?knowledge-capture[\'\"]?\s*$', header[1], re.M), 'frontmatter name mismatch')
    check(len(header) == 3 and bool(re.search(r'^description:\s*\S', header[1], re.M)), 'missing discovery description')
    meta = folder / 'agents/openai.yaml'
    check(meta.exists() and 'default_prompt:' in meta.read_text() and 'display_name:' in meta.read_text(), 'UI metadata missing')
else:
    check(False, 'knowledge-capture entrypoint missing')

hashes = json.loads((HERE / 'baseline-hashes.json').read_text())
for name, expected in hashes['protected'].items():
    path = ROOT / name
    check(path.exists() and sha(path) == expected, f'protected content changed: {name}')
relocated = {}
for name, expected in hashes['relocated'].items():
    matches = list(folder.rglob(name))
    check(len(matches) == 1, f'relocated helper/reference not unique or missing: {name}')
    if len(matches) == 1:
        relocated[name] = matches[0]
        check(sha(matches[0]) == expected, f'relocated bytes changed: {name}')

live = list((ROOT / 'docs/harness').rglob('*.md'))
live += [ROOT / x for x in ['AGENTS.md', 'README.md'] if (ROOT / x).exists()]
for entry in current.values():
    if entry['kind'] == 'owned':
        d = ROOT / 'skills' / entry['path']
        live += list(d.rglob('*.md')) + list(d.rglob('*.yaml'))
for path in live:
    text = path.read_text()
    for name in RETIRED:
        check(not re.search(r'(?<![\w-])' + re.escape(name) + r'(?![\w-])', text), f'retired live reference {name}: {path.relative_to(ROOT)}')
    for link in re.findall(r'\]\(([^)]+)\)', text):
        dest = link.split('#')[0].strip('<>')
        if not dest or ':' in dest or dest.startswith('/'):
            continue
        check((path.parent / dest).exists(), f'broken relative link {dest}: {path.relative_to(ROOT)}')

helper = relocated.get('build_capture_ris.py')
if helper:
    with tempfile.TemporaryDirectory(prefix='knowledge-capture-proof-') as tmp:
        tmp = Path(tmp)
        for source_type, ris_type, note_title in [('video', 'VIDEO', 'Raw_Transcript'), ('article', 'ELEC', 'Source_Outline')]:
            spec = {'source_type': source_type, 'title': 'Verified source', 'url': 'https://example.org/canonical', 'authors': ['Author One'], 'date': '2026-09-15', 'publisher': 'Publisher', 'tags': ['existing-topic', 'research'], 'source_note_html': f'<h1>{note_title}</h1><p>0:00 Start; 1:00 End</p>'}
            src, out = tmp / f'{source_type}.json', tmp / f'{source_type}.ris'
            src.write_text(json.dumps(spec))
            result = subprocess.run([sys.executable, str(helper), '--spec', str(src), '--out', str(out)], text=True, capture_output=True)
            check(result.returncode == 0 and out.exists(), f'RIS public CLI failed for {source_type}')
            if out.exists():
                lines = out.read_text().splitlines()
                expected = [f'TY  - {ris_type}', 'TI  - Verified source', 'AU  - Author One', 'DA  - 2026/09/15/', 'PB  - Publisher', 'UR  - https://example.org/canonical', 'KW  - existing-topic', 'KW  - research', f'N1  - {spec["source_note_html"]}', 'ER  -']
                check(lines == expected, f'RIS durable output loses metadata/tags/note shape for {source_type}')
            spec['source_note_html'] = '<h1>Highlights</h1><p>Wrong first note</p>'
            bad_out = tmp / f'{source_type}-bad.ris'
            src.write_text(json.dumps(spec))
            bad = subprocess.run([sys.executable, str(helper), '--spec', str(src), '--out', str(bad_out)], text=True, capture_output=True)
            check(bad.returncode != 0 and not bad_out.exists(), f'RIS must reject incorrect first note for {source_type}')

semantic = HERE.parent / 'evidence/semantic-review.json'
check(semantic.exists(), 'independent semantic scenario evidence required')
if semantic.exists():
    evidence = json.loads(semantic.read_text())
    check(evidence.get('author') == '/root/proof_author', 'semantic author must be independent')
    rubric = json.loads((HERE / 'scenarios.json').read_text())
    check(set(evidence.get('scenarios', {})) == set(rubric), 'semantic scenario groups incomplete')
    for name, result in evidence.get('scenarios', {}).items():
        check(result.get('status') == 'PASS' and len(result.get('reason', '')) > 100 and bool(result.get('citations')), f'semantic scenario lacks grounded PASS: {name}')
    inputs = evidence.get('inputs', {})
    required = ['skills.toml'] + [str(p.relative_to(ROOT)) for p in live] + [str(p.relative_to(ROOT)) for p in relocated.values()]
    check(all(name in inputs for name in required), 'semantic evidence must bind all live routing and relocated resources')
    for name, expected in inputs.items():
        path = ROOT / name
        check(path.exists() and sha(path) == expected, f'semantic evidence stale: {name}')
if errors:
    for error in errors:
        print('FAIL:', error)
    raise SystemExit(1)
print('PASS: 44-entry inventory, discovery, protected content, relocated RIS CLI and independent document scenarios')
print('Limit: no external capture, live model execution or app reload claimed.')
