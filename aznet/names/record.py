"""Signed name records. The seed is used to sign and then dropped.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any, Mapping

from aznet.errors import NameRefuse
from aznet.names.ed25519 import public_key, sign, verify
from aznet.names.namespace import classify
from aznet.names.wire import (
    ABSENT,
    BAD_SIGNATURE,
    DNS_FALLTHROUGH,
    LEAK,
    LEAK_KEYS,
    MALFORMED,
    NOT_MESH,
    NOT_OWNER,
    RECORD_FIELDS,
    SPEC,
    is_handle,
    is_hash,
    is_timeslate,
    record_hash,
    signature_message,
)


def _leak_keys(data: Mapping[str, Any]) -> None:
    found = LEAK_KEYS.intersection(data)
    if found:
        raise NameRefuse(LEAK, "name records carry hashes and handles, never keys or payloads")
    for key in ("payload", "keys", "user_content"):
        if data.get(key) not in (None, ABSENT):
            raise NameRefuse(LEAK, f"{key} must be ABSENT")


def sign_record(seed: bytes, **fields: Any) -> dict[str, Any]:
    """Sign a name record with a node-local seed. The seed is not copied into the result."""
    if not isinstance(seed, (bytes, bytearray)) or len(seed) != 32:
        raise NameRefuse(MALFORMED, "signing seed must be 32 bytes and is not stored")
    pub = public_key(bytes(seed))
    owner = "#" + pub.hex()
    body = {
        "expires_at": fields.get("expires_at") or "",
        "handle_prev": fields.get("handle_prev") or "",
        "keys": ABSENT,
        "name": fields.get("name") or "",
        "op": fields.get("op") or "",
        "owner": fields.get("owner") or owner,
        "payload": ABSENT,
        "prev": fields.get("prev") or "",
        "renewal": fields.get("renewal") or "until-release",
        "sequence": fields.get("sequence"),
        "spec": SPEC,
        "successor": fields.get("successor") or "",
        "target": fields.get("target") if fields.get("target") is not None else "",
        "target_kind": fields.get("target_kind") or "",
        "timeslate": fields.get("timeslate") or "",
        "user_content": ABSENT,
    }
    if body["owner"] != owner:
        raise NameRefuse(NOT_OWNER, "owner handle must be the public key of the signing seed")
    normalized = prepare(body | {"signature": "00" * 64, "record_hash": "0" * 64}, check_signature=False)
    digest = record_hash(normalized)
    signature = sign(bytes(seed), signature_message(normalized))
    out = dict(normalized)
    out["record_hash"] = digest
    out["signature"] = signature.hex()
    prepare(out)
    return out


def prepare(data: Mapping[str, Any], *, check_signature: bool = True) -> dict[str, Any]:
    """Validate shape. When ``check_signature`` is set, also verify the owner key."""
    if not isinstance(data, Mapping):
        raise NameRefuse(MALFORMED, "name record must be an object")
    _leak_keys(data)
    unknown = set(data) - set(RECORD_FIELDS)
    if unknown:
        raise NameRefuse(MALFORMED, "unknown name-record fields")
    missing = [key for key in RECORD_FIELDS if key not in data and key not in {"signature", "record_hash"}]
    if missing and check_signature:
        raise NameRefuse(MALFORMED, "missing name-record fields")
    try:
        sequence = data.get("sequence")
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
            raise NameRefuse(MALFORMED, "sequence must be an integer ≥ 1")
        name = str(data.get("name") or "")
        classified = classify(name)
        if classified.code in {DNS_FALLTHROUGH, NOT_MESH, MALFORMED} or classified.name is None:
            code = classified.code or MALFORMED
            raise NameRefuse(code, "name is not a mesh ledger key")
        if name != classified.name:
            raise NameRefuse(MALFORMED, f"sign the canonical name {classified.name}")
        owner = str(data.get("owner") or "")
        if not is_handle(owner):
            raise NameRefuse(MALFORMED, "owner must be a # handle")
        if classified.kind == "self_cert" and classified.owner_handle != owner:
            raise NameRefuse(NOT_OWNER, "a self-certifying name is owned by the key inside it")
        prev = str(data.get("prev") or "")
        handle_prev = str(data.get("handle_prev") or "")
        if not is_hash(prev) or not is_hash(handle_prev):
            raise NameRefuse(MALFORMED, "prev and handle_prev must be 64-char hex")
        timeslate = str(data.get("timeslate") or "")
        if not is_timeslate(timeslate):
            raise NameRefuse(MALFORMED, "timeslate must be YYYY-MM-DDTHH:MM:SSZ")
        expires_at = str(data.get("expires_at") or "")
        renewal = str(data.get("renewal") or "")
        if renewal not in {"until-release", "expiring"}:
            raise NameRefuse(MALFORMED, "renewal must be until-release or expiring")
        if renewal == "until-release" and expires_at:
            raise NameRefuse(MALFORMED, "until-release records have an empty expires_at")
        if renewal == "expiring":
            if not is_timeslate(expires_at) or expires_at <= timeslate:
                raise NameRefuse(MALFORMED, "expiring records need expires_at after timeslate")
        op = str(data.get("op") or "")
        if op not in {"claim", "update", "transfer", "release", "renew"}:
            raise NameRefuse(MALFORMED, "op is not a name-record operation")
        if str(data.get("spec") or "") != SPEC:
            raise NameRefuse(MALFORMED, f"spec must be {SPEC}")
        target_kind = str(data.get("target_kind") or "")
        target = str(data.get("target") or "")
        successor = str(data.get("successor") or "")
        _check_target(op, target_kind, target, successor, owner)
        body = {
            "expires_at": expires_at,
            "handle_prev": handle_prev,
            "keys": ABSENT,
            "name": name,
            "op": op,
            "owner": owner,
            "payload": ABSENT,
            "prev": prev,
            "renewal": renewal,
            "sequence": sequence,
            "spec": SPEC,
            "successor": successor,
            "target": target,
            "target_kind": target_kind,
            "timeslate": timeslate,
            "user_content": ABSENT,
        }
    except NameRefuse:
        raise
    except (TypeError, ValueError) as exc:
        raise NameRefuse(MALFORMED, str(exc)) from exc

    digest = record_hash(body)
    if not check_signature:
        return body
    signature_hex = str(data.get("signature") or "")
    stored = str(data.get("record_hash") or "")
    if stored != digest:
        raise NameRefuse(BAD_SIGNATURE, "record_hash is not the hash of the signed body")
    try:
        signature = bytes.fromhex(signature_hex)
        pub = bytes.fromhex(owner[1:])
    except ValueError as exc:
        raise NameRefuse(BAD_SIGNATURE, "signature or owner handle is not hex") from exc
    if not verify(pub, signature_message(body), signature):
        raise NameRefuse(BAD_SIGNATURE, "owner signature did not verify")
    out = dict(body)
    out["record_hash"] = digest
    out["signature"] = signature.hex()
    return out


def _check_target(op: str, target_kind: str, target: str, successor: str, owner: str) -> None:
    if "://" in target or "://" in successor:
        raise NameRefuse(MALFORMED, "targets are hashes or handles, not URLs")
    if op == "release":
        if target_kind != "none" or target or successor:
            raise NameRefuse(MALFORMED, "release clears target and successor")
        return
    if op == "transfer":
        if not is_handle(successor) or successor == owner:
            raise NameRefuse(MALFORMED, "transfer names a different successor handle")
    elif successor:
        raise NameRefuse(MALFORMED, "successor is set only on transfer")
    if target_kind in {"object", "ref"}:
        if not is_hash(target):
            raise NameRefuse(MALFORMED, "object and ref targets are 64-char hex")
        return
    if target_kind == "node":
        if not is_handle(target):
            raise NameRefuse(MALFORMED, "node targets are handles")
        return
    raise NameRefuse(MALFORMED, "target_kind must be object, ref, or node")
