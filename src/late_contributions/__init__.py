"""Late employer contributions (spec: late contributions v2).

Interface:
    assess(rows, run_date) -> list[Assessment]
    from_feed(records) -> (list[FeedRow], list[RowError])
    due_date(period) -> date

Contributions for a period are due on the 22nd of the following month. When the 22nd is not
a working day, they are due on the next working day.
"""

from late_contributions._assess import Assessment, FeedRow, assess, due_date
from late_contributions._from_feed import RowError, from_feed

__all__ = ["Assessment", "FeedRow", "RowError", "assess", "due_date", "from_feed"]
