import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[4]
with tempfile.TemporaryDirectory(prefix='contact-journey-') as temp:
    db = str(Path(temp) / 'contacts.sqlite')
    def cli(action, *args, owner='alice'):
        result = subprocess.run([sys.executable, str(root / 'contacts.py'), '--db', db, '--owner', owner, action, *args], capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, (action, result.returncode, result.stderr)
        return result.stdout
    def exported(owner='alice'):
        return list(csv.reader(io.StringIO(cli('export', owner=owner), newline=''), strict=True))
    assert exported() == [['name', 'email']], 'First-use export must contain only the header'
    assert json.loads(cli('list')) == [], 'First-use list must be empty'
    expected = [
        ['Ada Lovelace', 'ada@example.test'],
        ['Doe, "Mira"\nSecond line', 'mira@example.test'],
        ['Zoë 東京', 'zoe@example.test'],
    ]
    for name, email in expected:
        cli('add', name, email)
    # No in-process application calls: every read-back is a newly launched CLI.
    assert sorted(json.loads(cli('list'))) == sorted(expected), 'Saved records must survive process restart'
    rows = exported()
    assert rows[0] == ['name', 'email'], 'CSV schema header'
    assert sorted(rows[1:]) == sorted(expected), 'CSV must preserve names, quoting, comma, newline and Unicode'
    assert exported('empty-owner') == [['name', 'email']], 'Empty owner in populated database must export header only'
print('PASS: real CLI first use, persisted save/reopen, CSV parsing and empty-owner export')
