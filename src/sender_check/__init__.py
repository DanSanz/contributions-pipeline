"""Find the rows of a member file that belong to an employer other than its sender."""

from __future__ import annotations

from collections.abc import Iterable

from generated import MemberRecord

__all__ = ["rows_for_other_employers"]


def rows_for_other_employers(sender_id: str, rows: Iterable[MemberRecord]) -> list[str]:
    """The member references of the rows whose employer is not ``sender_id``, in file order."""
    return [row.member_ref for row in rows if row.employer_id != sender_id]
