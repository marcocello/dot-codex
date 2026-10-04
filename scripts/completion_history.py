#!/usr/bin/env python3
"""Compact portable historical completion; never substitutes for fresh proof."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile

from verification_receipt import digest, read_json, repo_path


def read_history(root: Path, feature_id: str, feature_dir: str, proof_run: str) -> dict | None:
    path = repo_path(root, feature_dir + '/completion.json')
    if not path.exists():
        return None
    value = read_json(path)
    checksum = value.pop('receipt_digest', None)
    if checksum != digest(value):
        raise ValueError('completion history is altered or incomplete')
    if value.get('version') != 1 or value.get('feature_id') != feature_id or value.get('feature_dir') != feature_dir or value.get('verdict') != 'PASS':
        raise ValueError('completion history does not match feature')
    if value.get('proof_run') != proof_run:
        return None  # A new completion must validate its newly supplied evidence.
    if not isinstance(value.get('summary'), str) or not value['summary'].strip() or not value.get('evidence_digest'):
        raise ValueError('completion history lacks evidence attribution')
    return value


def record_history(root: Path, entry: dict, *, historical: bool = False) -> None:
    pointer = entry['proof_run']
    source = pointer if pointer.endswith('/review.json') else pointer + '/review.json'
    source_path = repo_path(root, source)
    if historical and not source_path.exists():
        result = read_json(repo_path(root, pointer + '/result.json'))
        if result.get('status') != 'PASS':
            raise ValueError('historical source did not pass')
        receipt = dict(target=result.get('target', 'unrecorded'), implementer=None,
                       summary='Retained historical PASS; original run has no review attribution.',
                       receipt_digest=digest(result), candidate_digest=result.get('candidate_digest'))
    else:
        receipt = read_json(source_path)
    value = dict(version=1, feature_id=entry['id'], feature_dir=entry['feature_dir'],
                 proof_run=pointer, verdict='PASS', recorded_at=datetime.now(timezone.utc).isoformat(),
                 target=receipt['target'], implementer=receipt['implementer'], summary=receipt['summary'],
                 evidence_digest=receipt['receipt_digest'])
    if receipt.get('kind') == 'round':
        value['acceptance'] = receipt['features'][entry['id']]
    else:
        value['candidate_digest'] = receipt['candidate_digest']
    value['receipt_digest'] = digest(value)
    path = repo_path(root, entry['feature_dir'] + '/completion.json')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix='.completion-', delete=False) as output:
            temporary = Path(output.name)
            json.dump(value, output, indent=2, sort_keys=True)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
