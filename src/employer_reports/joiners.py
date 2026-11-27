from __future__ import annotations

from datetime import date

from member_service import MemberService
from scheme_common.dates import parse_uk_date

from employer_reports.report import Report


def joiners_report(members: MemberService, employer_id: str, start: date, end: date) -> Report:
    """New starters at one organisation whose date joined falls from start to end, oldest first."""
    report = Report(
        title=f"New starters for {employer_id}",
        columns=["Member number", "Start date"],
    )
    joined = [
        m for m in members.everyone()
        if m.employer_id == employer_id
        and parse_uk_date(m.date_joined) >= start
        and parse_uk_date(m.date_joined) <= end
    ]
    for m in sorted(joined, key=lambda m: parse_uk_date(m.date_joined)):
        report.add_row(m.member_ref, m.date_joined)
    return report
