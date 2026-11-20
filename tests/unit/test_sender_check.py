from pathlib import Path

from feeds import read_file, read_header
from sender_check import rows_for_other_employers
from tests.builders import make_member_record

MIXED = Path(__file__).parent.parent / "fixtures" / "members_E90012_20261116_mixed.txt"


def test_a_file_with_only_the_senders_rows_gives_an_empty_list():
    rows = [
        make_member_record(employer_id="E90001", member_ref="M900001"),
        make_member_record(employer_id="E90001", member_ref="M900002"),
        make_member_record(employer_id="E90001", member_ref="M900003"),
    ]
    assert rows_for_other_employers("E90001", rows) == []


def test_a_row_for_another_employer_is_returned_by_member_reference():
    rows = [
        make_member_record(employer_id="E90001", member_ref="M900001"),
        make_member_record(employer_id="E90002", member_ref="M900002"),
    ]
    assert rows_for_other_employers("E90001", rows) == ["M900002"]


def test_rows_are_returned_in_file_order():
    rows = [
        make_member_record(employer_id="E90003", member_ref="M900009"),
        make_member_record(employer_id="E90001", member_ref="M900001"),
        make_member_record(employer_id="E90002", member_ref="M900004"),
    ]
    assert rows_for_other_employers("E90001", rows) == ["M900009", "M900004"]


def test_the_mixed_fixture_has_one_row_for_another_employer():
    header = read_header(MIXED)
    assert rows_for_other_employers(header.sender_id, read_file(MIXED)) == ["M901301"]
