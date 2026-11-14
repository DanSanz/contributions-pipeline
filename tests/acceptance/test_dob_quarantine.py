"""Acceptance tests: DOB quarantine spec v2, task T1 (criteria 1 and 2, and the constraints).

Written by the team before T1 starts; they fail until T1 is done. Tests for T2-T5 are added
with those tasks. All data here is synthetic.
"""

import logging
from datetime import date

import pytest

from dob_quarantine import validate_file
from member_store import InMemoryMemberStore
from pipeline import settings
from pipeline.ingest_members import ingest_file
from tests.builders import make_member_record

FILE_DATE = date(2026, 11, 2)


# Criterion 1: an unparseable DOB is quarantined with DOB-01.

def test_unparseable_dob_quarantined():
    row = make_member_record(member_ref="M900001", date_of_birth="31/02/1980")
    result = validate_file([row], FILE_DATE)
    assert result.accepted == []
    assert [(q.row, q.rule_id) for q in result.quarantined] == [(row, "DOB-01")]


@pytest.mark.parametrize(
    "raw",
    ["29/02/1981", "03/14/1981", "1981-03-14", "14/03/81", ""],
    ids=["not-a-leap-year", "month-first", "iso", "two-digit-year", "empty"],
)
def test_dob_not_a_real_dd_mm_yyyy_date_is_dob_01(raw):
    row = make_member_record(date_of_birth=raw)
    result = validate_file([row], FILE_DATE)
    assert [q.rule_id for q in result.quarantined] == ["DOB-01"]


# Criterion 2: a valid row continues unchanged.

def test_valid_row_continues_unchanged():
    row = make_member_record(date_of_birth="14/03/1981")  # day over 12: wrong if read month first
    result = validate_file([row], FILE_DATE)
    assert result.quarantined == []
    assert result.accepted == [row]
    assert result.accepted[0] is row


def test_leap_day_in_a_leap_year_is_valid():
    result = validate_file([make_member_record(date_of_birth="29/02/1988")], FILE_DATE)
    assert result.quarantined == []


def test_valid_rows_continue_in_order_around_a_quarantined_row():
    rows = [
        make_member_record(member_ref="M900001", date_of_birth="14/03/1981"),
        make_member_record(member_ref="M900002", date_of_birth="31/02/1980"),
        make_member_record(member_ref="M900003", date_of_birth="23/08/1979"),
    ]
    result = validate_file(rows, FILE_DATE)
    assert [row.member_ref for row in result.accepted] == ["M900001", "M900003"]
    assert [q.row.member_ref for q in result.quarantined] == ["M900002"]


# Constraints: every quarantine is audited with actor and rule ID; no personal data leaks.

def test_quarantine_is_audited_with_actor_and_rule_id(audit_events):
    validate_file([make_member_record(member_ref="M900001", date_of_birth="31/02/1980")], FILE_DATE)
    [event] = audit_events.of_type("dob_quarantined")
    assert event.subject_ref == "M900001"
    assert event.rule_id == "DOB-01"
    assert event.actor == settings.AUDIT_ACTOR


def test_no_dob_or_ni_number_in_logs_or_audit(caplog, audit_events):
    row = make_member_record(member_ref="M900001", ni_number="QQ123456C", date_of_birth="31/02/1980")
    with caplog.at_level(logging.DEBUG):
        validate_file([row], FILE_DATE)
    recorded = caplog.text + " ".join(f"{e.subject_ref} {e.detail}" for e in audit_events.events)
    assert "31/02/1980" not in recorded
    assert "QQ123456C" not in recorded


# Tracer: the nightly member job holds the row back and loads the rest.

def test_ingest_loads_valid_members_and_holds_back_dob_01(fixtures_dir, audit_events):
    store = InMemoryMemberStore()
    ingest_file(fixtures_dir / "members_E90004_20261102_dob.txt", store)
    assert [member.member_ref for member in store.all()] == ["M940001", "M940003"]
    assert [e.subject_ref for e in audit_events.of_type("dob_quarantined")] == ["M940002"]
