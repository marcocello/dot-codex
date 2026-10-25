"""Track and cancel active native-harness subprocesses."""

from __future__ import annotations

import asyncio
import contextlib
from dataclasses import dataclass

from telegram_to_agents.infra.process_tree import (
    force_kill_process_tree,
    interrupt_process,
    terminate_process_tree,
)


@dataclass(slots=True)
class TrackedProcess:
    process: asyncio.subprocess.Process
    chat_id: int
    topic_id: int | None = None


class ProcessRegistry:
    """Own process state for `/stop`, `/stop_all`, and `/interrupt`."""

    def __init__(self) -> None:
        self._processes: dict[int, list[TrackedProcess]] = {}
        self._aborted_topics: set[tuple[int, int | None]] = set()
        self._lock = asyncio.Lock()

    def register(
        self,
        chat_id: int,
        process: asyncio.subprocess.Process,
        *,
        topic_id: int | None = None,
    ) -> TrackedProcess:
        tracked = TrackedProcess(process, chat_id, topic_id)
        self._processes.setdefault(chat_id, []).append(tracked)
        return tracked

    def unregister(self, tracked: TrackedProcess) -> None:
        entries = self._processes.get(tracked.chat_id, [])
        with contextlib.suppress(ValueError):
            entries.remove(tracked)
        if not entries:
            self._processes.pop(tracked.chat_id, None)

    async def kill_by_chat_topic(self, chat_id: int, topic_id: int | None) -> int:
        async with self._lock:
            entries = self._processes.get(chat_id, [])
            targets = [item for item in entries if item.topic_id == topic_id]
            if not targets:
                return 0
            self._aborted_topics.add((chat_id, topic_id))
            self._remove(chat_id, targets)
        return await _kill_processes(targets)

    async def kill_all_active(self) -> int:
        async with self._lock:
            targets = [item for entries in self._processes.values() for item in entries]
            self._processes.clear()
            self._aborted_topics.update((item.chat_id, item.topic_id) for item in targets)
        return await _kill_processes(targets)

    def interrupt_all(self, chat_id: int) -> int:
        count = 0
        for tracked in self._processes.get(chat_id, []):
            if tracked.process.returncode is None:
                self._aborted_topics.add((tracked.chat_id, tracked.topic_id))
                interrupt_process(tracked.process.pid)
                count += 1
        return count

    def was_aborted_topic(self, chat_id: int, topic_id: int | None) -> bool:
        return (chat_id, topic_id) in self._aborted_topics

    def clear_topic_abort(self, chat_id: int, topic_id: int | None) -> None:
        self._aborted_topics.discard((chat_id, topic_id))

    def has_active(self, chat_id: int, topic_id: int | None = None) -> bool:
        entries = self._processes.get(chat_id, [])
        return any(
            item.process.returncode is None and (topic_id is None or item.topic_id == topic_id)
            for item in entries
        )

    def _remove(self, chat_id: int, targets: list[TrackedProcess]) -> None:
        target_ids = {id(item) for item in targets}
        remaining = [
            item for item in self._processes.get(chat_id, []) if id(item) not in target_ids
        ]
        if remaining:
            self._processes[chat_id] = remaining
        else:
            self._processes.pop(chat_id, None)


async def _kill_processes(entries: list[TrackedProcess]) -> int:
    live = [item for item in entries if item.process.returncode is None]
    for tracked in live:
        _close_stdin(tracked.process)
        with contextlib.suppress(ProcessLookupError):
            terminate_process_tree(tracked.process.pid)
    if live:
        await asyncio.sleep(0.25)
    for tracked in live:
        if tracked.process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                force_kill_process_tree(tracked.process.pid)
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(tracked.process.wait(), timeout=2.0)
    return len(live)


def _close_stdin(process: asyncio.subprocess.Process) -> None:
    stdin = process.stdin
    if stdin is not None:
        with contextlib.suppress(OSError, RuntimeError, ValueError):
            stdin.close()
