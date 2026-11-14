"""Read a whole feed file: envelope first, then detail records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, TypeAlias

from generated import ContributionRecord, MemberRecord
from pipeline import settings
from scheme_common.feeds import (
    DETAIL,
    HEADER,
    TRAILER,
    EnvelopeError,
    FeedHeader,
    iter_records,
    parse_header,
    parse_trailer,
    read_lines,
)

from feeds._contract import check_contract_version, record_type_for, to_record
from feeds._errors import FeedError

Row: TypeAlias = MemberRecord | ContributionRecord
FileHeader: TypeAlias = FeedHeader


@dataclass(frozen=True)
class _Envelope:
    header: FeedHeader
    details: list[tuple[int, list[str]]]


def _read_envelope(path: Path) -> _Envelope:
    try:
        records = list(iter_records(read_lines(path)))
    except EnvelopeError as exc:
        raise FeedError(exc.line_no, exc.reason) from None
    if not records:
        raise FeedError(0, "file is empty")

    line_no, record_type, fields = records[0]
    if record_type != HEADER:
        raise FeedError(line_no, "first record is not a header")
    try:
        header = parse_header(fields, line_no)
    except EnvelopeError as exc:
        raise FeedError(exc.line_no, exc.reason) from None
    record_type_for(header.feed_type, line_no)
    check_contract_version(header.contract_version, line_no)

    last_line, last_type, last_fields = records[-1]
    if last_type != TRAILER:
        raise FeedError(last_line, "file has no trailer (truncated?)", file_id=header.file_id)
    try:
        expected = parse_trailer(last_fields, last_line)
    except EnvelopeError as exc:
        raise FeedError(exc.line_no, exc.reason, file_id=header.file_id) from None

    details = []
    for line_no, record_type, fields in records[1:-1]:
        if record_type != DETAIL:
            raise FeedError(line_no, f"unexpected {record_type} record", file_id=header.file_id)
        details.append((line_no, fields))
    if len(details) != expected:
        raise FeedError(
            last_line,
            f"trailer says {expected} detail records, file has {len(details)}",
            file_id=header.file_id,
        )
    return _Envelope(header, details)


def read_header(path: Path) -> FileHeader:
    """The header of a feed file, after checking the whole envelope."""
    return _read_envelope(Path(path)).header


def read_file(path: Path, *, strict: bool | None = None) -> Iterator[Row]:
    """Yield the detail records of a feed file as generated record types.

    The envelope is checked before the first record is yielded, so a truncated file
    fails before any of it is used. ``strict`` defaults to settings.STRICT_SCHEMA.
    """
    envelope = _read_envelope(Path(path))
    strict = settings.STRICT_SCHEMA if strict is None else strict
    record_type = record_type_for(envelope.header.feed_type, 1)
    return _records(envelope, record_type, strict)


def _records(envelope: _Envelope, record_type: type, strict: bool) -> Iterator[Row]:
    for line_no, fields in envelope.details:
        try:
            yield to_record(record_type, fields, line_no, strict=strict)
        except FeedError as exc:
            raise FeedError(exc.line_no, exc.reason, file_id=envelope.header.file_id) from None
