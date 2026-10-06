"""Single-use, short-lived tickets that authorise one terminal connection.

A ticket is issued over the normal authenticated API and redeemed once on the
WebSocket, so the access token never travels in a URL. The store is in memory:
it is correct for a single API process; use a shared store for several.
"""
from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass
from typing import Callable
from uuid import UUID

DEFAULT_TTL_SECONDS = 30
DEFAULT_MAX_OUTSTANDING = 1000


@dataclass(frozen=True)
class TerminalTicket:
    learner_id: UUID
    environment_id: UUID
    machine_name: str
    runtime_machine_id: str
    expires_at: float


class TerminalTicketStore:
    def __init__(
        self,
        *,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        max_outstanding: int = DEFAULT_MAX_OUTSTANDING,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.ttl_seconds = ttl_seconds
        self.max_outstanding = max_outstanding
        self._clock = clock
        self._tickets: dict[str, TerminalTicket] = {}
        self._lock = threading.Lock()

    def _purge_expired(self, now: float) -> None:
        for key in [k for k, t in self._tickets.items() if t.expires_at <= now]:
            del self._tickets[key]

    def issue(
        self,
        *,
        learner_id: UUID,
        environment_id: UUID,
        machine_name: str,
        runtime_machine_id: str,
    ) -> str:
        now = self._clock()

        with self._lock:
            self._purge_expired(now)

            if len(self._tickets) >= self.max_outstanding:
                raise RuntimeError("Too many outstanding terminal tickets.")

            ticket_id = secrets.token_urlsafe(32)
            self._tickets[ticket_id] = TerminalTicket(
                learner_id=learner_id,
                environment_id=environment_id,
                machine_name=machine_name,
                runtime_machine_id=runtime_machine_id,
                expires_at=now + self.ttl_seconds,
            )

        return ticket_id

    def redeem(self, ticket_id: str) -> TerminalTicket | None:
        """Return the ticket and invalidate it, or None if unknown/expired/used."""
        with self._lock:
            ticket = self._tickets.pop(ticket_id, None)

        if ticket is None or ticket.expires_at <= self._clock():
            return None

        return ticket

    def clear(self) -> None:
        with self._lock:
            self._tickets.clear()


ticket_store = TerminalTicketStore()
