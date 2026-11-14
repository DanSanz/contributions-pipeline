"""late_contributions at its interface (spec: late contributions v2)."""

from datetime import date

from late_contributions import FeedRow, RowError, assess, from_feed
from tests.builders import make_contribution_record

RUN = date(2026, 5, 1)


def test_unpaid_the_day_after_due_is_listed():
    rows = [FeedRow("E90001", "PAY01", "2026-03", None)]
    [item] = assess(rows, date(2026, 4, 23))
    assert (item.status, item.days_late) == ("unpaid", 1)


def test_unpaid_before_the_due_date_is_not_listed():
    assert assess([FeedRow("E90001", "PAY01", "2026-03", None)], date(2026, 4, 15)) == []


def test_paid_before_the_due_date_is_not_listed():
    assert assess([FeedRow("E90001", "PAY01", "2026-03", date(2026, 4, 20))], RUN) == []


def test_paid_after_the_due_date_is_paid_late():
    [item] = assess([FeedRow("E90001", "PAY01", "2026-03", date(2026, 4, 28))], RUN)
    assert (item.status, item.days_late) == ("paid late", 6)


def test_two_payrolls_are_assessed_separately():
    rows = [
        FeedRow("E90005", "MONTHLY", "2026-03", date(2026, 4, 17)),
        FeedRow("E90005", "WEEKLY", "2026-03", date(2026, 4, 24)),
    ]
    assert [(a.payroll_id, a.status) for a in assess(rows, RUN)] == [("WEEKLY", "paid late")]


def test_december_period_is_assessed_against_january():
    [item] = assess([FeedRow("E90001", "PAY01", "2025-12", None)], date(2026, 1, 29))
    assert item.days_late == 7


def test_days_late_count_from_the_monday_after_a_weekend_22nd():
    # Period 2026-02: the 22nd is Sunday 22/03/2026, so the count starts from Monday 23/03/2026.
    [item] = assess([FeedRow("E90001", "PAY01", "2026-02", date(2026, 3, 26))], RUN)
    assert (item.status, item.days_late) == ("paid late", 3)


def test_from_feed_parses_payment_dates_day_first():
    rows, errors = from_feed([make_contribution_record(paid_on="05/10/2026")])
    assert rows[0].paid_on == date(2026, 10, 5)
    assert errors == []


def test_from_feed_keeps_unpaid_rows():
    rows, _ = from_feed([make_contribution_record(paid_on="")])
    assert rows[0].paid_on is None


def test_malformed_payment_date_is_reported_not_dropped():
    rows, errors = from_feed([make_contribution_record(paid_on="10/23/2026")])
    assert rows == []
    assert errors == [RowError("E90001", "PAY01", "2026-09", "paid_on is not a DD/MM/YYYY date")]


def test_malformed_period_is_reported():
    _, errors = from_feed([make_contribution_record(period="2026-13")])
    assert errors[0].reason == "period is not YYYY-MM"
