from __future__ import annotations

from datetime import date, datetime

from member_service import MemberService

from employer_reports.report import Report

_FMT = "%d/%m/%Y"


def joiners_report(members: MemberService, employer_id: str, start: date, end: date) -> Report:
    """New starters at one organisation whose date joined falls from start to end, oldest first."""
    report = Report(
        title=f"New starters for {employer_id}",
        columns=["Member number", "Start date"],
    )
    joined = [
        m for m in members.everyone()
        if m.employer_id == employer_id
        and datetime.strptime(m.date_joined, _FMT).date() >= start
        and datetime.strptime(m.date_joined, _FMT).date() <= end
    ]
    for m in sorted(joined, key=lambda m: datetime.strptime(m.date_joined, _FMT)):
        report.add_row(m.member_ref, m.date_joined)
    return report
