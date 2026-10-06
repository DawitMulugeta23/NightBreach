import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.domains.sandbox.workers.sweeper import (
    DueEnvironment,
    LabSweeper,
)

NOW = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)


def due(n=1):
    return [DueEnvironment(uuid4(), uuid4()) for _ in range(n)]


class FakeTarget:
    def __init__(self, due_items=None, fail_ids=(), find_error=None):
        self.due_items = due_items or []
        self.fail_ids = set(fail_ids)
        self.find_error = find_error
        self.find_calls = []
        self.terminated = []

    async def find_due(self, *, now):
        self.find_calls.append(now)
        if self.find_error is not None:
            raise self.find_error
        return list(self.due_items)

    async def terminate(self, item):
        if item.environment_id in self.fail_ids:
            raise RuntimeError("docker unavailable")
        self.terminated.append(item)


def make_sweeper(target, interval=0.01):
    return LabSweeper(target, interval_seconds=interval, clock=lambda: NOW)


@pytest.mark.asyncio
async def test_sweep_terminates_everything_that_is_due():
    items = due(3)
    target = FakeTarget(items)

    result = await make_sweeper(target).sweep_once()

    assert target.terminated == items
    assert (result.terminated, result.failed) == (3, 0)
    assert target.find_calls == [NOW]


@pytest.mark.asyncio
async def test_sweep_with_nothing_due_does_nothing():
    target = FakeTarget([])

    result = await make_sweeper(target).sweep_once()

    assert target.terminated == []
    assert (result.terminated, result.failed) == (0, 0)


@pytest.mark.asyncio
async def test_one_failing_environment_does_not_block_the_rest():
    first, broken, last = due(3)
    target = FakeTarget([first, broken, last], fail_ids={broken.environment_id})

    result = await make_sweeper(target).sweep_once()

    assert target.terminated == [first, last]
    assert (result.terminated, result.failed) == (2, 1)


@pytest.mark.asyncio
async def test_run_keeps_sweeping_and_survives_lookup_errors():
    target = FakeTarget(find_error=RuntimeError("database down"))
    task = asyncio.create_task(make_sweeper(target).run())

    for _ in range(200):
        if len(target.find_calls) >= 3:
            break
        await asyncio.sleep(0.01)

    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert len(target.find_calls) >= 3
    assert task.cancelled()


@pytest.mark.asyncio
async def test_run_terminates_environments_as_they_become_due():
    target = FakeTarget()
    task = asyncio.create_task(make_sweeper(target).run())

    await asyncio.sleep(0.03)
    assert target.terminated == []

    item = due(1)[0]
    target.due_items = [item]

    for _ in range(200):
        if target.terminated:
            break
        await asyncio.sleep(0.01)

    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert item in target.terminated
