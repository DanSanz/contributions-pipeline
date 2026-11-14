"""Map detail records onto the generated record types."""

from __future__ import annotations

from generated import CONTRACT_VERSION, FEED_TYPES

from feeds._errors import FeedError


def record_type_for(feed_type: str, line_no: int) -> type:
    try:
        return FEED_TYPES[feed_type]
    except KeyError:
        raise FeedError(line_no, f"unknown feed type {feed_type!r}") from None


def check_contract_version(version: str, line_no: int) -> None:
    """Accept any minor version of the contract major this build was generated from."""
    expected_major = CONTRACT_VERSION.split(".")[0]
    if version.split(".")[0] != expected_major:
        raise FeedError(
            line_no, f"contract version {version} is not readable by contract {CONTRACT_VERSION}"
        )


def to_record(record_type: type, fields: list[str], line_no: int, *, strict: bool):
    """Build one record from the fields of a detail line.

    With ``strict`` on, a record with more fields than the contract defines is rejected.
    With it off, the extra fields are dropped. Too few fields is always an error.
    """
    columns = record_type.COLUMNS
    if len(fields) < len(columns):
        raise FeedError(line_no, f"expected {len(columns)} fields, found {len(fields)}")
    if len(fields) > len(columns) and strict:
        raise FeedError(
            line_no, f"expected {len(columns)} fields, found {len(fields)} (strict schema)"
        )
    values = [value.strip() for value in fields[: len(columns)]]
    for name, value in zip(columns, values):
        if not value and name in record_type.REQUIRED:
            raise FeedError(line_no, f"required field {name} is empty")
    return record_type(*values)
