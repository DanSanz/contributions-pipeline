from decimal import Decimal

import pytest

from member_store import InMemoryMemberStore, SqliteMemberStore, load_members, member_from_record
from tests.builders import make_member, make_member_record


@pytest.fixture(params=["memory", "sqlite"])
def store(request):
    if request.param == "memory":
        yield InMemoryMemberStore()
    else:
        sqlite_store = SqliteMemberStore(":memory:")
        yield sqlite_store
        sqlite_store.close()


def test_upsert_then_get(store):
    store.upsert(make_member())
    assert store.get("M900001") == make_member()


def test_upsert_replaces_by_member_ref(store):
    store.upsert(make_member(salary=Decimal("1.00")))
    store.upsert(make_member(salary=Decimal("2.00")))
    assert store.count() == 1
    assert store.get("M900001").salary == Decimal("2.00")


def test_all_is_ordered_by_member_ref(store):
    store.upsert(make_member(member_ref="M900002"))
    store.upsert(make_member(member_ref="M900001"))
    assert [m.member_ref for m in store.all()] == ["M900001", "M900002"]


def test_get_missing_is_none(store):
    assert store.get("M999999") is None


def test_load_members_counts_rows(store):
    records = [make_member_record(member_ref=f"M90000{i}") for i in range(3)]
    assert load_members(store, records, file_id="SYNTH-F") == 3
    assert store.get("M900002").source_file_id == "SYNTH-F"


def test_date_of_birth_is_stored_as_received():
    member = member_from_record(make_member_record(date_of_birth="31/02/1980"), file_id="SYNTH-F")
    assert member.date_of_birth == "31/02/1980"


def test_bad_salary_error_has_no_value():
    with pytest.raises(ValueError) as caught:
        member_from_record(make_member_record(salary="12,5O0"), file_id="SYNTH-F")
    assert "12,5O0" not in str(caught.value)
