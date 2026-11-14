from datetime import date

import pytest

from scheme_common.dates import (
    InvalidDateError,
    add_working_days,
    age_on,
    bank_holidays,
    easter_sunday,
    format_uk_date,
    is_working_day,
    next_working_day,
    parse_uk_date,
    previous_working_day,
    try_parse_uk_date,
    working_days_between,
)


def test_parses_day_first():
    assert parse_uk_date("05/03/1980") == date(1980, 3, 5)


def test_day_over_twelve_parses():
    assert parse_uk_date("14/03/1981") == date(1981, 3, 14)


@pytest.mark.parametrize(
    "text",
    ["31/02/1980", "29/02/1981", "03/14/1981", "1981-03-14", "14/3/1981", "14/03/81", "", " 14/03/1981"],
)
def test_rejects_anything_but_a_real_dd_mm_yyyy_date(text):
    with pytest.raises(InvalidDateError):
        parse_uk_date(text)


def test_error_message_does_not_repeat_the_input():
    with pytest.raises(InvalidDateError) as caught:
        parse_uk_date("31/02/1980")
    assert "31/02/1980" not in str(caught.value)


def test_try_parse_returns_none_for_bad_input():
    assert try_parse_uk_date("31/02/1980") is None


def test_leap_day_parses_in_a_leap_year():
    assert parse_uk_date("29/02/1988") == date(1988, 2, 29)


def test_format_round_trips():
    assert format_uk_date(date(1981, 3, 14)) == "14/03/1981"


def test_easter_2026():
    assert easter_sunday(2026) == date(2026, 4, 5)


def test_bank_holidays_2026():
    assert sorted(bank_holidays(2026)) == [
        date(2026, 1, 1),
        date(2026, 4, 3),
        date(2026, 4, 6),
        date(2026, 5, 4),
        date(2026, 5, 25),
        date(2026, 8, 31),
        date(2026, 12, 25),
        date(2026, 12, 28),
    ]


def test_christmas_on_sunday_gives_two_substitute_days():
    # 2022: Christmas Sunday, Boxing Day Monday, substitute Tuesday.
    holidays = bank_holidays(2022)
    assert date(2022, 12, 26) in holidays
    assert date(2022, 12, 27) in holidays


def test_proclaimed_holiday_included():
    assert date(2023, 5, 8) in bank_holidays(2023)


def test_moved_holiday_replaces_the_regular_one():
    holidays = bank_holidays(2020)
    assert date(2020, 5, 8) in holidays
    assert date(2020, 5, 4) not in holidays


def test_weekend_is_not_a_working_day():
    assert not is_working_day(date(2026, 11, 21))


def test_bank_holiday_is_not_a_working_day():
    assert not is_working_day(date(2026, 8, 31))


def test_next_working_day_skips_weekend():
    assert next_working_day(date(2026, 11, 21)) == date(2026, 11, 23)


def test_next_working_day_keeps_a_working_day():
    assert next_working_day(date(2026, 11, 20)) == date(2026, 11, 20)


def test_next_working_day_skips_easter():
    assert next_working_day(date(2026, 4, 3)) == date(2026, 4, 7)


def test_previous_working_day_skips_weekend():
    assert previous_working_day(date(2026, 11, 22)) == date(2026, 11, 20)


def test_add_working_days_crosses_christmas():
    assert add_working_days(date(2026, 12, 24), 1) == date(2026, 12, 29)


def test_add_negative_working_days():
    assert add_working_days(date(2026, 11, 23), -1) == date(2026, 11, 20)


def test_working_days_between():
    assert working_days_between(date(2026, 11, 20), date(2026, 11, 27)) == 5


def test_age_day_before_birthday():
    assert age_on(date(2010, 11, 3), date(2026, 11, 2)) == 15


def test_age_on_birthday():
    assert age_on(date(2010, 11, 2), date(2026, 11, 2)) == 16


def test_leap_day_birthday_counts_from_first_of_march():
    assert age_on(date(2008, 2, 29), date(2025, 2, 28)) == 16
    assert age_on(date(2008, 2, 29), date(2025, 3, 1)) == 17
