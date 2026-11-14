from employer_reports import feed_errors_report
from late_contributions import RowError


def test_feed_errors_report():
    report = feed_errors_report([RowError("E90006", "PAY01", "2026-09", "paid_on is not a DD/MM/YYYY date")], "SYNTH-F")
    assert report.title.endswith("SYNTH-F")
    assert len(report) == 1
