#!/usr/bin/env python3
"""Independent acceptance at the on-disk skill consumption boundary."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
PROOF = Path(__file__).resolve().parent
NEW = {'coding-shape', 'coding-ship', 'coding-fix', 'coding-operate'}
BASE = json.loads((PROOF / 'baseline.json').read_text())
FAILURES = []

def check(ok, message):
    print(('PASS ' if ok else 'FAIL ') + message)
    if not ok:
        FAILURES.append(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def surface():
    candidates = [ROOT / 'AGENTS.md', ROOT / 'README.md', ROOT / 'skills.toml']
    candidates += list((ROOT / 'docs/harness').rglob('*.md'))
    for directory in (ROOT / 'skills').iterdir():
        if directory.name.startswith('coding-') or directory.name == 'harness-manage-skills':
            candidates += [p for p in directory.rglob('*') if p.is_file() and p.suffix in ('.md', '.yaml', '.sh')]
    return sorted(set(candidates))

def fingerprint():
    return {str(p.relative_to(ROOT)): sha(p) for p in surface()}

if '--fingerprint' in sys.argv:
    print(json.dumps(fingerprint(), indent=2))
    sys.exit(0)

print('Target: local checkout skill inventory and current instruction consumers at ' + str(ROOT))
print('Fresh application-task discovery is outside this executable target.')
inventory = tomllib.loads((ROOT / 'skills.toml').read_text())['skills']
indexed = {s['name']: s for s in inventory}
check(len(indexed) == len(inventory), 'Inventory names are unique')
check(NEW <= indexed.keys() and 'coding-workflow' not in indexed and 'coding-analyze' not in indexed, 'Desired inventory replaces workflow with exactly four lifecycle entries')
expected_other = {s['name']: s for s in BASE['inventory'] if s['name'] != 'coding-workflow'}
check({n:s for n,s in indexed.items() if n not in NEW} == expected_other, 'Unrelated desired inventory entries preserved')
result = subprocess.run([sys.executable, str(ROOT / 'scripts/skill_inventory.py'), '--manifest', str(ROOT / 'skills.toml'), '--skills-root', str(ROOT / 'skills'), 'list'], capture_output=True, text=True)
check(result.returncode == 0, 'Real inventory list command succeeds')
listed = {line.split('\t')[0] for line in result.stdout.splitlines()}
check(NEW <= listed and 'coding-workflow' not in listed and 'coding-analyze' not in listed, 'Inventory consumer reads four lifecycle skills without retired entries')
for name in sorted(NEW):
    d = ROOT / 'skills' / name
    skill = d / 'SKILL.md'
    metadata = d / 'agents/openai.yaml'
    check(skill.is_file() and metadata.is_file(), name + ' has discoverable entrypoint and UI metadata')
    if skill.is_file() and metadata.is_file():
        front = skill.read_text().split('---', 2)[1]
        check(re.search(r'^name:\s*' + re.escape(name) + r'\s*$', front, re.M) is not None and re.search(r'^description:\s*\S', front, re.M) is not None, name + ' has matching discovery name and description')
        check(re.search(r'allow_implicit_invocation:\s*true\b', metadata.read_text()) is not None, name + ' allows automatic invocation')
        check('$' + name in metadata.read_text(), name + ' UI prompt invokes its own entrypoint')
check(not (ROOT / 'skills/coding-workflow').exists() and not (ROOT / 'skills/coding-analyze').exists(), 'Retired workflow and generic Analyze are not discoverable directories')
for name in ('coding-antipattern-review', 'coding-architecture-deep-dive', 'coding-review-workflow'):
    check((ROOT / 'skills' / name / 'SKILL.md').is_file(), name + ' remains directly available')

broken = []
stale = []
for file in surface():
    if file.suffix != '.md':
        continue
    text = file.read_text()
    if re.search(r'(?:skills/|\.\./)coding-workflow/|\$coding-workflow\b', text):
        stale.append(str(file.relative_to(ROOT)))
    for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', text):
        target = target.strip('<>')
        if '://' in target or target.startswith(('#', 'mailto:', '/')):
            continue
        relative = unquote(target.split('#', 1)[0])
        if not relative:
            continue
        resolved = (file.parent / relative).resolve()
        if not resolved.exists():
            broken.append(str(file.relative_to(ROOT)) + ' -> ' + target)
check(not stale, 'Current guidance has no retired skill paths/invocations: ' + '; '.join(stale))
check(not broken, 'Current guidance local Markdown links resolve: ' + '; '.join(broken))
ops = ROOT / 'skills/coding-operate/scripts/ops_diag_preflight.sh'
check(ops.is_file() and sha(ops) == BASE['ops_sha256'], 'Operational preflight helper moved without behavior changes')
if ops.is_file():
    help_run = subprocess.run(['bash', str(ops), '--help'], capture_output=True, text=True)
    check(help_run.returncode == 0 and '--namespace' in help_run.stdout, 'Moved operational helper accepts its real help invocation')
changed = [name for name,digest in BASE['historical_contracts'].items() if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
check(not changed, 'Historical feature contracts and runners preserved: ' + '; '.join(changed))

assessment_path = ROOT / 'docs/features/four-lifecycle-skills/evidence/semantic-assessment.json'
check(assessment_path.is_file(), 'Independent semantic assessment available')
if assessment_path.is_file():
    assessment = json.loads(assessment_path.read_text())
    check(assessment.get('author_role') == 'independent-proof-author', 'Semantic assessment authored independently')
    check(assessment.get('input_hashes') == fingerprint(), 'Semantic assessment binds unchanged current instruction surface')
    cases = json.loads((PROOF / 'scenarios.json').read_text())
    results = assessment.get('cases', {})
    check(set(results) == {c['id'] for c in cases}, 'Semantic assessment covers all frozen routing/scope cases')
    for case in cases:
        actual = results.get(case['id'], {})
        check(actual.get('verdict') == 'PASS' and actual.get('route') == case['expected_route'] and bool(actual.get('evidence')) and len(actual.get('paraphrase_outcomes', [])) == len(case['prompts']), 'Independent semantic routing and scope: ' + case['id'])
if FAILURES:
    print(str(len(FAILURES)) + ' acceptance failure(s)')
    sys.exit(1)
print('PASS four lifecycle skills acceptance; on-disk readiness only')
