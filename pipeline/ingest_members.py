"""Nightly member ingestion for employer files."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

from employer_reports import ingest_summary_report, to_text_table
from feeds import FeedError, read_file, read_header
from member_store import MemberStore, SqliteMemberStore, load_members
from pipeline import settings
from scheme_common import audit
from scheme_common.audit import record_event
from sender_check import rows_for_other_employers

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestSummary:
    file_id: str
    employer_id: str
    rows_read: int
    loaded: int


def ingest_file(path: Path, store: MemberStore) -> IngestSummary:
    """Load one employer member file into ``store`` and audit the load."""
    header = read_header(path)
    if header.feed_type != "MEMBERS":
        raise ValueError(f"{header.file_id} is a {header.feed_type} file, not MEMBERS")

    rows = list(read_file(path))
    strays = rows_for_other_employers(header.sender_id, rows)
    if strays:
        logger.warning("%s: %d rows for another employer", header.file_id, len(strays))
    loaded = load_members(store, rows, file_id=header.file_id)

    record_event(
        "member_file_loaded",
        header.file_id,
        f"{loaded} of {len(rows)} member rows loaded",
        actor=settings.AUDIT_ACTOR,
    )
    logger.info("Loaded %d of %d member rows from %s", loaded, len(rows), header.file_id)
    return IngestSummary(header.file_id, header.sender_id, len(rows), loaded)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load employer member files.")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--db", type=Path, default=settings.MEMBER_DB_PATH)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    audit.configure(audit.JsonLinesAuditSink(settings.AUDIT_LOG_PATH))
    store = SqliteMemberStore(args.db)

    failed = 0
    summaries = []
    try:
        for path in args.files:
            try:
                summary = ingest_file(path, store)
            except FeedError as exc:
                logger.error("Rejected %s: %s", path.name, exc)
                failed += 1
                continue
            print(f"{summary.file_id}: {summary.loaded} of {summary.rows_read} rows loaded")
            summaries.append(summary)
        print(to_text_table(ingest_summary_report(summaries)))
    finally:
        store.close()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
