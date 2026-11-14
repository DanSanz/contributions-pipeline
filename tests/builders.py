"""Builders for in-memory feed records and members. Every default value is synthetic."""

from decimal import Decimal

from generated import ContributionRecord, MemberRecord
from member_store import Member


def make_member_record(**overrides: str) -> MemberRecord:
    values = {
        "employer_id": "E90001",
        "member_ref": "M900001",
        "ni_number": "QQ100001A",
        "surname": "Synthetic",
        "forenames": "Alex",
        "date_of_birth": "14/03/1981",
        "date_joined": "01/09/2015",
        "salary": "41250.00",
    }
    values.update(overrides)
    return MemberRecord(**values)


def make_contribution_record(**overrides: str) -> ContributionRecord:
    values = {
        "employer_id": "E90001",
        "payroll_id": "PAY01",
        "period": "2026-09",
        "amount_due": "1000.00",
        "amount_paid": "1000.00",
        "paid_on": "15/10/2026",
        "bank_sort_code": "99-00-01",
        "bank_account": "00000001",
    }
    values.update(overrides)
    return ContributionRecord(**values)


def make_member(**overrides: object) -> Member:
    values: dict[str, object] = {
        "member_ref": "M900001",
        "employer_id": "E90001",
        "ni_number": "QQ100001A",
        "surname": "Synthetic",
        "forenames": "Alex",
        "date_of_birth": "14/03/1981",
        "date_joined": "01/09/2015",
        "salary": Decimal("41250.00"),
        "source_file_id": "SYNTH-M-E90001-20261102",
    }
    values.update(overrides)
    return Member(**values)  # type: ignore[arg-type]
