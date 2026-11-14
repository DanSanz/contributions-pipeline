"""Audit events for the scheme's data pipelines.

Every event goes to the sink installed with ``configure``. In production the job installs
the audit service sink; tests and local runs use InMemoryAuditSink or JsonLinesAuditSink.

The audit store is readable by the service desk, so ``detail`` must never contain personal
data (dates of birth, NI numbers, names, bank details). Refer to a member by member reference.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    subject_ref: str
    detail: str
    actor: str | None
    rule_id: str | None
    recorded_at: datetime

    def to_json(self) -> str:
        data = asdict(self)
        data["recorded_at"] = self.recorded_at.isoformat()
        return json.dumps(data, sort_keys=True)


class AuditSink(Protocol):
    def write(self, event: AuditEvent) -> None: ...


class InMemoryAuditSink:
    """Keeps events in a list. For tests and dry runs."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def write(self, event: AuditEvent) -> None:
        self.events.append(event)

    def of_type(self, event_type: str) -> list[AuditEvent]:
        return [event for event in self.events if event.event_type == event_type]

    def clear(self) -> None:
        self.events.clear()


class JsonLinesAuditSink:
    """Appends one JSON object per event to a file. For local runs."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def write(self, event: AuditEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")


class _UnconfiguredSink:
    """Drops events. Warns once, so a job that forgot to call configure() shows it in its log."""

    def __init__(self) -> None:
        self._warned = False

    def write(self, event: AuditEvent) -> None:
        if not self._warned:
            logger.warning("No audit sink configured; audit events are being dropped")
            self._warned = True


_lock = threading.Lock()
_sink: AuditSink = _UnconfiguredSink()
_clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc)


def configure(sink: AuditSink) -> AuditSink:
    """Install ``sink`` for this process. Returns the sink it replaced."""
    global _sink
    with _lock:
        previous, _sink = _sink, sink
    return previous


def current_sink() -> AuditSink:
    return _sink


def record_event(
    event_type: str,
    subject_ref: str,
    detail: str,
    *,
    actor: str | None = None,
    rule_id: str | None = None,
) -> AuditEvent:
    """Record one audit event and return it.

    ``actor`` is the person or service account responsible for the action. ``rule_id`` names
    the business rule that caused it, where one did. The quarterly audit check fails events
    raised by a rule that do not carry both.
    """
    if not event_type or not subject_ref:
        raise ValueError("event_type and subject_ref are required")
    event = AuditEvent(event_type, subject_ref, detail, actor, rule_id, _clock())
    with _lock:
        _sink.write(event)
    return event
