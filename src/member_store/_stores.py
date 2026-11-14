from __future__ import annotations

import sqlite3
from dataclasses import astuple, fields
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Protocol

from generated import MemberRecord

from member_store._model import Member, member_from_record


class MemberStore(Protocol):
    def upsert(self, member: Member) -> None: ...

    def get(self, member_ref: str) -> Member | None: ...

    def all(self) -> list[Member]: ...

    def count(self) -> int: ...


class InMemoryMemberStore:
    def __init__(self) -> None:
        self._members: dict[str, Member] = {}

    def upsert(self, member: Member) -> None:
        self._members[member.member_ref] = member

    def get(self, member_ref: str) -> Member | None:
        return self._members.get(member_ref)

    def all(self) -> list[Member]:
        return [self._members[ref] for ref in sorted(self._members)]

    def count(self) -> int:
        return len(self._members)


_COLUMNS = [field.name for field in fields(Member)]

_CREATE = f"""
CREATE TABLE IF NOT EXISTS members (
    {", ".join(f"{name} TEXT NOT NULL" for name in _COLUMNS)},
    PRIMARY KEY (member_ref)
)
"""

_UPSERT = f"""
INSERT INTO members ({", ".join(_COLUMNS)})
VALUES ({", ".join("?" for _ in _COLUMNS)})
ON CONFLICT (member_ref) DO UPDATE SET
    {", ".join(f"{name} = excluded.{name}" for name in _COLUMNS if name != "member_ref")}
"""


class SqliteMemberStore:
    """Members in a SQLite file, or in memory with ``":memory:"``."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path))
        self._db.execute(_CREATE)

    def upsert(self, member: Member) -> None:
        with self._db:
            self._db.execute(_UPSERT, [str(value) for value in astuple(member)])

    def get(self, member_ref: str) -> Member | None:
        row = self._db.execute(
            f"SELECT {', '.join(_COLUMNS)} FROM members WHERE member_ref = ?", [member_ref]
        ).fetchone()
        return _to_member(row) if row else None

    def all(self) -> list[Member]:
        rows = self._db.execute(
            f"SELECT {', '.join(_COLUMNS)} FROM members ORDER BY member_ref"
        ).fetchall()
        return [_to_member(row) for row in rows]

    def count(self) -> int:
        return self._db.execute("SELECT COUNT(*) FROM members").fetchone()[0]

    def close(self) -> None:
        self._db.close()


def _to_member(row: tuple) -> Member:
    values = dict(zip(_COLUMNS, row))
    values["salary"] = Decimal(values["salary"])
    return Member(**values)


def load_members(store: MemberStore, records: Iterable[MemberRecord], *, file_id: str) -> int:
    """Upsert each record into ``store`` by member reference. Returns the number loaded."""
    loaded = 0
    for record in records:
        store.upsert(member_from_record(record, file_id=file_id))
        loaded += 1
    return loaded
