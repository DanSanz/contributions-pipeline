"""The member database, as the pipeline sees it.

Interface:
    load_members(store, records, *, file_id) -> int
    MemberStore: upsert, get, all, count
    InMemoryMemberStore, SqliteMemberStore

Production uses the member database adapter from the platform repository. This repository
has the in-memory and SQLite stores, for tests and local runs.
"""

from member_store._model import Member, member_from_record
from member_store._stores import InMemoryMemberStore, MemberStore, SqliteMemberStore, load_members

__all__ = [
    "InMemoryMemberStore",
    "Member",
    "MemberStore",
    "SqliteMemberStore",
    "load_members",
    "member_from_record",
]
