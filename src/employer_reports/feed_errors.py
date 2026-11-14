from __future__ import annotations

from typing import Iterable

from late_contributions import RowError

from employer_reports.report import Report


def feed_errors_report(errors: Iterable[RowError], file_id: str) -> Report:
    report = Report(
        title=f"Rows that could not be read: {file_id}",
        columns=["Employer", "Payroll", "Period", "Problem"],
    )
    for error in errors:
        report.add_row(error.employer_id, error.payroll_id, error.period, error.reason)
    return report
