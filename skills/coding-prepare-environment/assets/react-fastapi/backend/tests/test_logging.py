import json
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app.log import AppFormatter, request_id
from app.main import create_app
from app.settings import Settings


def test_structured_details_redact_nested_secrets_and_exception_values():
    record = logging.LogRecord("worker.example", logging.ERROR, "", 0, "job_failed", (), None)
    record.details = {
        "password": "do-not-leak",
        "nested": {"access_token": "also-private"},
        "payload": {"text": "private-body"},
        "count": 3,
    }
    try:
        raise ValueError("private SQL connection password")
    except ValueError:
        import sys

        record.exc_info = sys.exc_info()
    rendered = AppFormatter("json").format(record)
    entry = json.loads(rendered)
    assert entry["details"]["count"] == 3
    assert entry["error_type"] == "ValueError"
    for secret in ("do-not-leak", "also-private", "private-body", "private SQL"):
        assert secret not in rendered


def test_requests_have_distinct_ids_and_omit_private_urls(tmp_path, capsys):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'test.db'}", log_format="json")
    with TestClient(create_app(settings)) as client:

        def request(_):
            return client.get("/api/health?access_token=private-query").headers["X-Request-ID"]

        with ThreadPoolExecutor(max_workers=4) as executor:
            ids = list(executor.map(request, range(8)))
        assert len(set(ids)) == 8
        assert client.get("/unknown/private-path").status_code == 404
    output = capsys.readouterr().out
    assert "private-query" not in output
    assert "private-path" not in output
    entries = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    correlated = [item for item in entries if item["request_id"] in ids]
    assert len(correlated) == 8
    assert all(item["details"]["status"] == 200 for item in correlated)
    assert request_id.get() == "-"
