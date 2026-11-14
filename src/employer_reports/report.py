from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field


@dataclass
class Report:
    title: str
    columns: list[str]
    rows: list[list[str]] = field(default_factory=list)

    def add_row(self, *values: object) -> None:
        self.rows.append([str(value) for value in values])

    def __len__(self) -> int:
        return len(self.rows)


def to_csv_text(report: Report) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(report.columns)
    writer.writerows(report.rows)
    return buffer.getvalue()


def to_text_table(report: Report) -> str:
    widths = [len(column) for column in report.columns]
    for row in report.rows:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]
    lines = [report.title, ""]
    lines.append("  ".join(column.ljust(width) for column, width in zip(report.columns, widths)))
    lines.append("  ".join("-" * width for width in widths))
    for row in report.rows:
        lines.append("  ".join(value.ljust(width) for value, width in zip(row, widths)))
    return "\n".join(lines) + "\n"
