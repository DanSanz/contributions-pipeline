"""Working days, England and Wales bank holidays, and strict DD/MM/YYYY parsing.

The scheme's payroll deadlines follow the England and Wales bank-holiday calendar.

Since 4.0 this module holds everything that used to be in ``scheme_common.calendar``,
which was removed.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from functools import lru_cache

UK_DATE_FORMAT = "%d/%m/%Y"

_UK_DATE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")

# Bank holidays proclaimed outside the usual rules.
_PROCLAIMED: dict[int, tuple[date, ...]] = {
    2022: (date(2022, 6, 3), date(2022, 9, 19)),
    2023: (date(2023, 5, 8),),
}

# Regular bank holidays moved to another day in a given year.
_MOVED: dict[date, date] = {
    date(2020, 5, 4): date(2020, 5, 8),
    date(2022, 5, 30): date(2022, 6, 2),
}


class InvalidDateError(ValueError):
    """Raised when text is not a real date in DD/MM/YYYY form.

    The message never repeats the input, because the input may be personal data
    (a date of birth, for example).
    """


def parse_uk_date(text: str) -> date:
    """Parse ``text`` as DD/MM/YYYY: two-digit day, two-digit month, four-digit year.

    Raises InvalidDateError for anything else, including impossible dates such as
    31/02/1980 and two-digit years.
    """
    match = _UK_DATE.fullmatch(text) if isinstance(text, str) else None
    if match is None:
        raise InvalidDateError("not in DD/MM/YYYY form")
    day, month, year = (int(part) for part in match.groups())
    try:
        return date(year, month, day)
    except ValueError:
        raise InvalidDateError("not a calendar date") from None


def try_parse_uk_date(text: str) -> date | None:
    """Like parse_uk_date, but return None instead of raising."""
    try:
        return parse_uk_date(text)
    except InvalidDateError:
        return None


def format_uk_date(value: date) -> str:
    """Format ``value`` as DD/MM/YYYY."""
    return f"{value.day:02d}/{value.month:02d}/{value.year:04d}"


def easter_sunday(year: int) -> date:
    """Western Easter Sunday for ``year`` (anonymous Gregorian algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month, day = divmod(h + l_ - 7 * m + 114, 31)
    return date(year, month, day + 1)


def _first_monday(year: int, month: int) -> date:
    day = date(year, month, 1)
    return day + timedelta(days=(7 - day.weekday()) % 7)


def _last_monday(year: int, month: int) -> date:
    next_month = date(year + month // 12, month % 12 + 1, 1)
    day = next_month - timedelta(days=1)
    return day - timedelta(days=day.weekday())


def _roll_to_free_weekday(day: date, taken: set[date]) -> date:
    while day.weekday() >= 5 or day in taken:
        day += timedelta(days=1)
    return day


@lru_cache(maxsize=None)
def bank_holidays(year: int) -> frozenset[date]:
    """England and Wales bank holidays in ``year``, substitute days included."""
    easter = easter_sunday(year)
    fixed_weekdays = [
        easter - timedelta(days=2),
        easter + timedelta(days=1),
        _first_monday(year, 5),
        _last_monday(year, 5),
        _last_monday(year, 8),
    ]
    holidays: set[date] = {_MOVED.get(day, day) for day in fixed_weekdays}
    holidays.add(_roll_to_free_weekday(date(year, 1, 1), holidays))
    # Christmas first, then Boxing Day, each to the next free weekday.
    holidays.add(_roll_to_free_weekday(date(year, 12, 25), holidays))
    holidays.add(_roll_to_free_weekday(date(year, 12, 26), holidays))
    holidays.update(_PROCLAIMED.get(year, ()))
    return frozenset(holidays)


def is_working_day(day: date) -> bool:
    """True for Monday to Friday, except bank holidays."""
    return day.weekday() < 5 and day not in bank_holidays(day.year)


def next_working_day(day: date) -> date:
    """``day`` itself if it is a working day, otherwise the next working day after it."""
    while not is_working_day(day):
        day += timedelta(days=1)
    return day


def previous_working_day(day: date) -> date:
    """``day`` itself if it is a working day, otherwise the last working day before it."""
    while not is_working_day(day):
        day -= timedelta(days=1)
    return day


def add_working_days(day: date, count: int) -> date:
    """The date ``count`` working days after ``day`` (before it, if ``count`` is negative)."""
    step = timedelta(days=1 if count >= 0 else -1)
    remaining = abs(count)
    while remaining:
        day += step
        if is_working_day(day):
            remaining -= 1
    return day


def working_days_between(start: date, end: date) -> int:
    """Working days after ``start`` up to and including ``end``. Zero if ``end <= start``."""
    count = 0
    day = start
    while day < end:
        day += timedelta(days=1)
        if is_working_day(day):
            count += 1
    return count


def age_on(born: date, on: date) -> int:
    """Age in whole years on ``on`` for someone born on ``born``.

    Someone born on 29 February has a birthday on 1 March in years that are not leap years.
    """
    years = on.year - born.year
    if (on.month, on.day) < (born.month, born.day):
        years -= 1
    return years
