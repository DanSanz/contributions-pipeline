from __future__ import annotations

from datetime import date
from decimal import Decimal

from scheme_common.dates import format_uk_date


def uk_date(value: date | None) -> str:
    return format_uk_date(value) if value else ""


def money(value: Decimal | None) -> str:
    return f"{value:,.2f}" if value is not None else ""


def days(count: int) -> str:
    return "1 day" if count == 1 else f"{count} days"
