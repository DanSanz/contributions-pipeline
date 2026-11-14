"""The SparkSession used by the pipeline jobs and the Spark tests."""

from __future__ import annotations

from pyspark.sql import SparkSession

from pipeline import settings

SPARK_CONF = {
    "spark.ui.enabled": "false",
    "spark.sql.shuffle.partitions": "1",
    "spark.sql.session.timeZone": "Europe/London",
    # Unparseable dates become null instead of raising SparkUpgradeException.
    "spark.sql.legacy.timeParserPolicy": "CORRECTED",
}


def get_spark(app_name: str, master: str | None = None) -> SparkSession:
    builder = SparkSession.builder.master(master or settings.SPARK_MASTER).appName(app_name)
    for key, value in SPARK_CONF.items():
        builder = builder.config(key, value)
    return builder.getOrCreate()
