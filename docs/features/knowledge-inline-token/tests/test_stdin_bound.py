"""Regression: never persist a truncated, whitespace-prefixed stdin token."""
import subprocess
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    config = Path(directory) / 'knowledge.toml'
    command = [sys.executable, 'skills/knowledge-connect/scripts/knowledge_profile.py', '--config', str(config)]
    subprocess.run(command + ['put', 'work', '--provider', 'clickup', '--connection', 'work', '--account', '1', '--workspace-id', '2'], check=True, capture_output=True)
    before = config.read_bytes()
    result = subprocess.run(command + ['credentials', 'work', '--token-stdin'], input=' ' * 16385 + 'xMORE', text=True, capture_output=True)
    assert result.returncode != 0, result.stdout
    assert config.read_bytes() == before
    assert 'xMORE' not in result.stdout + result.stderr
print('PASS: oversized stdin rejected without mutation or disclosure')

with tempfile.TemporaryDirectory() as directory:
    config = Path(directory) / 'knowledge.toml'
    command = [sys.executable, 'skills/knowledge-connect/scripts/knowledge_profile.py', '--config', str(config)]
    subprocess.run(command + ['put', 'work', '--provider', 'clickup', '--connection', 'work', '--account', '1', '--workspace-id', '2', '--token-env', 'TEST_TOKEN', '--auth-type', 'oauth'], check=True, capture_output=True)
    subprocess.run(command + ['credentials', 'work', '--token-stdin'], input='synthetic-token', text=True, check=True, capture_output=True)
    import tomllib
    assert tomllib.loads(config.read_text())['profiles']['work']['auth_type'] == 'oauth'
print('PASS: inline replacement preserves OAuth authentication type')
