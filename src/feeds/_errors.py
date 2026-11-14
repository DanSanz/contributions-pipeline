from __future__ import annotations


class FeedError(ValueError):
    """A feed file that cannot be read.

    ``line_no`` is the 1-based line in the file (0 when the problem is the whole file).
    ``reason`` says what is wrong without quoting any field value: files carry personal data.
    """

    def __init__(self, line_no: int, reason: str, *, file_id: str | None = None) -> None:
        where = f"{file_id} line {line_no}" if file_id else f"line {line_no}"
        super().__init__(f"{where}: {reason}")
        self.line_no = line_no
        self.reason = reason
        self.file_id = file_id
