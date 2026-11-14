"""Fixtures shared by every suite."""

from pathlib import Path

import pytest

from scheme_common import audit

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def audit_events():
    """A fresh in-memory audit sink for every test. Use it to read the events a test raised."""
    sink = audit.InMemoryAuditSink()
    previous = audit.configure(sink)
    yield sink
    audit.configure(previous)


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES
