import asyncio

# Maps session_id -> asyncio.Task scheduled to tear down that session's container.
# In-memory only: fine for a single backend process, would need a shared store
# (e.g. Redis) if the backend ever runs as multiple processes/workers.
_pending_teardowns: dict[str, asyncio.Task] = {}


def schedule_teardown(session_id: str, coro_factory, delay_seconds: float) -> None:
    """
    Schedules `coro_factory()` to run after `delay_seconds`, unless cancelled
    first via cancel_teardown(session_id).
    """
    cancel_teardown(session_id)  # replace any existing pending teardown

    async def _delayed():
        try:
            await asyncio.sleep(delay_seconds)
            await coro_factory()
        except asyncio.CancelledError:
            pass
        finally:
            _pending_teardowns.pop(session_id, None)

    _pending_teardowns[session_id] = asyncio.create_task(_delayed())


def cancel_teardown(session_id: str) -> bool:
    """Cancels a pending teardown if one exists. Returns True if one was cancelled."""
    task = _pending_teardowns.pop(session_id, None)
    if task is not None and not task.done():
        task.cancel()
        return True
    return False
