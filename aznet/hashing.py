"""Hashing helpers for AZNet.

Re-exports canonical encoding from ``canon``. Stdlib ``hashlib`` only.
Author: Aziel Eliab only.
"""

from __future__ import annotations

from aznet.canon import (
    ABSENT,
    ACTOR_OPERATOR,
    GENESIS_PREV_HASH,
    HASH_FIELDS,
    MARKER,
    SPEC,
    canonical_bytes,
    canonical_object,
    digest,
    sha256_text,
    witness_digest,
)

__all__ = [
    "ABSENT",
    "ACTOR_OPERATOR",
    "GENESIS_PREV_HASH",
    "HASH_FIELDS",
    "MARKER",
    "SPEC",
    "canonical_bytes",
    "canonical_object",
    "digest",
    "sha256_text",
    "witness_digest",
]
