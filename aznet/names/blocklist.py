"""Versioned name blocklist for friendly ``.aziel`` claims.

Policy: no pornography, no sexual content involving children, no hate
names. This is a label check. It is not an image classifier and it does
not catch paraphrases, misspellings, or words from every language.
A missing match is a miss. Classifiers on the hosting node are a
separate check.

Author: Aziel Eliab only.
"""

from __future__ import annotations

BLOCKLIST_VERSION = "AZN-BLOCK-1.0"

# Length >= 5 matches inside the label. Shorter tokens match the whole
# label only, so ordinary words are not caught by a fragment.
_SUBSTRINGS = (
    "porn",
    "porno",
    "xxx",
    "hentai",
    "nsfw",
    "onlyfans",
    "sexcam",
    "camgirl",
    "pornhub",
    "xvideos",
    "xhamster",
    "rule34",
    "childporn",
    "childsex",
    "jailbait",
    "pedophile",
    "paedophile",
    "underage",
    "preteen",
    "csam",
    "nazi",
    "whitesupremac",
    "killall",
)
_EXACT = (
    "sex",
    "xxx",
    "nude",
    "nudes",
    "milf",
    "anal",
)


def _fold(label: str) -> str:
    return "".join(ch for ch in label.lower() if ch.isalnum())


def name_blocked(name: str) -> str | None:
    """Return the blocklist version when ``name`` matches, else None."""
    label = str(name or "").split(".", 1)[0]
    folded = _fold(label)
    if not folded:
        return None
    if folded in _EXACT:
        return BLOCKLIST_VERSION
    for token in _SUBSTRINGS:
        if len(token) >= 4 and token in folded:
            return BLOCKLIST_VERSION
    return None
