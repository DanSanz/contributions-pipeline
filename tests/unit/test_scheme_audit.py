import json
from datetime import timezone

import pytest

from scheme_common import audit
from scheme_common.audit import JsonLinesAuditSink, record_event


def test_event_goes_to_the_configured_sink(audit_events):
    record_event("member_file_loaded", "SYNTH-F1", "3 rows", actor="svc-test")
    assert [e.event_type for e in audit_events.events] == ["member_file_loaded"]


def test_event_carries_actor_and_rule_id(audit_events):
    event = record_event("rule_fired", "M900001", "detail", actor="svc-test", rule_id="R-1")
    assert (event.actor, event.rule_id) == ("svc-test", "R-1")


def test_actor_and_rule_id_default_to_none(audit_events):
    event = record_event("note", "M900001", "detail")
    assert event.actor is None and event.rule_id is None


def test_actor_is_keyword_only():
    with pytest.raises(TypeError):
        record_event("note", "M900001", "detail", "svc-test")  # type: ignore[misc]


def test_recorded_at_is_utc(audit_events):
    event = record_event("note", "M900001", "detail")
    assert event.recorded_at.tzinfo == timezone.utc


def test_subject_ref_is_required():
    with pytest.raises(ValueError):
        record_event("note", "", "detail")


def test_of_type_filters(audit_events):
    record_event("a", "S1", "")
    record_event("b", "S2", "")
    assert [e.subject_ref for e in audit_events.of_type("b")] == ["S2"]


def test_configure_returns_previous_sink(audit_events):
    other = audit.InMemoryAuditSink()
    previous = audit.configure(other)
    try:
        assert previous is audit_events
        assert audit.current_sink() is other
    finally:
        audit.configure(previous)


def test_json_lines_sink_appends(tmp_path):
    path = tmp_path / "audit.jsonl"
    sink = JsonLinesAuditSink(path)
    previous = audit.configure(sink)
    try:
        record_event("a", "S1", "one", actor="svc-test")
        record_event("b", "S2", "two", rule_id="R-2")
    finally:
        audit.configure(previous)
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert [(line["event_type"], line["actor"], line["rule_id"]) for line in lines] == [
        ("a", "svc-test", None),
        ("b", None, "R-2"),
    ]
