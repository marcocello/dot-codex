#!/usr/bin/env python3
"""Independent local skill-consumption contract, not an LLM behavior test."""
from pathlib import Path
import hashlib
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
RETIRED = {'coding-research', 'codex-session-showcase', 'no-bullshit-technical-writing', 'manage-codex-skills', 'sync-codex-skills', 'second-brain-activity-brief', 'second-brain-weekly-review', 'coding-ui-improvement'}
NEW = {'writing-technical-content', 'codex-manage-skills', 'second-brain-review', 'coding-ui-toolkit'}
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
check(len(baseline) == 51, 'baseline must retain 51 entries')
check(set(current) == set(baseline) - RETIRED | NEW, 'inventory set differs from agreed 47 names')
for name in set(baseline) - RETIRED:
    check(current.get(name) == baseline[name], f'unrelated inventory declaration changed: {name}')
for name in RETIRED:
    check(not (ROOT / 'skills' / name).exists(), f'retired folder remains discoverable: {name}')
for name in NEW:
    check(current.get(name) == {'name': name, 'kind': 'owned', 'path': name}, f'new owned declaration invalid: {name}')
    path = ROOT / 'skills' / name / 'SKILL.md'
    if not path.exists():
        check(False, f'missing entrypoint: {name}')
        continue
    content = path.read_text()
    header = content.split('---', 2)
    check(len(header) == 3 and re.search(r'^name:\s*[\'\"]?' + re.escape(name) + r'[\'\"]?\s*$', header[1], re.M), f'frontmatter name mismatch: {name}')
    check(len(header) == 3 and bool(re.search(r'^description:\s*\S', header[1], re.M)), f'missing discovery description: {name}')
    meta = path.parent / 'agents/openai.yaml'
    check(meta.exists() and 'default_prompt:' in meta.read_text() and 'display_name:' in meta.read_text(), f'new UI metadata missing: {name}')

for old, expected in json.loads((HERE / 'baseline-hashes.json').read_text()).items():
    target = ROOT / old.replace('no-bullshit-technical-writing/', 'writing-technical-content/')
    check(target.exists() and sha(target) == expected, f'protected content changed or missing: {old}')

# Current harness and owned skill sources, excluding historical feature packages/reviews.
live = list((ROOT / 'docs/harness').rglob('*.md'))
live += [ROOT / x for x in ['AGENTS.md', 'README.md'] if (ROOT / x).exists()]
for entry in current.values():
    if entry['kind'] == 'owned':
        folder = ROOT / 'skills' / entry['path']
        live += list(folder.rglob('*.md')) + list(folder.rglob('*.yaml'))
for path in live:
    text = path.read_text()
    for old in RETIRED:
        check(not re.search(r'(?<![\w-])' + re.escape(old) + r'(?![\w-])', text), f'retired current reference {old}: {path.relative_to(ROOT)}')
    # Only relative Markdown links are checked; code strings are read during semantic evaluation.
    for link in re.findall(r'\]\(([^)]+)\)', text):
        dest = link.split('#')[0].strip('<>')
        if not dest or ':' in dest or dest.startswith('/'):
            continue
        check((path.parent / dest).exists(), f'broken local link {dest}: {path.relative_to(ROOT)}')

# Semantic inspection is independent evidence, not a bag-of-keywords assertion.
semantic = HERE.parent / 'evidence/semantic-review.json'
check(semantic.exists(), 'independent semantic read-through evidence is required')
if semantic.exists():
    evidence = json.loads(semantic.read_text())
    check(evidence.get('author') == '/root/proof_author', 'semantic review must be by independent proof author')
    rubric = json.loads((HERE / 'scenarios.json').read_text())
    check(set(evidence.get('scenarios', {})) == set(rubric), 'semantic scenarios incomplete')
    for scenario, result in evidence.get('scenarios', {}).items():
        check(result.get('status') == 'PASS' and len(result.get('reason', '')) > 100 and bool(result.get('citations')), f'semantic scenario lacks grounded PASS: {scenario}')
    hashes = evidence.get('inputs', {})
    required = ['skills.toml'] + [str(p.relative_to(ROOT)) for p in live]
    check(all(p in hashes for p in required), 'semantic review does not bind all current discovery/routing inputs')
    for name, expected in hashes.items():
        path = ROOT / name
        check(path.exists() and sha(path) == expected, f'semantic review stale: {name}')
if errors:
    for error in errors:
        print('FAIL:', error)
    raise SystemExit(1)
print('PASS: 47-entry inventory, discovery, preserved providers, current references and independent semantic document scenarios')
print('Limit: document-contract proof; no claim of fresh Codex activation or probabilistic agent execution.')
