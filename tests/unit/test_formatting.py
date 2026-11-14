from datetime import date
from decimal import Decimal

from employer_reports.formatting import days, money, uk_date


def test_money_has_two_places_and_separators():
    assert money(Decimal("12500")) == "12,500.00"


def test_money_none_is_blank():
    assert money(None) == ""


def test_uk_date():
    assert uk_date(date(2026, 10, 22)) == "22/10/2026"


def test_days_singular():
    assert days(1) == "1 day"
    assert days(8) == "8 days"
