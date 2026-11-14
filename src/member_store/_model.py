from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from generated import MemberRecord


@dataclass(frozen=True)
class Member:
    member_ref: str
    employer_id: str
    ni_number: str
    surname: str
    forenames: str
    date_of_birth: str  # DD/MM/YYYY as received from the employer
    date_joined: str  # DD/MM/YYYY as received from the employer
    salary: Decimal
    source_file_id: str


def member_from_record(record: MemberRecord, *, file_id: str) -> Member:
    """Convert a feed record to a member. Raises ValueError (without values) for a bad salary."""
    try:
        salary = Decimal(record.salary)
    except InvalidOperation:
        raise ValueError(f"salary for member {record.member_ref} is not a decimal") from None
    return Member(
        member_ref=record.member_ref,
        employer_id=record.employer_id,
        ni_number=record.ni_number,
        surname=record.surname,
        forenames=record.forenames,
        date_of_birth=record.date_of_birth,
        date_joined=record.date_joined,
        salary=salary,
        source_file_id=file_id,
    )
