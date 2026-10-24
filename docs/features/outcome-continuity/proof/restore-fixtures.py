#!/usr/bin/env python3
"""Restore only missing generated vendor inputs; never create observations."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
missing = []
for name in ('baseline-integration', 'candidate-integration'):
    base = root / name
    relative = 'fixture/vendor/archivebox.py'
    target = base / relative
    if target.exists() or target.is_symlink():
        continue  # Existing bytes remain subject to the original integrity check.
    if not target.resolve().is_relative_to(root):
        raise SystemExit(f'Refusing an escaping fixture path: {name}')
    expected = json.loads((base / 'inputs.json').read_text())[relative]
    missing.append((target, expected))

if missing:
    with tempfile.TemporaryDirectory(prefix='outcome-fixtures-', dir='/tmp') as temporary:
        seed = Path(temporary) / 'integration'
        subprocess.run([sys.executable, str(Path(__file__).with_name('prepare.py')),
                        'integration', str(seed)], check=True, capture_output=True, text=True)
        content = (seed / 'vendor/archivebox.py').read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if any(expected != digest for _, expected in missing):
            raise SystemExit('Fixture generator does not match the recorded vendor hashes; no fixtures restored.')
        for target, _ in missing:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(content)
            print(f'Restored generated fixture with recorded SHA-256: {target.relative_to(root)}')
