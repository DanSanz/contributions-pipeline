"""Report builders for Employer Relations and Finance Ops.

Each builder turns results from another module into a Report (title, columns, rows).
Reports go outside the data team: they carry member references, never personal data.
"""

from employer_reports.ageing import ageing_report
from employer_reports.feed_errors import feed_errors_report
from employer_reports.ingest_summary import ingest_summary_report
from employer_reports.joiners import joiners_report
from employer_reports.late_payers import late_payers_report
from employer_reports.report import Report, to_csv_text, to_text_table
from employer_reports.variance import variance_report

__all__ = [
    "Report",
    "ageing_report",
    "feed_errors_report",
    "ingest_summary_report",
    "joiners_report",
    "late_payers_report",
    "to_csv_text",
    "to_text_table",
    "variance_report",
]
