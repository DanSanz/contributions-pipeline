from __future__ import annotations

from datetime import date
from typing import Iterable

from pyspark.sql import Column, DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructField, StructType

from member_store import Member

MEMBERS_SCHEMA = StructType(
    [
        StructField("member_ref", StringType(), False),
        StructField("employer_id", StringType(), False),
        StructField("date_of_birth", StringType(), True),
        StructField("date_joined", StringType(), True),
        StructField("salary", StringType(), True),
    ]
)

EXTRACT_COLUMNS = [
    "member_ref",
    "employer_id",
    "age_at_valuation",
    "age_band",
    "service_years",
    "salary",
]

# (upper bound exclusive, label). Ages at or above the last bound fall in "65+".
_AGE_BANDS = [(25, "under 25"), (35, "25-34"), (45, "35-44"), (55, "45-54"), (65, "55-64")]

_FEED_DATE = "dd/MM/yyyy"


def members_frame(spark: SparkSession, members: Iterable[Member]) -> DataFrame:
    """Members as a DataFrame of the fields the extract needs, as text."""
    rows = [
        (m.member_ref, m.employer_id, m.date_of_birth, m.date_joined, str(m.salary))
        for m in members
    ]
    return spark.createDataFrame(rows, MEMBERS_SCHEMA)


def _age_band(age: Column) -> Column:
    band = F.when(age.isNull(), F.lit("unknown"))
    for upper, label in _AGE_BANDS:
        band = band.when(age < upper, F.lit(label))
    return band.otherwise(F.lit("65+"))


def build_extract(members: DataFrame, valuation_date: date) -> DataFrame:
    """One row per member. Age is null and the band "unknown" when the date of birth
    can't be read as DD/MM/YYYY."""
    on = F.lit(valuation_date)
    born = F.to_date(F.col("date_of_birth"), _FEED_DATE)
    joined = F.to_date(F.col("date_joined"), _FEED_DATE)
    age = F.floor(F.months_between(on, born) / 12).cast("int")
    return (
        members.withColumn("age_at_valuation", age)
        .withColumn("age_band", _age_band(F.col("age_at_valuation")))
        .withColumn("service_years", F.round(F.months_between(on, joined) / 12, 2))
        .withColumn("salary", F.col("salary").cast("decimal(12,2)"))
        .select(*EXTRACT_COLUMNS)
        .orderBy("member_ref")
    )
