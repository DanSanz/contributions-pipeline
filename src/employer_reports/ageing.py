from __future__ import annotations

from datetime import date
from typing import Iterable

from late_contributions import Assessment, due_date

from employer_reports.formatting import uk_date
from employer_reports.report import Report

_BANDS = [(30, "0 to 30 days"), (60, "31 to 60 days"), (90, "61 to 90 days")]


def ageing_report(assessments: Iterable[Assessment]) -> Report:
    """Arrears by age: each unpaid payroll, banded by days past the deadline."""
    today = date.today()
    report = Report(
        title=f"Arrears at {uk_date(today)}",
        columns=["Employer", "Payroll", "Pay period", "Deadline", "Overdue by"],
    )
    for item in assessments:
        if item.status != "unpaid":
            continue
        deadline = due_date(item.period)
        report.add_row(item.employer_id, item.payroll_id, item.period,
                       uk_date(deadline), _band((today - deadline).days))
    return report


def _band(days_overdue: int) -> str:
    for bound, label in _BANDS:
        if days_overdue <= bound:
            return label
    return "over 90 days"
