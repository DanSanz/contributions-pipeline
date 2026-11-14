"""The member extract for the scheme valuation, built in Spark.

Interface:
    members_frame(spark, members) -> DataFrame
    build_extract(members_df, valuation_date) -> DataFrame with EXTRACT_COLUMNS
    eligible_members(members, as_at) -> list[Member]
    service_days(member, as_at) -> int
    joined_in_year(member, year) -> bool

The extract leaves out personal fields: the actuaries get age and service, not dates of
birth, names or NI numbers.
"""

from valuation_extract._eligibility import eligible_members, joined_in_year, service_days
from valuation_extract._extract import EXTRACT_COLUMNS, build_extract, members_frame

__all__ = [
    "EXTRACT_COLUMNS",
    "build_extract",
    "eligible_members",
    "joined_in_year",
    "members_frame",
    "service_days",
]
