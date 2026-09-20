"""Exercise documented storage procedure with synthetic hidden input only."""
from pathlib import Path
import contextlib
import getpass
import io
import shlex
import stat
import tempfile
from unittest.mock import patch

ref = Path("skills/knowledge-connect/references/credentials.md").read_text()
line = next(line.strip() for line in ref.splitlines() if line.strip().startswith("python3 -c "))
args = shlex.split(line)
code = args[2]
secret = "synthetic-only-not-real"
with tempfile.TemporaryDirectory() as root:
    output = io.StringIO()
    with patch.object(Path, "home", return_value=Path(root)), patch.object(getpass, "getpass", return_value=secret), contextlib.redirect_stdout(output):
        exec(compile(code, "<documented setup>", "exec"), {})
        target = Path(root)/".config/knowledge-tokens/clickup-work"
        assert target.read_text() == secret
        assert stat.S_IMODE(target.stat().st_mode) == 0o600
        try:
            exec(compile(code, "<documented setup>", "exec"), {})
        except FileExistsError:
            pass
        else:
            raise AssertionError("Existing token must not be overwritten")
        assert target.read_text() == secret
    assert secret not in output.getvalue()
print("Documented private setup: synthetic storage/read-back, permissions and overwrite refusal PASS")
