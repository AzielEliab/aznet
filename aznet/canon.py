"""Canonical encoding for AZNet receipts (AZN-WP-0.1).

AZNet mirrors cryptographic hashes only. Payload, keys, and user
content are always ABSENT. UTF-8 JSON with sorted keys and no extra
whitespace. ``receipt_hash`` is excluded from the encoding.

Genesis ``prev_hash`` is 64 zero hex characters.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

SPEC = "AZN-WP-0.1"
ABSENT = "ABSENT"
ACTOR_OPERATOR = "operator"
GENESIS_PREV_HASH = "0" * 64
MARKER = "Truth Is No Defense — .AZNet — AZ."
PRODUCT = "AZNet"
VERSION = "0.1.0"
AUTHOR = "Aziel Eliab"
ROLE = "silent verification side-net"
MOTTO = "Verification without hosting. Presence without authority."
HONEST = (
    "THIS IS: a silent verification SIDE-NET (hash continuity, Custodian Garden, "
    "Memorial ledger). THIS IS NOT: an alt internet, a host, a payload store, a VPN, "
    "or a key store. The Worker is a control-plane / demo garden. Device-local silent "
    "node is the real posture. AZNet + AZBrowser are both required to run. FragGate "
    "unlocks access. StaticClock stamps time. Author Aziel Eliab only."
)

EVENT_KINDS = (
    "GARDEN",
    "STAMP",
    "MEMORIAL",
    "PAIR",
    "UNLOCK",
    "WITNESS",
    "WITHDRAW",
)
PAIR_STATES = ("UNPAIRED", "PAIRED", "BROKEN")
UNLOCK_STATES = ("LOCKED", "UNLOCKED")
MEMORIAL_REASONS = (
    "ui_altered",
    "integrity_refuse",
    "node_withdraw",
    "pair_broken",
    "witness_fail",
    "isolation",
)
NOTE_MAX = 80
WITNESS_SECTIONS = (
    "garden",
    "memorial",
    "stamps",
    "receipts",
    "pair",
    "unlock",
    "staticclock",
)

# Hashed fields (lexicographic via sort_keys). receipt_hash is excluded.
HASH_FIELDS = (
    "actor",
    "azbrowser",
    "aznet_node",
    "date_stamp",
    "event_kind",
    "final_hash",
    "fraggate",
    "genesis_hash",
    "hash_hex",
    "keys",
    "label",
    "marker",
    "note",
    "pair_status",
    "payload",
    "prev_hash",
    "reason",
    "spec",
    "staticclock",
    "summary",
    "timestamp",
    "unlock_status",
    "user_content",
    "witness_hash",
    "zone",
)

FORBIDDEN_KEYS = frozenset(
    {
        "payload_bytes",
        "ciphertext",
        "private_key",
        "secret",
        "user_text",
        "body",
        "exploit",
        "poc",
        "cve",
        "0day",
        "key_material",
        "password",
        "plaintext",
    }
)

# Public demo Gold Pages seeds. These are labels, not user content / payloads.
DEMO_SEEDS = (
    "AZNet Gold Pages card 0 — verification without hosting",
    "AZNet Gold Pages card 1 — presence without authority",
    "AZNet Gold Pages card 2 — withdrawal over coercion",
    "AZNet Gold Pages card 3 — silence as security",
    "AZNet Gold Pages card 4 — hash continuity",
    "AZNet Gold Pages card 5 — node sovereignty",
    "AZNet Gold Pages card 6 — memorial ledger",
    "AZNet Gold Pages card 7 — cold storage",
)


def canonical_object(record: Mapping[str, Any]) -> dict[str, Any]:
    """Build the hashed object. Payload / keys / user_content are forced ABSENT."""
    payload: dict[str, Any] = {}
    for key in HASH_FIELDS:
        payload[key] = record.get(key, None)
    payload["spec"] = SPEC
    payload["marker"] = MARKER
    payload["actor"] = ACTOR_OPERATOR
    payload["payload"] = ABSENT
    payload["keys"] = ABSENT
    payload["user_content"] = ABSENT
    return payload


def canonical_bytes(record: Mapping[str, Any]) -> bytes:
    """Return the AZN-WP-0.1 canonical UTF-8 encoding (sorted keys, no extra space)."""
    payload = canonical_object(record)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw.encode("utf-8")


def digest(record: Mapping[str, Any]) -> str:
    """SHA-256 (lowercase hex) of ``canonical_bytes(record)``."""
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


def sha256_text(text: str) -> str:
    """SHA-256 (lowercase hex) of UTF-8 text. Used for demo hashes and stamps."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def witness_digest() -> str:
    """Mandatory UI witness hash. If the UI is altered, this no longer matches."""
    joined = MARKER + "|" + "|".join(WITNESS_SECTIONS) + "|" + SPEC
    return sha256_text(joined)
