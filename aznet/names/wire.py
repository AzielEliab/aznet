"""AZN-NAME-1.0 wire format. One module so a merged FED-MESH can be aligned here.

Nothing in this file opens a socket, stores a private key, or carries a payload.
Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

SPEC = "AZN-NAME-1.0"
ANCHOR_SPEC = "AZN-NAME-ANCHOR-1.0"
SYNC_SPEC = "AZN-NAME-SYNC-1.0"
AUTHOR = "Aziel Eliab"

# Empty today would cross-protocol-replay more easily. The prefix is a local
# choice until FED-MESH specifies the signed bytes. Change it here only.
SIGNATURE_PREFIX = b"AZN-NAME-1.0\x00"

MESH_TLD = "aziel"
DNS_CCTLD_AZ = "az"
CAP_PER_HANDLE = 7
HANDLE_PREFIX = "#"
HANDLE_HEX_LEN = 64
GENESIS_PREV = "0" * 64

OPS = ("claim", "update", "transfer", "release", "renew")
TARGET_KINDS = ("object", "ref", "node", "none")
RENEWALS = ("until-release", "expiring")

# Signed body. ``signature`` and ``record_hash`` are outside this set.
SIGNED_FIELDS = (
    "expires_at",
    "handle_prev",
    "keys",
    "name",
    "op",
    "owner",
    "payload",
    "prev",
    "renewal",
    "sequence",
    "spec",
    "successor",
    "target",
    "target_kind",
    "timeslate",
    "user_content",
)

RECORD_FIELDS = SIGNED_FIELDS + ("record_hash", "signature")

ABSENT = "ABSENT"

# Refusal / result codes. Stable for AZBrowser and qnm-node.
OK = "OK"
SELF_CERT = "SELF_CERT"
IDEMPOTENT = "IDEMPOTENT"
UNCLAIMED = "UNCLAIMED"
BAD_SIGNATURE = "BAD_SIGNATURE"
FORK = "FORK"
EXPIRED = "EXPIRED"
REVOKED = "REVOKED"
OVER_CAP = "OVER_CAP"
LOST_RACE = "LOST_RACE"
NOT_OWNER = "NOT_OWNER"
BAD_CHAIN = "BAD_CHAIN"
BAD_SEQUENCE = "BAD_SEQUENCE"
DNS_FALLTHROUGH = "DNS_FALLTHROUGH"
NOT_MESH = "NOT_MESH"
MALFORMED = "MALFORMED"
SELF_CERT_FIXED = "SELF_CERT_FIXED"
LEAK = "LEAK"
WAIT = "WAIT"

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_HANDLE = re.compile(r"^#[0-9a-f]{64}$")

LEAK_KEYS = frozenset(
    {
        "private_key",
        "secret",
        "seed",
        "signing_key",
        "key_material",
        "password",
        "payload_bytes",
        "ciphertext",
        "plaintext",
        "user_text",
        "body",
        "content",
        "file",
        "bytes",
        "video",
        "mp4",
    }
)


def canonical_bytes(fields: Mapping[str, Any]) -> bytes:
    """UTF-8 JSON, sorted keys, no extra whitespace, signed fields only."""
    payload = {key: fields[key] for key in SIGNED_FIELDS}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return raw.encode("utf-8")


def signature_message(fields: Mapping[str, Any]) -> bytes:
    return SIGNATURE_PREFIX + canonical_bytes(fields)


def record_hash(fields: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(fields)).hexdigest()


def anchor_hash(fields: Mapping[str, Any]) -> str:
    body = {
        "kind": fields["kind"],
        "name": fields["name"],
        "prev_hash": fields["prev_hash"],
        "record_hash": fields["record_hash"],
        "spec": ANCHOR_SPEC,
        "timeslate": fields["timeslate"],
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def is_hash(value: str) -> bool:
    return bool(_HASH.match(value))


def is_handle(value: str) -> bool:
    return bool(_HANDLE.match(value))


def is_timeslate(value: str) -> bool:
    return bool(_ISO.match(value))
