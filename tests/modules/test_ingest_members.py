"""The nightly member ingestion job, end to end, with an in-memory store."""

import pytest

from feeds import FeedError
from member_store import InMemoryMemberStore, SqliteMemberStore
from pipeline import settings
from pipeline.ingest_members import ingest_file, main


def test_loads_every_member(fixtures_dir):
    store = InMemoryMemberStore()
    summary = ingest_file(fixtures_dir / "members_E90001_20261102.txt", store)
    assert (summary.rows_read, summary.loaded) == (8, 8)
    assert store.count() == 8


def test_member_keeps_its_source_file(fixtures_dir):
    store = InMemoryMemberStore()
    ingest_file(fixtures_dir / "members_E90001_20261102.txt", store)
    assert store.get("M900104").source_file_id == "SYNTH-M-E90001-20261102"


def test_load_is_audited_with_the_service_actor(fixtures_dir, audit_events):
    ingest_file(fixtures_dir / "members_E90001_20261102.txt", InMemoryMemberStore())
    [event] = audit_events.of_type("member_file_loaded")
    assert event.subject_ref == "SYNTH-M-E90001-20261102"
    assert event.actor == settings.AUDIT_ACTOR


def test_reloading_a_file_does_not_duplicate_members(fixtures_dir):
    store = InMemoryMemberStore()
    ingest_file(fixtures_dir / "members_E90001_20261102.txt", store)
    ingest_file(fixtures_dir / "members_E90001_20261102.txt", store)
    assert store.count() == 8


def test_contribution_file_is_refused(fixtures_dir):
    with pytest.raises(ValueError, match="not MEMBERS"):
        ingest_file(fixtures_dir / "contributions_E90001_202609.txt", InMemoryMemberStore())


def test_bad_file_loads_nothing(fixtures_dir):
    store = InMemoryMemberStore()
    with pytest.raises(FeedError):
        ingest_file(fixtures_dir / "members_E90002_bad_trailer.txt", store)
    assert store.count() == 0


def test_works_with_the_sqlite_store(fixtures_dir):
    store = SqliteMemberStore(":memory:")
    ingest_file(fixtures_dir / "members_E90001_20261102.txt", store)
    assert store.get("M900107").date_of_birth == "29/02/1988"


def test_main_reports_a_rejected_file(fixtures_dir, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(settings, "AUDIT_LOG_PATH", tmp_path / "audit.jsonl")
    code = main([
        str(fixtures_dir / "members_E90001_20261102.txt"),
        str(fixtures_dir / "members_E90002_bad_trailer.txt"),
        "--db", str(tmp_path / "members.sqlite"),
    ])
    assert code == 1
    assert "SYNTH-M-E90001-20261102: 8 of 8 rows loaded" in capsys.readouterr().out


def test_an_empty_member_file_loads_nothing_and_is_not_rejected(fixtures_dir):
    store = InMemoryMemberStore()
    summary = ingest_file(fixtures_dir / "no_members_E90009_20261102.txt", store)
    assert (summary.rows_read, summary.loaded) == (0, 0)
    assert store.count() == 0
