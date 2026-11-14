from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Mapping

from employer_reports.formatting import money
from employer_reports.report import Report


def variance_report(rows: Iterable[Mapping[str, object]], period: str) -> Report:
    """Rows are reconciliation results (see reconciliation.reconcile), collected as dicts."""
    report = Report(
        title=f"Contribution variances for {period}",
        columns=["Employer", "Payrolls", "Due", "Paid", "Variance", "Status"],
    )
    for row in rows:
        if row["status"] == "balanced":
            continue
        report.add_row(
            row["employer_id"],
            row["payrolls"],
            money(_decimal(row["amount_due"])),
            money(_decimal(row["amount_paid"])),
            money(_decimal(row["variance"])),
            row["status"],
        )
    return report


def _decimal(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))
