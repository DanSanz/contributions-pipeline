"""Nightly contributions run: list late payers and the rows that could not be read."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from employer_reports import (Report, ageing_report, feed_errors_report, late_payers_report,
                              to_text_table)
from feeds import FeedError, read_file, read_header
from late_contributions import Assessment, RowError, assess, from_feed

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ContributionsRun:
    file_id: str
    assessments: list[Assessment]
    errors: list[RowError]
    late_payers: Report
    unreadable: Report


def run(path: Path, run_date: date) -> ContributionsRun:
    """Assess one contributions file. Rerunning with the same inputs gives the same result."""
    header = read_header(path)
    if header.feed_type != "CONTRIB":
        raise ValueError(f"{header.file_id} is a {header.feed_type} file, not CONTRIB")
    rows, errors = from_feed(read_file(path))
    assessments = assess(rows, run_date)
    logger.info(
        "%s: %d rows assessed, %d late, %d unreadable",
        header.file_id, len(rows), len(assessments), len(errors),
    )
    return ContributionsRun(
        file_id=header.file_id,
        assessments=assessments,
        errors=errors,
        late_payers=late_payers_report(assessments, run_date),
        unreadable=feed_errors_report(errors, header.file_id),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assess employer contribution files.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--run-date", type=lambda text: datetime.strptime(text, "%d/%m/%Y").date(),
                        default=date.today(), help="DD/MM/YYYY; defaults to today")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    failed = 0
    for path in args.files:
        try:
            result = run(path, args.run_date)
        except FeedError as exc:
            logger.error("Rejected %s: %s", path.name, exc)
            failed += 1
            continue
        print(to_text_table(result.late_payers))
        print(to_text_table(ageing_report(result.assessments)))
        if result.errors:
            print(to_text_table(result.unreadable))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
