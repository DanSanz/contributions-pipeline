from scheme_common.dates import parse_uk_date
from tools.peek_feed import main, summarise


def _header(path):
    return path.read_text(encoding="utf-8").splitlines()[0].split("|")


def test_reports_the_header_date_of_a_member_file(fixtures_dir):
    path = fixtures_dir / "members_E90001_20261102.txt"
    file_date = parse_uk_date(_header(path)[4])
    assert summarise(path)["file_date"] == file_date


def test_reports_the_header_date_of_a_contributions_file(fixtures_dir):
    path = fixtures_dir / "contributions_E90001_202609.txt"
    file_date = parse_uk_date(_header(path)[4])
    assert summarise(path)["file_date"] == file_date


def test_counts_the_detail_lines(fixtures_dir):
    summary = summarise(fixtures_dir / "contributions_E90001_202609.txt")
    assert (summary["feed_type"], summary["sender"], summary["lines"]) == ("CONTRIB", "E90001", 4)


def test_lists_bad_rows_by_line_number(fixtures_dir):
    summary = summarise(fixtures_dir / "contributions_E90006_bad_dates.txt")
    assert summary["bad_rows"] == [2]


def test_a_member_file_with_an_impossible_date_of_birth(fixtures_dir):
    summary = summarise(fixtures_dir / "members_E90004_20261102_dob.txt")
    assert summary["bad_rows"] == [3]


def test_prints_no_field_values(fixtures_dir, capsys):
    assert main([str(fixtures_dir / "members_E90004_20261102_dob.txt")]) == 0
    out = capsys.readouterr().out
    assert "line 3" in out
    assert "31/02/1980" not in out and "M940002" not in out and "QQ" not in out
