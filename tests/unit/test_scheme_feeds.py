from datetime import date

import pytest

from scheme_common.feeds import EnvelopeError, iter_records, parse_header, parse_trailer, split_record


def test_split_on_pipes():
    assert split_record("DTL|a|b|c") == ["DTL", "a", "b", "c"]


def test_escaped_pipe_stays_in_the_field():
    assert split_record(r"DTL|a\|b|c") == ["DTL", "a|b", "c"]


def test_trailing_empty_field_is_kept():
    assert split_record("DTL|a|") == ["DTL", "a", ""]


def test_header_parses_file_date_day_first():
    header = parse_header(["MEMBERS", "E90001", "SYNTH-F1", "02/11/2026", "3.1"])
    assert header.file_date == date(2026, 11, 2)
    assert (header.feed_type, header.sender_id, header.file_id) == ("MEMBERS", "E90001", "SYNTH-F1")


def test_header_with_wrong_field_count_is_rejected():
    with pytest.raises(EnvelopeError, match="5"):
        parse_header(["MEMBERS", "E90001"])


def test_header_date_must_be_dd_mm_yyyy():
    with pytest.raises(EnvelopeError):
        parse_header(["MEMBERS", "E90001", "SYNTH-F1", "2026-11-02", "3.1"])


def test_trailer_count():
    assert parse_trailer(["12"], 14) == 12


def test_trailer_must_be_a_number():
    with pytest.raises(EnvelopeError) as caught:
        parse_trailer(["twelve"], 14)
    assert caught.value.line_no == 14


def test_blank_lines_are_skipped_and_line_numbers_kept():
    records = list(iter_records(["HDR|x", "", "DTL|y", "TRL|1"]))
    assert [(line_no, kind) for line_no, kind, _ in records] == [(1, "HDR"), (3, "DTL"), (4, "TRL")]
