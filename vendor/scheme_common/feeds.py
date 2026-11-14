"""The envelope shared by the scheme's inbound feed files.

A file is one header record, any number of detail records, and one trailer record.
Fields are pipe-delimited. A pipe inside a field is written as a backslash and a pipe.

    HDR|<feed type>|<sender id>|<file id>|<file date, DD/MM/YYYY>|<contract version>
    DTL|<field>|<field>|...
    TRL|<number of detail records>

This module knows the envelope only. What the detail fields mean is defined per feed
by the feed contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterator

from scheme_common.dates import InvalidDateError, parse_uk_date

DELIMITER = "|"
ESCAPE = "\\"
HEADER, DETAIL, TRAILER = "HDR", "DTL", "TRL"
ENCODINGS = ("utf-8-sig", "cp1252")


class EnvelopeError(ValueError):
    """A file whose envelope is malformed. Messages carry line numbers, never field values."""

    def __init__(self, line_no: int, message: str) -> None:
        super().__init__(f"line {line_no}: {message}")
        self.line_no = line_no
        self.reason = message


@dataclass(frozen=True)
class FeedHeader:
    feed_type: str
    sender_id: str
    file_id: str
    file_date: date
    contract_version: str


def split_record(line: str, delimiter: str = DELIMITER) -> list[str]:
    """Split one record into fields, honouring escaped delimiters."""
    fields: list[str] = []
    current: list[str] = []
    chars = iter(line)
    for char in chars:
        if char == ESCAPE:
            following = next(chars, "")
            if following == delimiter:
                current.append(delimiter)
            else:
                current.append(char + following)
        elif char == delimiter:
            fields.append("".join(current))
            current = []
        else:
            current.append(char)
    fields.append("".join(current))
    return fields


def read_lines(path: Path, encodings: tuple[str, ...] = ENCODINGS) -> list[str]:
    """Read a feed file as text, trying each encoding in turn."""
    raw = Path(path).read_bytes()
    for encoding in encodings:
        try:
            return raw.decode(encoding).splitlines()
        except UnicodeDecodeError:
            continue
    raise EnvelopeError(0, f"file is not in any of {', '.join(encodings)}")


def iter_records(lines: list[str]) -> Iterator[tuple[int, str, list[str]]]:
    """Yield (line number, record type, fields after the type) for each non-blank line."""
    for line_no, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        fields = split_record(line)
        yield line_no, fields[0].strip(), fields[1:]


def parse_header(fields: list[str], line_no: int = 1) -> FeedHeader:
    if len(fields) != 5:
        raise EnvelopeError(line_no, f"header has {len(fields)} fields, expected 5")
    feed_type, sender_id, file_id, file_date, version = (field.strip() for field in fields)
    try:
        parsed_date = parse_uk_date(file_date)
    except InvalidDateError:
        raise EnvelopeError(line_no, "header file date is not DD/MM/YYYY") from None
    return FeedHeader(feed_type, sender_id, file_id, parsed_date, version)


def parse_trailer(fields: list[str], line_no: int) -> int:
    if len(fields) != 1 or not fields[0].strip().isdigit():
        raise EnvelopeError(line_no, "trailer must hold one record count")
    return int(fields[0].strip())
