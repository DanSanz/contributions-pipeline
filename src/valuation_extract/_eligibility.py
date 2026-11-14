"""Which members the valuation counts, and their service at the effective date."""

from __future__ import annotations

import datetime as dt
import logging
from typing import Iterable

from employer_reports.formatting import uk_date
from member_store import Member

logger = logging.getLogger(__name__)


def eligible_members(members: Iterable[Member], as_at: dt.date) -> list[Member]:
    """Leave out anyone who joined after the as-at date."""
    members = list(members)
    eligible = []
    for member in members:
        try:
            joined = dt.datetime.strptime(member.date_joined, "%d/%m/%Y").date()
        except ValueError:
            # The extract shows these members with a null service, so keep them.
            eligible.append(member)
            continue
        if joined <= as_at:
            eligible.append(member)
    logger.info("%d of %d members eligible at %s", len(eligible), len(members), uk_date(as_at))
    return eligible


def service_days(member: Member, as_at: dt.date) -> int:
    """Days in the scheme at the effective date."""
    return (as_at - dt.datetime.strptime(member.date_joined, "%d/%m/%Y").date()).days


def joined_in_year(member: Member, year: int) -> bool:
    """True for a new entrant in that year."""
    return dt.datetime.strptime(member.date_joined, "%d/%m/%Y").year == year
