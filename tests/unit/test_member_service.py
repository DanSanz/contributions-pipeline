from member_service import MemberService
from member_store import InMemoryMemberStore
from tests.builders import make_member


def _service(*members):
    store = InMemoryMemberStore()
    for member in members:
        store.upsert(member)
    return MemberService(store)


def test_find_returns_the_member_with_that_reference():
    service = _service(make_member(member_ref="M900201"), make_member(member_ref="M900202"))
    assert service.find("M900202").member_ref == "M900202"


def test_everyone_lists_members_in_reference_order():
    service = _service(make_member(member_ref="M900202"), make_member(member_ref="M900201"))
    assert [m.member_ref for m in service.everyone()] == ["M900201", "M900202"]


def test_how_many_counts_the_members():
    service = _service(make_member(member_ref="M900201"), make_member(member_ref="M900202"))
    assert service.how_many() == 2


def test_exists_is_false_for_an_unknown_reference():
    service = _service(make_member(member_ref="M900201"))
    assert service.exists("M900201")
    assert not service.exists("M900299")
