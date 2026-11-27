import datetime as dt
import logging

from scheme_common.dates import parse_uk_date
from tests.builders import make_member
from valuation_extract import eligible_members, joined_in_year, service_days

AS_AT = dt.date(2026, 3, 31)


def _refs(members):
    return [m.member_ref for m in members]


def test_a_member_who_joined_after_the_as_at_date_is_left_out():
    members = [
        make_member(member_ref="M900401", date_joined="01/09/2015"),
        make_member(member_ref="M900402", date_joined="01/04/2026"),
    ]
    assert _refs(eligible_members(members, AS_AT)) == ["M900401"]


def test_a_member_who_joined_on_the_as_at_date_is_eligible():
    member = make_member(member_ref="M900411", date_joined="31/03/2026")
    as_at = parse_uk_date(member.date_joined)
    assert _refs(eligible_members([member], as_at)) == ["M900411"]


def test_a_member_who_joined_the_day_before_the_as_at_date_is_eligible():
    member = make_member(member_ref="M900421", date_joined="01/04/2026")
    as_at = parse_uk_date(member.date_joined) + dt.timedelta(days=1)
    assert _refs(eligible_members([member], as_at)) == ["M900421"]


def test_a_member_who_joined_the_day_after_the_as_at_date_is_left_out():
    member = make_member(member_ref="M900431", date_joined="31/03/2026")
    as_at = parse_uk_date(member.date_joined) - dt.timedelta(days=1)
    assert eligible_members([member], as_at) == []


def test_a_member_whose_date_joined_cannot_be_read_is_kept():
    members = [make_member(member_ref="M900441", date_joined="31/02/2026")]
    assert _refs(eligible_members(members, AS_AT)) == ["M900441"]


def test_logs_how_many_members_are_eligible(caplog):
    members = [
        make_member(member_ref="M900451", date_joined="01/09/2015"),
        make_member(member_ref="M900452", date_joined="01/04/2026"),
    ]
    with caplog.at_level(logging.INFO):
        eligible_members(members, AS_AT)
    assert "1 of 2 members eligible at 31/03/2026" in caplog.messages


def test_service_days_counts_the_days_since_the_member_joined():
    member = make_member(member_ref="M900461", date_joined="01/09/2015")
    assert service_days(member, AS_AT) == 3864


def test_service_days_is_zero_on_the_day_the_member_joined():
    member = make_member(member_ref="M900462", date_joined="31/03/2026")
    assert service_days(member, AS_AT) == 0


def test_a_member_is_a_new_entrant_only_in_the_year_they_joined():
    member = make_member(member_ref="M900471", date_joined="01/09/2015")
    assert joined_in_year(member, 2015)
    assert not joined_in_year(member, 2016)
