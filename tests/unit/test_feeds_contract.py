import pytest

from feeds import FeedError
from feeds._contract import check_contract_version, record_type_for, to_record
from generated import ContributionRecord, MemberRecord

MEMBER_FIELDS = ["E90001", "M900101", "QQ100101A", "Synthetic", "Alex", "14/03/1981", "01/09/2015", "41250.00"]


def test_feed_type_selects_the_record_type():
    assert record_type_for("MEMBERS", 1) is MemberRecord
    assert record_type_for("CONTRIB", 1) is ContributionRecord


def test_unknown_feed_type():
    with pytest.raises(FeedError, match="unknown feed type"):
        record_type_for("PENSIONERS", 1)


def test_fields_map_in_contract_order():
    record = to_record(MemberRecord, MEMBER_FIELDS, 2, strict=True)
    assert record.member_ref == "M900101"
    assert record.date_of_birth == "14/03/1981"


def test_values_are_trimmed():
    fields = [f" {value} " for value in MEMBER_FIELDS]
    assert to_record(MemberRecord, fields, 2, strict=True).surname == "Synthetic"


def test_date_of_birth_is_kept_as_text_even_when_invalid():
    fields = MEMBER_FIELDS[:5] + ["31/02/1980"] + MEMBER_FIELDS[6:]
    assert to_record(MemberRecord, fields, 2, strict=True).date_of_birth == "31/02/1980"


def test_too_few_fields():
    with pytest.raises(FeedError, match="expected 8 fields, found 7"):
        to_record(MemberRecord, MEMBER_FIELDS[:-1], 2, strict=False)


def test_extra_fields_rejected_when_strict():
    with pytest.raises(FeedError, match="strict schema"):
        to_record(MemberRecord, MEMBER_FIELDS + ["PT"], 2, strict=True)


def test_extra_fields_dropped_when_not_strict():
    record = to_record(MemberRecord, MEMBER_FIELDS + ["PT"], 2, strict=False)
    assert record.salary == "41250.00"


def test_required_field_empty():
    fields = MEMBER_FIELDS[:2] + [""] + MEMBER_FIELDS[3:]
    with pytest.raises(FeedError, match="ni_number is empty"):
        to_record(MemberRecord, fields, 2, strict=True)


def test_optional_field_may_be_empty():
    fields = ["E90001", "PAY01", "2026-09", "10.00", "0.00", "", "99-00-01", "00000001"]
    assert to_record(ContributionRecord, fields, 2, strict=True).paid_on == ""


def test_error_names_the_field_not_the_value():
    fields = MEMBER_FIELDS[:2] + [""] + MEMBER_FIELDS[3:]
    with pytest.raises(FeedError) as caught:
        to_record(MemberRecord, fields, 2, strict=True)
    assert "QQ" not in str(caught.value) and "14/03/1981" not in str(caught.value)


def test_same_major_version_accepted():
    check_contract_version("3.0", 1)


def test_other_major_version_rejected():
    with pytest.raises(FeedError, match="contract version 2.4"):
        check_contract_version("2.4", 1)
