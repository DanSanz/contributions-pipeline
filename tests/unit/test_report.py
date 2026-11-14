from employer_reports import Report, to_csv_text, to_text_table


def test_csv_text():
    report = Report("T", ["a", "b"])
    report.add_row(1, "x")
    assert to_csv_text(report) == "a,b\n1,x\n"


def test_text_table_aligns_columns():
    report = Report("Title", ["Employer", "Days"])
    report.add_row("E90001", 3)
    lines = to_text_table(report).splitlines()
    assert lines[2] == "Employer  Days"
    assert lines[4] == "E90001    3   "
