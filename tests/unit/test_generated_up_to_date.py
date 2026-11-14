"""src/generated/ must be exactly what the feed contract produces."""

from tools.generate_feed_types import load_contract, out_of_date, render_all


def test_generated_files_match_the_contract():
    stale = out_of_date(load_contract())
    assert stale == [], (
        f"src/generated/ differs from contracts/feed_contract.json: {stale}. "
        "Change the contract and run tools/generate_feed_types.py; never edit generated files."
    )


def test_every_feed_has_a_module():
    assert set(render_all(load_contract())) == {"__init__.py", "member_feed.py", "contribution_feed.py"}


def test_personal_fields_are_classified():
    from generated import MemberRecord

    assert MemberRecord.PERSONAL == {"ni_number", "surname", "forenames", "date_of_birth"}
