"""Custodian Garden / Gold Pages — shifting non-ranked hash directory.

Hover reveal. Manual intent. No favorites, analytics, or personalization.
Hashes only. Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from aznet.canon import DEMO_SEEDS, sha256_text
from aznet.clock import advise


def demo_cards() -> list[dict[str, str]]:
    """Public demo hashes. Not user content. Not ranked."""
    cards = []
    for i, seed in enumerate(DEMO_SEEDS):
        cards.append(
            {
                "slot": str(i),
                "label": f"card-{i}",
                "hash_hex": sha256_text(seed),
                "seed_kind": "public-demo-label",
            }
        )
    return cards


def shift(now: str | None = None) -> list[dict[str, str]]:
    """Rotate the directory by StaticClock stamp. Non-ranked. No personalization."""
    cards = demo_cards()
    clock = advise(now)
    offset = int(clock["stamp"][:8], 16) % len(cards)
    rotated = cards[offset:] + cards[:offset]
    for i, card in enumerate(rotated):
        card["order"] = str(i)
        card["rank"] = "none"
        card["favorite"] = "forbidden"
    return rotated


def garden_view(now: str | None = None) -> dict[str, Any]:
    clock = advise(now)
    return {
        "name": "Custodian Garden / Gold Pages",
        "kind": "shifting non-ranked hash directory",
        "hover_reveal": True,
        "manual_intent": True,
        "favorites": False,
        "analytics": False,
        "personalization": False,
        "payloads": False,
        "staticclock": clock,
        "cards": shift(clock["local"]),
        "note": "Hashes only. Worker is a demo garden. Device-local silent node is the real posture.",
    }
