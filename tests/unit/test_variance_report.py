from decimal import Decimal

from employer_reports import variance_report


def test_variance_report_leaves_out_balanced_rows():
    rows = [
        {"employer_id": "E90001", "payrolls": 1, "amount_due": Decimal("10"), "amount_paid": Decimal("10"),
         "variance": Decimal("0"), "status": "balanced"},
        {"employer_id": "E90005", "payrolls": 2, "amount_due": Decimal("25000"), "amount_paid": Decimal("24500"),
         "variance": Decimal("-500"), "status": "underpaid"},
    ]
    report = variance_report(rows, "2026-09")
    assert report.rows == [["E90005", "2", "25,000.00", "24,500.00", "-500.00", "underpaid"]]
