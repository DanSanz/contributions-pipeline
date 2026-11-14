"""feeds, tested at its interface: read_header and read_file on whole files."""

from datetime import date

import pytest

from feeds import FeedError, read_file, read_header
from generated import ContributionRecord, MemberRecord
from pipeline import settings


def test_header(fixtures_dir):
    header = read_header(fixtures_dir / "members_E90001_20261102.txt")
    assert header.feed_type == "MEMBERS"
    assert header.sender_id == "E90001"
    assert header.file_date == date(2026, 11, 2)


def test_member_file_yields_member_records(fixtures_dir):
    rows = list(read_file(fixtures_dir / "members_E90001_20261102.txt"))
    assert len(rows) == 8
    assert all(isinstance(row, MemberRecord) for row in rows)


def test_contribution_file_yields_contribution_records(fixtures_dir):
    rows = list(read_file(fixtures_dir / "contributions_E90001_202609.txt"))
    assert [row.payroll_id for row in rows] == ["PAY01", "PAY02", "PAY03", "PAY04"]
    assert all(isinstance(row, ContributionRecord) for row in rows)


def test_values_are_trimmed(fixtures_dir):
    rows = list(read_file(fixtures_dir / "members_E90001_20261102.txt"))
    assert rows[-1].date_of_birth == "13/10/1992"


def test_empty_optional_value(fixtures_dir):
    rows = list(read_file(fixtures_dir / "contributions_E90001_202609.txt"))
    assert rows[-1].paid_on == ""


def test_extra_column_rejected_under_strict_schema(fixtures_dir):
    assert settings.STRICT_SCHEMA is True
    with pytest.raises(FeedError, match="strict schema"):
        list(read_file(fixtures_dir / "members_E90001_extra_column.txt"))


def test_extra_column_dropped_when_strict_is_off(fixtures_dir):
    rows = list(read_file(fixtures_dir / "members_E90001_extra_column.txt", strict=False))
    assert [row.salary for row in rows] == ["41250.00", "52300.50", "33800.00"]


def test_trailer_count_mismatch_fails_before_any_row(fixtures_dir):
    with pytest.raises(FeedError, match="trailer says 4 detail records, file has 3"):
        read_file(fixtures_dir / "members_E90002_bad_trailer.txt")


def test_cp1252_file_is_read(fixtures_dir):
    [row] = read_file(fixtures_dir / "members_E90003_cp1252.txt")
    assert row.forenames == "Zoë"


def test_missing_trailer(tmp_path):
    path = tmp_path / "truncated.txt"
    path.write_text(
        "HDR|MEMBERS|E90009|SYNTH-T|02/11/2026|3.1\n"
        "DTL|E90009|M990001|QQ900001A|Synthetic|Alex|14/03/1981|01/09/2015|100.00\n",
        encoding="utf-8",
    )
    with pytest.raises(FeedError, match="no trailer"):
        read_header(path)


def test_empty_file(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("\n", encoding="utf-8")
    with pytest.raises(FeedError, match="empty"):
        read_header(path)


def test_wrong_contract_major(tmp_path):
    path = tmp_path / "old.txt"
    path.write_text("HDR|MEMBERS|E90009|SYNTH-T|02/11/2026|2.9\nTRL|0\n", encoding="utf-8")
    with pytest.raises(FeedError, match="contract version 2.9"):
        read_header(path)


def test_error_carries_file_and_line_but_no_values(tmp_path):
    path = tmp_path / "short.txt"
    path.write_text(
        "HDR|MEMBERS|E90009|SYNTH-T|02/11/2026|3.1\n"
        "DTL|E90009|M990001|QQ900001A|Synthetic|Alex|14/03/1981\n"
        "TRL|1\n",
        encoding="utf-8",
    )
    with pytest.raises(FeedError) as caught:
        list(read_file(path))
    message = str(caught.value)
    assert message.startswith("SYNTH-T line 2:")
    assert "QQ900001A" not in message and "14/03/1981" not in message
