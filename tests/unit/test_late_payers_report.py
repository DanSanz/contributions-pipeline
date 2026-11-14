from datetime import date

from employer_reports import late_payers_report
from late_contributions import Assessment


def test_late_payers_report_shows_due_date():
    report = late_payers_report([Assessment("E90001", "PAY03", "2026-09", "paid late", 8)], date(2026, 11, 1))
    assert report.rows == [["E90001", "PAY03", "2026-09", "22/10/2026", "paid late", "8 days"]]
