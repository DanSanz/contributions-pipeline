from __future__ import annotations

from typing import Iterable, Protocol

from employer_reports.report import Report


class _Summary(Protocol):
    file_id: str
    employer_id: str
    rows_read: int
    loaded: int


def ingest_summary_report(summaries: Iterable[_Summary]) -> Report:
    report = Report(
        title="Member files loaded",
        columns=["File", "Employer", "Rows read", "Loaded"],
    )
    for summary in summaries:
        report.add_row(
            summary.file_id, summary.employer_id, summary.rows_read, summary.loaded
        )
    return report
