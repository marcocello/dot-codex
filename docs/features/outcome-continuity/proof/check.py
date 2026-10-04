#!/usr/bin/env python3
"""Check retained evidence integrity, not agent behavior or reviewer correctness."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
trials = ['baseline-integration', 'candidate-integration', 'candidate-review', 'candidate-repair']
workers = []
models = []
for name in trials:
    base = root / name
    meta = json.loads((base / 'metadata.json').read_text())
    assert meta['worker_id'], f'{name}: missing fresh worker identity'
    assert meta['instruction_selection'] == 'forced', f'{name}: record explicit bundle selection'
    assert meta['source_session'], f'{name}: missing trace provenance'
    assert meta['observation_kind'] in ['native-visible-trace', 'instrumented-tool-receipts'], f'{name}: declare observation kind'
    if meta['observation_kind'] == 'instrumented-tool-receipts':
        assert meta['observation_limit'].strip(), f'{name}: record missing native trace limitation'
        assert (base / 'tool-events.log').read_text().strip(), f'{name}: missing executed tool receipts'
    assert meta['outcome'] in ['completed', 'failed', 'interrupted'], f'{name}: missing outcome'
    workers.append(meta['worker_id'])
    models.append(meta['model'])
    for artifact in ['trace.md', 'result.md']:
        assert (base / artifact).read_text().strip(), f'{name}: empty {artifact}'
    inputs = json.loads((base / 'inputs.json').read_text())
    assert 'fixture/REQUEST.md' in inputs, f'{name}: missing original task'
    assert any(p.startswith('instructions/') for p in inputs), f'{name}: missing instruction snapshot'
    assert 'trace.md' in inputs and 'result.md' in inputs, f'{name}: hash retained observations too'
    if meta['observation_kind'] == 'instrumented-tool-receipts':
        assert 'tool-events.log' in inputs, f'{name}: hash tool receipts'
    for relative, expected in inputs.items():
        file = (base / relative).resolve()
        assert file.is_relative_to(base.resolve()), f'{name}: escaping retained artifact'
        assert hashlib.sha256(file.read_bytes()).hexdigest() == expected, f'{name}: changed {relative}'
assert len(set(workers)) == 4, 'Trials require four fresh workers'
# Identical raw integration input is central to the comparison.
a = json.loads((root / trials[0] / 'inputs.json').read_text())
b = json.loads((root / trials[1] / 'inputs.json').read_text())
assert {p: h for p, h in a.items() if p.startswith('fixture/')} == {p: h for p, h in b.items() if p.startswith('fixture/')}, 'Integration fixtures differ'
review = json.loads((root / 'adjudication.json').read_text())
assert review['reviewer_id'] and review['reviewer_id'] not in workers, 'Independent adjudicator required'
assert review['limitations'].strip(), 'Record sample and comparison limits'
assert review['comparison'].strip(), 'Record baseline/candidate assessment, including neutral result'
assert len(set(models)) == 1 or review.get('model_difference'), 'Disclose model difference'
for name in trials:
    judgment = review['trials'][name]
    assert isinstance(judgment['pass'], bool), f'{name}: semantic pass judgment required'
    assert judgment['rationale'].strip(), f'{name}: semantic rationale required'
    assert judgment['evidence'], f'{name}: retained evidence references required'
    for reference in judgment['evidence']:
        file = (root / reference.split('#')[0]).resolve()
        assert file.is_relative_to(root) and file.is_file(), f'{name}: missing evidence {reference}'
    if name.startswith('candidate-'):
        assert judgment['pass'], f'{name}: independent semantic adjudication failed'
print('PASS: retained artifact integrity and independent recorded semantic judgments')
print('LIMIT: this command does not execute workers or independently validate their behavior')
