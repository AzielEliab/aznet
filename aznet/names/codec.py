"""FED-MESH-1.0 bytes: canonical JSON, Crockford handles, hashcash.

Matches aziel-runtime ``canonicalize`` and ``handleFromRawPublicKey``
(PR branch cursor/fed-mesh-e546). Private seeds are not stored here.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
HANDLE_LEN = 11


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64url_decode(text: str) -> bytes | None:
    raw = str(text or "").strip()
    if not raw or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for ch in raw):
        return None
    pad = "=" * ((4 - len(raw) % 4) % 4)
    try:
        return base64.urlsafe_b64decode(raw + pad)
    except ValueError:
        return None


def canonicalize(value: Any) -> str:
    """Same bytes as aziel-runtime ``session-core.js`` ``canonicalize``."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return json.dumps(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(canonicalize(item) for item in value) + "]"
    if isinstance(value, dict):
        keys = sorted(value)
        return "{" + ",".join(json.dumps(key) + ":" + canonicalize(value[key]) for key in keys) + "}"
    raise TypeError(f"cannot canonicalize {type(value).__name__}")


def statement_hash(statement: dict[str, Any]) -> str:
    return hashlib.sha256(canonicalize(statement).encode("utf-8")).hexdigest()


def handle_from_public(raw: bytes) -> str:
    """``#`` plus 11 Crockford characters from the first 55 bits of SHA-256(pubkey)."""
    if len(raw) != 32:
        return ""
    digest = hashlib.sha256(raw).digest()
    acc = 0
    bits = 0
    out: list[str] = []
    for byte in digest:
        acc = (acc << 8) | byte
        bits += 8
        while bits >= 5 and len(out) < HANDLE_LEN:
            bits -= 5
            out.append(CROCKFORD[(acc >> bits) & 31])
        if len(out) == HANDLE_LEN:
            break
    if len(out) != HANDLE_LEN:
        return ""
    return "#" + "".join(out)


def pow_digest(statement_hash_hex: str, sig: str, nonce: str) -> str:
    """SHA-256 of statement hash, signature, and nonce, separated by newlines.

    Matches aziel-runtime ``namePowDigest``. The nonce is outside the signature.
    """
    return hashlib.sha256(f"{statement_hash_hex}\n{sig}\n{nonce}".encode("utf-8")).hexdigest()


def leading_zero_bits(hex_hash: str) -> int:
    number = int(hex_hash, 16)
    if number == 0:
        return 256
    return 256 - number.bit_length()


def find_pow(statement_hash_hex: str, sig: str, bits: int) -> dict[str, Any]:
    """Search a hashcash stamp. ``bits`` is small (the spec minimum is 8)."""
    limit = 1 << (bits + 12)
    for counter in range(limit):
        nonce = f"{counter:x}"
        digest = pow_digest(statement_hash_hex, sig, nonce)
        if leading_zero_bits(digest) >= bits:
            return {"bits": bits, "digest": digest, "nonce": nonce}
    raise RuntimeError("proof-of-work search exceeded its window")
