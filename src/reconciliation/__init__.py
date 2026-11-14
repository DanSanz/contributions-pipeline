"""Reconcile contributions due against contributions paid, per employer and period, in Spark.

Interface:
    contributions_frame(spark, records) -> DataFrame
    reconcile(contributions_df) -> DataFrame with RESULT_COLUMNS

Bank details in the feed are Confidential; they are never read into the frame.
"""

from reconciliation._reconcile import RESULT_COLUMNS, contributions_frame, reconcile

__all__ = ["RESULT_COLUMNS", "contributions_frame", "reconcile"]
