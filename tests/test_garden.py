"""Garden is non-ranked and hash-only."""

from __future__ import annotations

from aznet.garden import demo_cards, garden_view, shift


def test_demo_cards_are_hashes() -> None:
    cards = demo_cards()
    assert len(cards) == 8
    for card in cards:
        assert len(card["hash_hex"]) == 64
        assert card["hash_hex"].isalnum()


def test_shift_has_no_rank_or_favorites() -> None:
    cards = shift("2026-09-06T00:00:00Z")
    assert all(c["rank"] == "none" for c in cards)
    assert all(c["favorite"] == "forbidden" for c in cards)


def test_garden_view_forbids_engagement() -> None:
    view = garden_view("2026-09-06T00:00:00Z")
    assert view["favorites"] is False
    assert view["analytics"] is False
    assert view["personalization"] is False
    assert view["payloads"] is False
    assert view["hover_reveal"] is True
    assert view["manual_intent"] is True
