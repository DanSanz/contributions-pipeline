"""Member lookups for the reports and the valuation job."""

from __future__ import annotations

from member_store import Member, MemberStore

__all__ = ["MemberService"]


class MemberService:
    def __init__(self, store: MemberStore) -> None:
        self._store = store

    def find(self, member_id: str) -> Member | None:
        return self._store.get(member_id)

    def everyone(self) -> list[Member]:
        return self._store.all()

    def how_many(self) -> int:
        return self._store.count()

    def exists(self, member_id: str) -> bool:
        return self._store.get(member_id) is not None
