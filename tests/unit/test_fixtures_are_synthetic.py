"""Every fixture file is marked synthetic (see tests/fixtures/README.md)."""

from pathlib import Path

import pytest

from scheme_common.feeds import read_lines, split_record

FIXTURES = Path(__file__).parent.parent / "fixtures"
FEED_FILES = sorted(FIXTURES.glob("*.txt"))


def _records(path: Path) -> list[list[str]]:
    return [split_record(line) for line in read_lines(path) if line.strip()]


@pytest.mark.parametrize("path", FEED_FILES, ids=lambda p: p.name)
def test_file_id_is_marked_synthetic(path):
    header = _records(path)[0]
    assert header[3].startswith("SYNTH-")


@pytest.mark.parametrize("path", FEED_FILES, ids=lambda p: p.name)
def test_employer_ids_are_in_the_test_range(path):
    for record in _records(path):
        if record[0] in ("HDR", "DTL"):
            assert record[2 if record[0] == "HDR" else 1].startswith("E9")


@pytest.mark.parametrize(
    "path", [p for p in FEED_FILES if p.name.startswith("members_")], ids=lambda p: p.name
)
def test_ni_numbers_use_the_unissued_prefix(path):
    details = [record for record in _records(path) if record[0] == "DTL"]
    assert details
    assert all(record[3].startswith("QQ") for record in details)
