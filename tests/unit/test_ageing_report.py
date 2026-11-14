from employer_reports import ageing_report
from late_contributions import Assessment


def test_ageing_report_columns():
    report = ageing_report([])
    assert report.columns == ["Employer", "Payroll", "Pay period", "Deadline", "Overdue by"]


def test_one_row_for_each_unpaid_assessment():
    report = ageing_report([
        Assessment("E90001", "PAY04", "2026-09", "unpaid", 10),
        Assessment("E90005", "PAY02", "2026-08", "unpaid", 41),
    ])
    assert len(report) == 2
    assert report.rows[0][:4] == ["E90001", "PAY04", "2026-09", "22/10/2026"]


def test_paid_late_assessments_are_left_out():
    report = ageing_report([
        Assessment("E90001", "PAY03", "2026-09", "paid late", 8),
        Assessment("E90001", "PAY04", "2026-09", "unpaid", 10),
    ])
    assert [row[1] for row in report.rows] == ["PAY04"]
