"""Versioned name blocklist for friendly ``.aziel`` claims.

Policy: no pornography, no sexual content involving children, no hate
names. Version ``FED-MESH-BLOCKLIST-1`` is the runtime token list.
Matching follows ``nameBlockHit``: drop every character that is not a
letter or digit, then test the longest substring tokens first. Digit
lookalikes ``0 1 3 4 5 7`` are also read as ``o i e a s t``, so a
separator or a digit swap does not hide a token. This is still a label
check. It misses paraphrases, other spellings, and other languages.

Author: Aziel Eliab only.
"""

from __future__ import annotations

BLOCKLIST_VERSION = "FED-MESH-BLOCKLIST-1"

# Same tokens and scopes as aziel-runtime ``NAME_BLOCKLIST``.
# scope "substring": the folded label contains the token (length >= 4).
# scope "exact": the whole label or one hyphen-part only.
_ROWS = (
    ("childporn", "substring"),
    ("childsex", "substring"),
    ("jailbait", "substring"),
    ("pedophile", "substring"),
    ("paedophile", "substring"),
    ("underage", "substring"),
    ("preteen", "substring"),
    ("csam", "substring"),
    ("porn", "substring"),
    ("porno", "substring"),
    ("pornhub", "substring"),
    ("hentai", "substring"),
    ("onlyfans", "substring"),
    ("nsfw", "substring"),
    ("sexcam", "substring"),
    ("camgirl", "substring"),
    ("xvideos", "substring"),
    ("xhamster", "substring"),
    ("rule34", "substring"),
    ("nude", "substring"),
    ("nudes", "substring"),
    ("sex", "exact"),
    ("xxx", "exact"),
    ("milf", "exact"),
    ("anal", "exact"),
    ("nazi", "substring"),
    ("nazism", "substring"),
    ("whitepower", "substring"),
    ("whitesupremac", "substring"),
    ("killall", "substring"),
    ("kkk", "exact"),
)

# After separators are removed. Same pairs nameBlockHit needs for ch1ldp0rn.
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})


def _label(name: str) -> str:
    text = str(name or "").strip().lower()
    suffix = ".aziel"
    if text.endswith(suffix):
        text = text[: -len(suffix)]
    return text


def _alnum(text: str) -> str:
    return "".join(ch for ch in text if ch.isalnum())


def name_blocked(name: str) -> str | None:
    """Return the blocklist version when ``name`` matches, else None.

    ``name`` may be a label (``child.porn``) or a mesh name
    (``child-porn.aziel``). The ``.aziel`` suffix is not part of the label.
    """
    raw = _label(name)
    if not raw:
        return None
    folded = _alnum(raw)
    leet = folded.translate(_LEET)
    parts = [part for part in raw.split("-") if part]
    part_keys = []
    for part in parts:
        part_folded = _alnum(part)
        part_keys.append(part_folded)
        part_keys.append(part_folded.translate(_LEET))
    substrings = sorted(
        (token for token, scope in _ROWS if scope != "exact" and len(token) >= 4),
        key=len,
        reverse=True,
    )
    for token in substrings:
        if token in folded or token in leet or token in raw:
            return BLOCKLIST_VERSION
    for token, _scope in _ROWS:
        if raw == token or folded == token or leet == token or token in parts or token in part_keys:
            return BLOCKLIST_VERSION
    return None
