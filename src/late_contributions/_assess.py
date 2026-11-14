"""Assess employer contributions against the due date (spec: late contributions v2)."""
from dataclasses import dataclass
from datetime import date

from scheme_common.dates import next_working_day


@dataclass(frozen=True)
class FeedRow:
    employer_id: str
    payroll_id: str
    period: str              # "YYYY-MM"
    paid_on: date | None


@dataclass(frozen=True)
class Assessment:
    employer_id: str
    payroll_id: str
    period: str
    status: str              # "unpaid" or "paid late"
    days_late: int


def due_date(period: str) -> date:
    year, month = (int(part) for part in period.split("-"))
    if month == 12:
        year, month = year + 1, 1
    else:
        month += 1
    return next_working_day(date(year, month, 22))


def assess(rows: list[FeedRow], run_date: date) -> list[Assessment]:
    out = []
    for row in rows:
        due = due_date(row.period)
        if row.paid_on is None:
            if run_date > due:
                out.append(Assessment(row.employer_id, row.payroll_id, row.period,
                                      "unpaid", (run_date - due).days))
        elif row.paid_on > due:
            out.append(Assessment(row.employer_id, row.payroll_id, row.period,
                                  "paid late", (row.paid_on - due).days))
    return out
