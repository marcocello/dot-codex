import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[4]
with tempfile.TemporaryDirectory(prefix='contact-isolation-') as temp:
    db = str(Path(temp) / 'contacts.sqlite')
    def cli(owner, action, *args, success=True):
        result = subprocess.run([sys.executable, str(root / 'contacts.py'), '--db', db, '--owner', owner, action, *args], capture_output=True, text=True, timeout=10)
        assert (result.returncode == 0) == success, (owner, action, result.returncode, result.stderr)
        return result
    owners = {
        'alice': [['Alice Original', 'shared@example.test'], ['Alice Other', 'other@example.test']],
        'bob': [['Bob Original', 'shared@example.test'], ['Bob Secret', 'private@example.test']],
        "owner' OR 1=1 --": [['Quoted Owner', 'quoted@example.test']],
    }
    for owner, records in owners.items():
        for name, email in records:
            cli(owner, 'add', name, email)
    rejected = cli('alice', 'add', 'Replacement Must Not Persist', 'shared@example.test', success=False)
    assert rejected.stderr.strip(), 'Rejected duplicate must provide a diagnostic'
    # Read every owner after the rejected write; replacement and cross-owner pollution fail.
    for owner, expected in {**owners, 'unknown': []}.items():
        listed = json.loads(cli(owner, 'list').stdout)
        assert sorted(listed) == sorted(expected), ('list owner isolation/durable preservation', owner, listed)
        rows = list(csv.reader(io.StringIO(cli(owner, 'export').stdout, newline=''), strict=True))
        assert rows[0] == ['name', 'email']
        assert sorted(rows[1:]) == sorted(expected), ('export owner isolation', owner, rows)
    cli('alice', 'add', 'After Failure', 'after@example.test')
    assert ['After Failure', 'after@example.test'] in json.loads(cli('alice', 'list').stdout), 'Normal add must remain usable after rejection'
print('PASS: real CLI owner separation, shared email, duplicate rejection/preservation and recovery')
