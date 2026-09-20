"""Additional regressions for shell-default parity and invalid TOML characters."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

CLI = Path(__file__).resolve().parents[4] / 'scripts/knowledge_profile.py'
with tempfile.TemporaryDirectory() as tmp:
    home = Path(tmp)
    env = dict(os.environ, HOME=tmp, CODEX_HOME='')
    command = [sys.executable, str(CLI)]
    subprocess.run(command + ['put', 'disabled', '--provider', 'none', '--default'],
                   env=env, check=True, capture_output=True)
    config = home / '.codex/knowledge.toml'
    assert config.is_file(), 'Empty CODEX_HOME must use the shell-compatible home fallback'
    before = config.read_bytes()
    result = subprocess.run(command + ['put', 'bad', '--provider', 'markdown',
                                      '--root', str(home / 'invalid\x7fpath')],
                            env=env, capture_output=True)
    assert result.returncode != 0, 'DEL cannot be encoded as a TOML literal character'
    assert config.read_bytes() == before
print('Environment fallback and invalid-character preservation: PASS')
