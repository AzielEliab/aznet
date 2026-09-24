"""Ed25519 sign and verify (RFC 8032) using stdlib hashlib only.

Private seeds stay with the caller. This module never writes them.
Arithmetic follows the public-domain ed25519 reference and RFC 8032
clamping, with extended coordinates so tests stay practical.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib

P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = (-121665 * pow(121666, P - 2, P)) % P
I = pow(2, (P - 1) // 4, P)
_IDENTITY = (0, 1, 1, 0)


def _sha512(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def _recover_x(y: int, sign: int) -> int:
    if y >= P:
        raise ValueError("non-canonical y")
    y2 = (y * y) % P
    u = (y2 - 1) % P
    v = (D * y2 + 1) % P
    x = pow((u * pow(v, P - 2, P)) % P, (P + 3) // 8, P)
    if (v * x * x - u) % P != 0:
        x = (x * I) % P
    if (v * x * x - u) % P != 0:
        raise ValueError("point is not on the curve")
    if (x & 1) != sign:
        x = P - x
    return x


def _encode_point(pt: tuple[int, int, int, int]) -> bytes:
    x, y, z, _t = pt
    inv_z = pow(z, P - 2, P)
    x_aff = (x * inv_z) % P
    y_aff = (y * inv_z) % P
    bits = y_aff | ((x_aff & 1) << 255)
    return bits.to_bytes(32, "little")


def _decode_point(raw: bytes) -> tuple[int, int, int, int]:
    if len(raw) != 32:
        raise ValueError("point length")
    y = int.from_bytes(raw, "little") & ((1 << 255) - 1)
    sign = raw[31] >> 7
    x = _recover_x(y, sign)
    return (x, y, 1, (x * y) % P)


def _add(p1: tuple[int, int, int, int], p2: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x1, y1, z1, t1 = p1
    x2, y2, z2, t2 = p2
    a = ((y1 - x1) * (y2 - x2)) % P
    b = ((y1 + x1) * (y2 + x2)) % P
    c = (t1 * (2 * D) * t2) % P
    d = (z1 * 2 * z2) % P
    e = (b - a) % P
    f = (d - c) % P
    g = (d + c) % P
    h = (b + a) % P
    return ((e * f) % P, (g * h) % P, (f * g) % P, (e * h) % P)


def _double(pt: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x1, y1, z1, _t1 = pt
    a = (x1 * x1) % P
    b = (y1 * y1) % P
    c = (2 * z1 * z1) % P
    h = (a + b) % P
    e = (h - ((x1 + y1) * (x1 + y1))) % P
    g = (a - b) % P
    f = (c + g) % P
    return ((e * f) % P, (g * h) % P, (f * g) % P, (e * h) % P)


def _scalarmult(pt: tuple[int, int, int, int], scalar: int) -> tuple[int, int, int, int]:
    result = _IDENTITY
    addend = pt
    if scalar < 0:
        raise ValueError("negative scalar")
    while scalar:
        if scalar & 1:
            result = _add(result, addend)
        addend = _double(addend)
        scalar >>= 1
    return result


def _base_point() -> tuple[int, int, int, int]:
    by = (4 * pow(5, P - 2, P)) % P
    bx = _recover_x(by, 0)
    return (bx, by, 1, (bx * by) % P)


_B = _base_point()


def _clamp_scalar(seed: bytes) -> tuple[int, bytes]:
    digest = _sha512(seed)
    a = int.from_bytes(digest[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, digest


def _is_identity(pt: tuple[int, int, int, int]) -> bool:
    encoded = _encode_point(pt)
    return encoded == _encode_point(_IDENTITY)


def public_key(seed: bytes) -> bytes:
    """Return the 32-byte public key for a 32-byte seed. The seed is not retained."""
    if len(seed) != 32:
        raise ValueError("Ed25519 seed must be 32 bytes")
    scalar, _prefix = _clamp_scalar(seed)
    return _encode_point(_scalarmult(_B, scalar))


def sign(seed: bytes, message: bytes) -> bytes:
    """Sign ``message``. Returns 64 bytes. Does not store ``seed``."""
    if len(seed) != 32:
        raise ValueError("Ed25519 seed must be 32 bytes")
    scalar, digest = _clamp_scalar(seed)
    public = _encode_point(_scalarmult(_B, scalar))
    r = int.from_bytes(_sha512(digest[32:] + message), "little") % L
    R = _encode_point(_scalarmult(_B, r))
    k = int.from_bytes(_sha512(R + public + message), "little") % L
    S = (r + k * scalar) % L
    return R + S.to_bytes(32, "little")


def verify(public: bytes, message: bytes, signature: bytes) -> bool:
    """Return True when ``signature`` is valid for ``message`` under ``public``."""
    if len(public) != 32 or len(signature) != 64:
        return False
    try:
        A = _decode_point(public)
        if _is_identity(_scalarmult(A, 8)):
            return False
        R = _decode_point(signature[:32])
        S = int.from_bytes(signature[32:], "little")
        if S >= L:
            return False
        k = int.from_bytes(_sha512(signature[:32] + public + message), "little") % L
        left = _encode_point(_scalarmult(_B, S))
        right = _encode_point(_add(R, _scalarmult(A, k)))
    except ValueError:
        return False
    return left == right
