"""Safety fixtures for the focused gateway tests."""

from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def _no_real_process_signals() -> object:
    """Never signal real host processes from tests."""
    with (
        patch("telegram_to_agents.cli.process_registry.terminate_process_tree", return_value=None),
        patch("telegram_to_agents.cli.process_registry.force_kill_process_tree", return_value=None),
        patch("telegram_to_agents.cli.process_registry.interrupt_process", return_value=None),
        patch("telegram_to_agents.cli.executor.force_kill_process_tree", return_value=None),
        patch("telegram_to_agents.infra.pidlock.terminate_process_tree", return_value=None),
        patch("telegram_to_agents.infra.pidlock.force_kill_process_tree", return_value=None),
        patch("telegram_to_agents.infra.pidlock.list_process_descendants", return_value=[]),
    ):
        yield
