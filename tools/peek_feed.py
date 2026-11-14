"""Look inside an employer feed file, a return, without loading it.

    $env:PYTHONPATH = "vendor"; python tools/peek_feed.py <file>

For on-call use. It reads the file line by line, so it also works on a file that the
nightly job rejects. It prints line numbers, never field values.
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

from scheme_common.dates import UK_DATE_FORMAT
from scheme_common.feeds import DETAIL, iter_records, read_lines


def summarise(path: Path) -> dict:
    """Feed type, sender, file date, number of detail lines and the line numbers of bad rows."""
    records = list(iter_records(read_lines(Path(path))))
    _, _, header = records[0]
    file_date = datetime.datetime.strptime(header[3], UK_DATE_FORMAT)

    lines = 0
    bad_rows = []
    for line_no, record_type, fields in records[1:]:
        if record_type != DETAIL:
            continue
        lines += 1
        try:
            if header[0] == "MEMBERS":
                datetime.datetime.strptime(fields[5], UK_DATE_FORMAT)
                datetime.datetime.strptime(fields[6], UK_DATE_FORMAT)
            elif header[0] == "CONTRIB" and fields[5]:
                datetime.datetime.strptime(fields[5], UK_DATE_FORMAT)
        except (ValueError, IndexError):
            bad_rows.append(line_no)

    return {
        "feed_type": header[0],
        "sender": header[1],
        "file_date": file_date,
        "lines": lines,
        "bad_rows": bad_rows,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python tools/peek_feed.py <file>, with vendor on PYTHONPATH")
        return 2
    summary = summarise(Path(args[0]))
    print(f"Feed type: {summary['feed_type']}")
    print(f"Sender:    {summary['sender']}")
    print(f"File date: {summary['file_date']:%d/%m/%Y}")
    print(f"Lines:     {summary['lines']}")
    if summary["bad_rows"]:
        print("Bad rows, where a date does not parse:")
        for line_no in summary["bad_rows"]:
            print(f"  line {line_no}")
        print("Look up the member number on that line of the file. This tool never prints it.")
    else:
        print("Bad rows:  none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
