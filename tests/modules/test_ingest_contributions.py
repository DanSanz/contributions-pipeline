"""The nightly contributions run, end to end on fixture files."""

from datetime import date

import pytest

from employer_reports import to_csv_text
from pipeline.ingest_contributions import run

RUN = date(2026, 11, 1)


def test_late_payers(fixtures_dir):
    result = run(fixtures_dir / "contributions_E90001_202609.txt", RUN)
    assert [(a.payroll_id, a.status, a.days_late) for a in result.assessments] == [
        ("PAY03", "paid late", 8),
        ("PAY04", "unpaid", 10),
    ]


def test_late_payers_report_rows(fixtures_dir):
    result = run(fixtures_dir / "contributions_E90001_202609.txt", RUN)
    assert result.late_payers.rows[1] == ["E90001", "PAY04", "2026-09", "22/10/2026", "unpaid", "10 days"]


def test_reports_carry_no_bank_details(fixtures_dir):
    result = run(fixtures_dir / "contributions_E90001_202609.txt", RUN)
    text = to_csv_text(result.late_payers) + to_csv_text(result.unreadable)
    assert "99-00-01" not in text and "00000001" not in text


def test_unreadable_rows_are_reported(fixtures_dir):
    result = run(fixtures_dir / "contributions_E90006_bad_dates.txt", RUN)
    assert [(e.payroll_id, e.reason) for e in result.errors] == [
        ("PAY01", "paid_on is not a DD/MM/YYYY date"),
        ("PAY03", "period is not YYYY-MM"),
    ]
    assert len(result.unreadable) == 2


def test_rerun_gives_the_same_result(fixtures_dir):
    first = run(fixtures_dir / "contributions_E90005_two_payrolls.txt", RUN)
    second = run(fixtures_dir / "contributions_E90005_two_payrolls.txt", RUN)
    assert first.assessments == second.assessments


def test_member_file_is_refused(fixtures_dir):
    with pytest.raises(ValueError, match="not CONTRIB"):
        run(fixtures_dir / "members_E90001_20261102.txt", RUN)
