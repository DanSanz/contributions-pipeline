from datetime import date, datetime

from employer_reports import joiners_report
from member_service import MemberService
from member_store import InMemoryMemberStore
from tests.builders import make_member

START = date(2026, 11, 1)
END = date(2026, 11, 30)


def _service(*members):
    store = InMemoryMemberStore()
    for member in members:
        store.upsert(member)
    return MemberService(store)


def test_lists_members_who_joined_in_the_range_oldest_first():
    service = _service(
        make_member(member_ref="M900301", date_joined="20/11/2026"),
        make_member(member_ref="M900302", date_joined="15/10/2026"),
        make_member(member_ref="M900303", date_joined="02/11/2026"),
    )
    report = joiners_report(service, "E90001", START, END)
    assert report.rows == [["M900303", "02/11/2026"], ["M900301", "20/11/2026"]]


def test_leaves_out_members_of_other_employers():
    ours = make_member(member_ref="M900311", employer_id="E90001", date_joined="10/11/2026")
    theirs = make_member(member_ref="M900312", employer_id="E90002", date_joined="10/11/2026")
    joined = datetime.strptime(ours.date_joined, "%d/%m/%Y").date()
    report = joiners_report(_service(ours, theirs), "E90001", joined, joined)
    assert [row[0] for row in report.rows] == ["M900311"]


def test_start_date_is_included():
    member = make_member(member_ref="M900321", date_joined="01/11/2026")
    start = datetime.strptime(member.date_joined, "%d/%m/%Y").date()
    report = joiners_report(_service(member), "E90001", start, END)
    assert report.rows == [["M900321", "01/11/2026"]]


def test_end_date_is_included():
    member = make_member(member_ref="M900331", date_joined="01/12/2026")
    end = datetime.strptime(member.date_joined, "%d/%m/%Y").date()
    report = joiners_report(_service(member), "E90001", START, end)
    assert report.rows == [["M900331", "01/12/2026"]]


def test_rows_carry_no_personal_data():
    service = _service(make_member(member_ref="M900341", date_joined="05/11/2026"))
    report = joiners_report(service, "E90001", START, END)
    assert report.rows[0] == ["M900341", "05/11/2026"]
    assert "Synthetic" not in report.rows[0] and "QQ100001A" not in report.rows[0]
