"""Build the valuation extract from the member database.

    python -m pipeline.run_valuation --valuation-date 31/03/2026 --show

Production writes the extract to CP_VALUATION_EXTRACT_URI on the cluster. Local runs use
--show: writing files through Spark on a Windows laptop fails without winutils.exe.
"""

from __future__ import annotations

import argparse
import sys

from member_service import MemberService
from member_store import SqliteMemberStore
from pipeline import settings
from pipeline.spark import get_spark
from scheme_common.dates import parse_uk_date
from valuation_extract import build_extract, eligible_members, members_frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the valuation extract.")
    parser.add_argument("--valuation-date", type=lambda text: parse_uk_date(text),
                        required=True, help="DD/MM/YYYY")
    parser.add_argument("--show", action="store_true", help="print the extract instead of writing it")
    args = parser.parse_args(argv)

    store = SqliteMemberStore(settings.MEMBER_DB_PATH)
    spark = get_spark("valuation-extract")
    try:
        members = eligible_members(MemberService(store).everyone(), args.valuation_date)
        extract = build_extract(members_frame(spark, members), args.valuation_date)
        if args.show or not settings.VALUATION_EXTRACT_URI:
            extract.show(50, truncate=False)
        else:
            extract.write.mode("overwrite").parquet(settings.VALUATION_EXTRACT_URI)
    finally:
        spark.stop()
        store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
