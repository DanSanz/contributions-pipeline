from decimal import Decimal

from feeds import read_file
from reconciliation import RESULT_COLUMNS, contributions_frame, reconcile
from tests.builders import make_contribution_record


def results(spark, records):
    return reconcile(contributions_frame(spark, records)).collect()


def test_result_columns_leave_out_bank_details(spark):
    frame = reconcile(contributions_frame(spark, [make_contribution_record()]))
    assert frame.columns == RESULT_COLUMNS


def test_balanced(spark):
    [row] = results(spark, [make_contribution_record(amount_due="100.00", amount_paid="100.00")])
    assert (row["status"], row["variance"]) == ("balanced", Decimal("0.00"))


def test_payrolls_are_summed_per_employer_and_period(spark, fixtures_dir):
    [row] = results(spark, read_file(fixtures_dir / "contributions_E90005_two_payrolls.txt"))
    assert row["payrolls"] == 2
    assert row["amount_due"] == Decimal("25000.00")
    assert row["amount_paid"] == Decimal("24500.00")
    assert (row["status"], row["variance"]) == ("underpaid", Decimal("-500.00"))


def test_overpaid(spark):
    [row] = results(spark, [make_contribution_record(amount_due="100.00", amount_paid="120.00")])
    assert row["status"] == "overpaid"


def test_unreadable_amount_marks_the_period(spark):
    records = [
        make_contribution_record(payroll_id="PAY01", amount_due="100.00", amount_paid="100.00"),
        make_contribution_record(payroll_id="PAY02", amount_due="1OO.00", amount_paid="100.00"),
    ]
    [row] = results(spark, records)
    assert row["status"] == "unreadable"


def test_periods_are_kept_apart(spark):
    records = [
        make_contribution_record(period="2026-08", amount_paid="0.00"),
        make_contribution_record(period="2026-09"),
    ]
    assert [(row["period"], row["status"]) for row in results(spark, records)] == [
        ("2026-08", "underpaid"),
        ("2026-09", "balanced"),
    ]
