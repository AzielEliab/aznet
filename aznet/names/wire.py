"""AZN-NAME-1.0 statements in FED-MESH-1.0 canonical form.

Handle, signature, and statement hash match aziel-runtime FED-MESH-1.0.
The Mesh Security constants below are this repo's copy. FED-MESH-1.0.md
on the runtime branch does not yet publish a Mesh Security section.
Change the numbers here if that section lands with different values.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping

FED_SPEC = "FED-MESH-1.0"
SPEC = "AZN-NAME-1.0"
ANCHOR_SPEC = "AZN-NAME-ANCHOR-1.0"
SYNC_SPEC = "AZN-NAME-SYNC-1.0"
AUTHOR = "Aziel Eliab"

MESH_TLD = "aziel"
DNS_CCTLD_AZ = "az"
CAP_PER_HANDLE = 7
GENESIS_PREV = "0" * 64

# Mesh Security. Small on purpose so a claim is costly to flood and cheap to test.
POW_BITS_MIN = 8
WITNESS_K = 3
WITNESS_AGE_SECONDS = 72 * 60 * 60

# FED-MESH section 5.1. Security statements are extra kinds. The runtime
# spec has no Mesh Security section yet.
KIND_NAME = "name"
KIND_CLAIM = KIND_NAME
KIND_WITNESS = "name-witness"
KIND_VOUCH = "vouch"
KIND_ADVISORY = "advisory"
NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.aziel$")
REF_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_./-]{0,63}$")

OPS = ("claim", "update", "transfer", "release", "renew")
TARGET_KINDS = ("object", "ref", "node", "none")
RENEWALS = ("until-release", "expiring")
ADVISORY_NOTE_MAX = 80

HANDLE_RE = re.compile(r"^#[0-9A-HJKMNP-TV-Z]{11}$")
HANDLE_BODY_RE = re.compile(r"^[0-9a-hjkmnp-tv-z]{11}$")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_HASH = re.compile(r"^[0-9a-f]{64}$")
_NONCE = re.compile(r"^[0-9a-f]{1,16}$")
_LIST_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,31}$")

OK = "OK"
SELF_CERT = "SELF_CERT"
IDEMPOTENT = "IDEMPOTENT"
UNCLAIMED = "UNCLAIMED"
PENDING = "PENDING"
FINAL = "FINAL"
BAD_SIGNATURE = "BAD_SIGNATURE"
FORK = "FORK"
EXPIRED = "EXPIRED"
REVOKED = "REVOKED"
OVER_CAP = "OVER_CAP"
LOST_RACE = "LOST_RACE"
NOT_OWNER = "NOT_OWNER"
BAD_CHAIN = "BAD_CHAIN"
BAD_SEQUENCE = "BAD_SEQUENCE"
ROLLBACK = "ROLLBACK"
DNS_FALLTHROUGH = "DNS_FALLTHROUGH"
NOT_MESH = "NOT_MESH"
MALFORMED = "MALFORMED"
SELF_CERT_FIXED = "SELF_CERT_FIXED"
LEAK = "LEAK"
NO_EXEC = "NO_EXEC"
POW_FAIL = "POW_FAIL"
POW_WEAK = "POW_WEAK"
EQUIVOCATION = "EQUIVOCATION"
WAIT = "WAIT"

ABSENT = "ABSENT"

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
        "pkcs8",
        "enc_private_key",
    }
)

EXEC_KEYS = frozenset(
    {
        "code",
        "wasm",
        "script",
        "contract",
        "smart_contract",
        "bytecode",
        "source",
    }
)


def is_hash(value: str) -> bool:
    return bool(_HASH.match(value))


def is_handle(value: str) -> bool:
    return bool(HANDLE_RE.match(value))


def is_timeslate(value: str) -> bool:
    return bool(_ISO.match(value))


def is_nonce(value: str) -> bool:
    return bool(_NONCE.match(value))


def is_list_id(value: str) -> bool:
    return bool(_LIST_ID.match(value))


def anchor_hash(fields: Mapping[str, Any]) -> str:
    body = {
        "anchored_at": fields.get("anchored_at") or "",
        "kind": fields["kind"],
        "name": fields["name"],
        "prev_hash": fields["prev_hash"],
        "prior_hash": fields.get("prior_hash") or "",
        "record_hash": fields["record_hash"],
        "spec": ANCHOR_SPEC,
        "timeslate": fields["timeslate"],
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
