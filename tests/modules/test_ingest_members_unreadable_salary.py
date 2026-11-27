"""A member file with a salary that cannot be read is rejected whole, and the job carries on."""

from dataclasses import astuple

import pytest

from feeds import FeedError
from member_store import InMemoryMemberStore, SqliteMemberStore
from pipeline import settings
from pipeline.ingest_members import ingest_file, main
from tests.builders import make_member_record

BAD_SALARY = "41,250.00"


def _member_file(tmp_path, name, rows):
    lines = [f"HDR|MEMBERS|E90001|SYNTH-M-{name}|09/11/2026|3.1"]
    lines += ["DTL|" + "|".join(astuple(row)) for row in rows]
    lines.append(f"TRL|{len(rows)}")
    path = tmp_path / f"{name}.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_a_file_with_an_unreadable_salary_loads_nothing(tmp_path):
    path = _member_file(tmp_path, "BAD", [
        make_member_record(member_ref="M900001"),
        make_member_record(member_ref="M900002", salary=BAD_SALARY),
        make_member_record(member_ref="M900003"),
    ])
    store = InMemoryMemberStore()
    with pytest.raises(FeedError):
        ingest_file(path, store)
    assert store.count() == 0


def test_the_job_carries_on_after_a_file_with_an_unreadable_salary(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "AUDIT_LOG_PATH", tmp_path / "audit.jsonl")
    bad = _member_file(tmp_path, "BAD", [make_member_record(salary=BAD_SALARY)])
    good = _member_file(tmp_path, "GOOD", [make_member_record(member_ref="M900009")])
    db = tmp_path / "members.sqlite"
    assert main([str(bad), str(good), "--db", str(db)]) == 1
    assert SqliteMemberStore(db).get("M900009") is not None
