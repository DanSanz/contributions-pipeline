from datetime import date

from late_contributions import due_date


def test_due_on_the_22nd_of_the_following_month():
    assert due_date("2026-03") == date(2026, 4, 22)


def test_december_period_due_in_january():
    assert due_date("2025-12") == date(2026, 1, 22)


def test_friday_22nd_is_not_moved():
    assert due_date("2026-04") == date(2026, 5, 22)


def test_weekend_22nd_moves_to_the_monday():
    # Saturday 22/05/2027.
    assert due_date("2027-04") == date(2027, 5, 24)


def test_bank_holiday_22nd_moves_to_the_next_working_day():
    # Easter Monday 22/04/2019: due the next day.
    assert due_date("2019-03") == date(2019, 4, 23)
