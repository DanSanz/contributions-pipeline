from datetime import date
from decimal import Decimal

import pytest

from tests.builders import make_member
from valuation_extract import EXTRACT_COLUMNS, build_extract, members_frame

VALUATION_DATE = date(2026, 3, 31)


def extract_rows(spark, *members):
    frame = members_frame(spark, members)
    return {row["member_ref"]: row for row in build_extract(frame, VALUATION_DATE).collect()}


def test_columns_leave_out_personal_data(spark):
    frame = build_extract(members_frame(spark, [make_member()]), VALUATION_DATE)
    assert frame.columns == EXTRACT_COLUMNS
    assert not {"date_of_birth", "ni_number", "surname", "forenames"} & set(frame.columns)


def test_age_at_valuation_reads_dates_day_first(spark):
    rows = extract_rows(spark, make_member(member_ref="M900001", date_of_birth="14/03/1981"))
    assert rows["M900001"]["age_at_valuation"] == 45


def test_age_day_before_birthday(spark):
    rows = extract_rows(spark, make_member(member_ref="M900001", date_of_birth="01/04/1981"))
    assert rows["M900001"]["age_at_valuation"] == 44


def test_unreadable_date_of_birth_gives_unknown_age(spark):
    rows = extract_rows(spark, make_member(member_ref="M900001", date_of_birth="31/02/1980"))
    assert rows["M900001"]["age_at_valuation"] is None
    assert rows["M900001"]["age_band"] == "unknown"


@pytest.mark.parametrize(
    ("born", "band"),
    [("01/04/2001", "under 25"), ("31/03/2001", "25-34"), ("31/03/1961", "65+"), ("01/04/1961", "55-64")],
)
def test_age_band_boundaries(spark, born, band):
    rows = extract_rows(spark, make_member(member_ref="M900001", date_of_birth=born))
    assert rows["M900001"]["age_band"] == band


def test_service_years(spark):
    rows = extract_rows(spark, make_member(member_ref="M900001", date_joined="30/09/2015"))
    assert rows["M900001"]["service_years"] == 10.5


def test_salary_is_decimal(spark):
    rows = extract_rows(spark, make_member(member_ref="M900001", salary=Decimal("41250.50")))
    assert rows["M900001"]["salary"] == Decimal("41250.50")


def test_one_row_per_member_in_reference_order(spark):
    frame = members_frame(spark, [make_member(member_ref="M900002"), make_member(member_ref="M900001")])
    assert [row["member_ref"] for row in build_extract(frame, VALUATION_DATE).collect()] == [
        "M900001",
        "M900002",
    ]
