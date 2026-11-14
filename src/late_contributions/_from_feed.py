"""Turn contribution feed records into FeedRows, reporting rows that can't be read."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from generated import ContributionRecord
from scheme_common.dates import InvalidDateError, parse_uk_date

from late_contributions._assess import FeedRow

_PERIOD = re.compile(r"\d{4}-(0[1-9]|1[0-2])")


@dataclass(frozen=True)
class RowError:
    employer_id: str
    payroll_id: str
    period: str
    reason: str


def from_feed(records: Iterable[ContributionRecord]) -> tuple[list[FeedRow], list[RowError]]:
    """Convert records to FeedRows. A row with a malformed period or payment date is
    returned as a RowError, never dropped (spec: late contributions v2)."""
    rows: list[FeedRow] = []
    errors: list[RowError] = []
    for record in records:
        if not _PERIOD.fullmatch(record.period):
            errors.append(_error(record, "period is not YYYY-MM"))
            continue
        if not record.paid_on:
            rows.append(FeedRow(record.employer_id, record.payroll_id, record.period, None))
            continue
        try:
            paid_on = parse_uk_date(record.paid_on)
        except InvalidDateError:
            errors.append(_error(record, "paid_on is not a DD/MM/YYYY date"))
            continue
        rows.append(FeedRow(record.employer_id, record.payroll_id, record.period, paid_on))
    return rows, errors


def _error(record: ContributionRecord, reason: str) -> RowError:
    return RowError(record.employer_id, record.payroll_id, record.period, reason)
