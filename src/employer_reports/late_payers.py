from __future__ import annotations

from datetime import date
from typing import Iterable

from late_contributions import Assessment, due_date

from employer_reports.formatting import days, uk_date
from employer_reports.report import Report


def late_payers_report(assessments: Iterable[Assessment], run_date: date) -> Report:
    report = Report(
        title=f"Late contributions at {uk_date(run_date)}",
        columns=["Employer", "Payroll", "Period", "Due", "Status", "Late by"],
    )
    for item in assessments:
        report.add_row(
            item.employer_id,
            item.payroll_id,
            item.period,
            uk_date(due_date(item.period)),
            item.status,
            days(item.days_late),
        )
    return report
