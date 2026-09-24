"""Versioned name blocklist for friendly ``.aziel`` claims.

Policy: no pornography, no sexual content involving children, no hate
names. Version ``FED-MESH-BLOCKLIST-1`` is the runtime list plus every
token this library already refused. This is a label check. It is not an
image classifier and it does not catch paraphrases, misspellings, or
words from every language. A missing match is a miss.

Author: Aziel Eliab only.
"""

from __future__ import annotations

BLOCKLIST_VERSION = "FED-MESH-BLOCKLIST-1"

# Union of the runtime FED-MESH-BLOCKLIST-1 tokens and the tokens this
# library already refused under AZN-BLOCK-1.0. Do not drop either side.
_TOKENS = (
    "childporn",
    "jailbait",
    "underage",
    "porn",
    "porno",
    "xxx",
    "hentai",
    "onlyfans",
    "nsfw",
    "camgirl",
    "nude",
    "nudes",
    "sex",
    "nazi",
    "nazism",
    "whitepower",
    "kkk",
    "sexcam",
    "pornhub",
    "xvideos",
    "xhamster",
    "rule34",
    "childsex",
    "pedophile",
    "paedophile",
    "preteen",
    "csam",
    "whitesupremac",
    "killall",
    "milf",
    "anal",
)

# Shorter than 4, or an ambiguous fragment. These match the whole label
# or one hyphen-separated part. They do not match inside a longer word,
# so "sex" misses "sussex", "kkk" misses a longer word, and "anal"
# misses "analysis".
_PART_ONLY = frozenset({"sex", "xxx", "kkk", "milf", "anal"})


def name_blocked(name: str) -> str | None:
    """Return the blocklist version when ``name`` matches, else None."""
    label = str(name or "").split(".", 1)[0].lower()
    if not label:
        return None
    parts = [part for part in label.split("-") if part]
    for token in _TOKENS:
        if label == token or token in parts:
            return BLOCKLIST_VERSION
        if token in _PART_ONLY or len(token) < 4:
            continue
        if token in label:
            return BLOCKLIST_VERSION
    return None
