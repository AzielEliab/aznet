"""FED-MESH name statements plus witness, vouch, advisory, and isolation.

The seed is used to sign and then dropped. It is not a field on the result.
``pow`` is outside the signature: SHA-256 of the statement hash, the
signature, and the nonce, separated by newlines.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping

from aznet.errors import NameRefuse
from aznet.names.blocklist import name_blocked
from aznet.names.codec import (
    b64url,
    b64url_decode,
    canonicalize,
    find_pow,
    handle_from_public,
    leading_zero_bits,
    pow_digest,
    statement_hash,
)
from aznet.names.ed25519 import public_key, sign, verify
from aznet.names.namespace import CAP7_FACTORY_LABELS, classify
from aznet.names.wire import (
    ADVISORY_NOTE_MAX,
    BAD_SIGNATURE,
    DNS_FALLTHROUGH,
    EQUIVOCATION,
    EXEC_KEYS,
    FED_SPEC,
    GENESIS_PREV,
    ISOLATION_REASONS,
    KIND_ADVISORY,
    KIND_APPEAL,
    KIND_ISOLATION,
    KIND_NAME,
    KIND_VOUCH,
    KIND_WITNESS,
    POLICY,
    RESERVED,
    RESERVED_LABELS,
    LEAK,
    LEAK_KEYS,
    MALFORMED,
    MESH_TLD,
    NO_EXEC,
    NOT_MESH,
    NOT_OWNER,
    POW_BITS_MIN,
    POW_FAIL,
    POW_WEAK,
    REF_NAME_RE,
    SELF_CERT_FIXED,
    is_handle,
    is_hash,
    is_nonce,
    is_timeslate,
)


def _walk_keys(value: Any, found: set[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            found.add(str(key))
            _walk_keys(item, found)
    elif isinstance(value, list):
        for item in value:
            _walk_keys(item, found)


def _refuse_material(data: Mapping[str, Any]) -> None:
    found: set[str] = set()
    _walk_keys(data, found)
    if LEAK_KEYS.intersection(found):
        raise NameRefuse(LEAK, "statements carry hashes and handles, never keys or payloads")
    if EXEC_KEYS.intersection(found):
        raise NameRefuse(NO_EXEC, "a name statement is not code and is not executed")
    if "score" in found or "ranking" in found:
        raise NameRefuse(MALFORMED, "no score and no ranking on name or advisory statements")


def _identity(seed: bytes) -> tuple[str, str, bytes]:
    if not isinstance(seed, (bytes, bytearray)) or len(seed) != 32:
        raise NameRefuse(MALFORMED, "signing seed must be 32 bytes and is not stored")
    raw = public_key(bytes(seed))
    handle = handle_from_public(raw)
    if not is_handle(handle):
        raise NameRefuse(MALFORMED, "public key did not form a handle")
    return handle, b64url(raw), raw


def _sign(seed: bytes, statement: dict[str, Any]) -> dict[str, Any]:
    signature = sign(bytes(seed), canonicalize(statement).encode("utf-8"))
    out = dict(statement)
    out["sig"] = b64url(signature)
    out["record_hash"] = statement_hash(statement)
    return out


def timeslate_ms(value: str) -> int:
    parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return int(parsed.timestamp() * 1000)


def _canonical_name(raw: str) -> tuple[str, str]:
    classified = classify(raw)
    if classified.code == DNS_FALLTHROUGH:
        raise NameRefuse(DNS_FALLTHROUGH, ".az outside the allowlist stays on normal DNS")
    if classified.code == NOT_MESH or classified.name is None:
        raise NameRefuse(classified.code or MALFORMED, "name is not a mesh name")
    if not str(classified.name).endswith("." + MESH_TLD):
        raise NameRefuse(NOT_MESH, "AZ.* display names are cites of hub HTTPS, not FED-MESH name records")
    if classified.kind not in {"friendly", "self_cert", "az_allow"}:
        raise NameRefuse(MALFORMED, "name is not a mesh ledger key")
    label = classified.name.split(".", 1)[0]
    if label in RESERVED_LABELS:
        raise NameRefuse(RESERVED, "ae, corpus, godlock, and hdj are reserved hub-mirror slots")
    if label in CAP7_FACTORY_LABELS:
        raise NameRefuse(RESERVED, "MirageGrid factory labels are not .aziel names")
    if classified.kind != "self_cert" and name_blocked(classified.name):
        raise NameRefuse(POLICY, "name matches the versioned blocklist")
    return classified.name, classified.kind


def _target_type(kind: str) -> str:
    mapped = {"object": "hash", "hash": "hash", "ref": "ref", "node": "handle", "handle": "handle", "none": "none"}
    if kind not in mapped:
        raise NameRefuse(MALFORMED, "target type is hash, ref, or handle")
    return mapped[kind]


def _check_target_value(target_type: str, value: str) -> str:
    if target_type == "hash":
        if not is_hash(value):
            raise NameRefuse(MALFORMED, "hash targets are 64-char hex")
        return value
    if target_type == "ref":
        if not REF_NAME_RE.match(value):
            raise NameRefuse(MALFORMED, "ref targets match the FED-MESH ref name pattern")
        return value
    if target_type == "handle":
        if not is_handle(value):
            raise NameRefuse(MALFORMED, "handle targets are #handles")
        return value
    raise NameRefuse(MALFORMED, "target type is hash, ref, or handle")


def pow_meets(record: Mapping[str, Any]) -> None:
    """Require the FED-MESH ``pow`` stamp. It is outside the signature."""
    stamp = record.get("pow")
    digest = str(record.get("record_hash") or "")
    sig = str(record.get("sig") or "")
    if not isinstance(stamp, Mapping) or not is_hash(digest) or not sig:
        raise NameRefuse(POW_FAIL, "a friendly claim needs a pow stamp")
    nonce = str(stamp.get("nonce") or "")
    bits = stamp.get("bits")
    if not is_nonce(nonce):
        raise NameRefuse(POW_FAIL, "pow.nonce must be 1 to 64 lowercase hex characters")
    if isinstance(bits, bool) or not isinstance(bits, int) or bits < POW_BITS_MIN or bits > 256:
        raise NameRefuse(POW_WEAK, f"pow.bits must be at least {POW_BITS_MIN}")
    got = pow_digest(digest, sig, nonce)
    if stamp.get("digest") not in (None, "", got):
        raise NameRefuse(POW_FAIL, "pow.digest does not match the stamp")
    if leading_zero_bits(got) < bits:
        raise NameRefuse(POW_FAIL, f"proof-of-work does not meet {bits} leading zero bits")


def sign_record(seed: bytes, **fields: Any) -> dict[str, Any]:
    """Sign a FED-MESH ``kind: name`` statement. A friendly claim also gets proof-of-work."""
    handle, public, _raw = _identity(seed)
    op = str(fields.get("op") or "")
    if op not in {"claim", "update", "transfer", "release", "renew"}:
        raise NameRefuse(MALFORMED, "op is not a name-record operation")
    name, name_kind = _canonical_name(str(fields.get("name") or ""))
    if name_kind == "self_cert" and op in {"claim", "transfer", "release"}:
        raise NameRefuse(SELF_CERT_FIXED, "a self-certifying name is not claimed, transferred, or released")
    bits = fields.get("pow_bits", POW_BITS_MIN if op == "claim" and name_kind != "self_cert" else 0)
    if isinstance(bits, bool) or not isinstance(bits, int):
        raise NameRefuse(POW_WEAK, "pow_bits must be an integer")
    needs_pow = op == "claim" and name_kind != "self_cert"
    if needs_pow and bits < POW_BITS_MIN:
        raise NameRefuse(POW_WEAK, f"pow_bits must be at least {POW_BITS_MIN}")
    if not needs_pow and bits not in (0, None):
        raise NameRefuse(MALFORMED, "proof-of-work is required only on a friendly name claim")
    seq = fields.get("seq") if fields.get("seq") is not None else fields.get("sequence")
    prev_record = fields.get("prev_record") or fields.get("name_prev") or GENESIS_PREV
    target, owner = _name_ends(op, handle, fields)
    statement = {
        "expires": _expires_value(fields),
        "handle": handle,
        "kind": KIND_NAME,
        "name": name,
        "owner": owner,
        "prev": fields.get("prev") or GENESIS_PREV,
        "prev_record": prev_record,
        "public_key": public,
        "seq": seq,
        "target": target,
        "v": FED_SPEC,
    }
    prepared = prepare_statement(statement, check_signature=False)
    signed = _sign(seed, prepared)
    if needs_pow:
        signed["pow"] = find_pow(signed["record_hash"], signed["sig"], bits)
    return prepare_statement(signed)


def _name_ends(op: str, handle: str, fields: Mapping[str, Any]) -> tuple[Any, str]:
    if op == "release":
        return None, ""
    successor = str(fields.get("successor") or "")
    if op == "transfer":
        if not is_handle(successor) or successor == handle:
            raise NameRefuse(MALFORMED, "transfer names a different successor handle")
        owner = successor
    else:
        if successor:
            raise NameRefuse(MALFORMED, "successor is set only on transfer")
        owner = handle
    kind = _target_type(str(fields.get("target_kind") or fields.get("target_type") or "hash"))
    if kind == "none":
        raise NameRefuse(MALFORMED, "release is the only act with an empty target")
    value = fields.get("target")
    if isinstance(value, Mapping):
        kind = _target_type(str(value.get("type") or kind))
        value = value.get("value")
    return {"type": kind, "value": _check_target_value(kind, str(value or ""))}, owner


def _expires_value(fields: Mapping[str, Any]) -> Any:
    if "expires" in fields and fields.get("expires_at") not in (None, ""):
        raise NameRefuse(MALFORMED, "pass expires or expires_at, not both")
    if "expires" in fields:
        expires = fields.get("expires")
        if expires is None:
            return None
        if isinstance(expires, bool) or not isinstance(expires, int) or expires < 0:
            raise NameRefuse(MALFORMED, "expires is null or a unix millisecond time")
        return expires
    text = str(fields.get("expires_at") or "")
    if not text:
        return None
    if not is_timeslate(text):
        raise NameRefuse(MALFORMED, "expires_at must be YYYY-MM-DDTHH:MM:SSZ")
    return timeslate_ms(text)


def sign_witness(seed: bytes, **fields: Any) -> dict[str, Any]:
    handle, public, _raw = _identity(seed)
    statement = {
        "handle": handle,
        "kind": KIND_WITNESS,
        "prev": fields.get("prev") or GENESIS_PREV,
        "public_key": public,
        "seq": fields.get("seq"),
        "subject_hash": fields.get("subject_hash") or "",
        "subject_kind": fields.get("subject_kind") or "name",
        "v": FED_SPEC,
    }
    prepared = prepare_statement(statement, check_signature=False)
    signed = _sign(seed, prepared)
    return prepare_statement(signed)


def sign_vouch(seed: bytes, **fields: Any) -> dict[str, Any]:
    handle, public, _raw = _identity(seed)
    statement = {
        "handle": handle,
        "kind": KIND_VOUCH,
        "prev": fields.get("prev") or GENESIS_PREV,
        "public_key": public,
        "seq": fields.get("seq"),
        "subject": fields.get("subject") or fields.get("subject_handle") or "",
        "subject_public_key": fields.get("subject_public_key") or "",
        "v": FED_SPEC,
    }
    prepared = prepare_statement(statement, check_signature=False)
    signed = _sign(seed, prepared)
    return prepare_statement(signed)


def sign_advisory(seed: bytes, **fields: Any) -> dict[str, Any]:
    handle, public, _raw = _identity(seed)
    _refuse_material(fields)
    statement = {
        "handle": handle,
        "kind": KIND_ADVISORY,
        "note": fields.get("note") or "",
        "prev": fields.get("prev") or GENESIS_PREV,
        "public_key": public,
        "seq": fields.get("seq"),
        "subject": fields.get("subject") or fields.get("subject_handle") or "",
        "v": FED_SPEC,
    }
    prepared = prepare_statement(statement, check_signature=False)
    signed = _sign(seed, prepared)
    return prepare_statement(signed)


def sign_isolation(seed: bytes, **fields: Any) -> dict[str, Any]:
    """The handle signs its own isolation. Evidence is a hash, never the bytes."""
    _refuse_material(fields)
    handle, public, _raw = _identity(seed)
    statement = {
        "check": fields.get("check") or "",
        "evidence_hash": fields.get("evidence_hash") or "",
        "handle": handle,
        "kind": KIND_ISOLATION,
        "model": fields.get("model") or "absent",
        "prev": fields.get("prev") or GENESIS_PREV,
        "public_key": public,
        "reason": fields.get("reason") or "",
        "seq": fields.get("seq"),
        "subject": fields.get("subject") or handle,
        "v": FED_SPEC,
    }
    prepared = prepare_statement(statement, check_signature=False)
    signed = _sign(seed, prepared)
    return prepare_statement(signed)


def sign_appeal(seed: bytes, **fields: Any) -> dict[str, Any]:
    """Ask for a re-check. This does not clear isolation."""
    _refuse_material(fields)
    handle, public, _raw = _identity(seed)
    statement = {
        "handle": handle,
        "isolation_hash": fields.get("isolation_hash") or "",
        "kind": KIND_APPEAL,
        "note": fields.get("note") or "",
        "prev": fields.get("prev") or GENESIS_PREV,
        "public_key": public,
        "seq": fields.get("seq"),
        "v": FED_SPEC,
    }
    prepared = prepare_statement(statement, check_signature=False)
    signed = _sign(seed, prepared)
    return prepare_statement(signed)


def prepare_statement(data: Mapping[str, Any], *, check_signature: bool = True) -> dict[str, Any]:
    """Validate a statement. The signature is checked when requested.

    A friendly claim's proof-of-work is checked by the ledger, because the
    published FED-MESH name vector has no nonce. A nonce that is present
    must already meet the minimum.
    """
    if not isinstance(data, Mapping):
        raise NameRefuse(MALFORMED, "statement must be an object")
    _refuse_material(data)
    allowed = {
        "v",
        "kind",
        "handle",
        "public_key",
        "seq",
        "prev",
        "sig",
        "pow",
        "record_hash",
        "name",
        "owner",
        "target",
        "expires",
        "prev_record",
        "subject_hash",
        "subject_kind",
        "subject",
        "subject_public_key",
        "note",
        "model",
        "reason",
        "check",
        "evidence_hash",
        "isolation_hash",
    }
    unknown = set(data) - allowed
    if unknown:
        raise NameRefuse(MALFORMED, "unknown statement fields")
    kind = str(data.get("kind") or "")
    if data.get("v") != FED_SPEC:
        raise NameRefuse(MALFORMED, f"v must be {FED_SPEC}")
    handle = str(data.get("handle") or "")
    public_b64 = str(data.get("public_key") or "")
    if not is_handle(handle):
        raise NameRefuse(MALFORMED, "handle must be # plus 11 Crockford characters")
    raw_key = b64url_decode(public_b64)
    if raw_key is None or len(raw_key) != 32:
        raise NameRefuse(BAD_SIGNATURE, "public_key must be 32-byte base64url")
    if handle_from_public(raw_key) != handle:
        raise NameRefuse(NOT_OWNER, "public_key does not match the handle")
    seq = data.get("seq")
    if isinstance(seq, bool) or not isinstance(seq, int) or seq < 1:
        raise NameRefuse(MALFORMED, "seq must be an integer ≥ 1")
    prev = str(data.get("prev") or "")
    if not is_hash(prev):
        raise NameRefuse(MALFORMED, "prev must be 64-char hex")

    if kind == KIND_NAME:
        body = _name_body(data, handle, public_b64, seq, prev)
    elif kind == KIND_WITNESS:
        body = _witness_body(data, handle, public_b64, seq, prev)
    elif kind == KIND_VOUCH:
        body = _vouch_body(data, handle, public_b64, seq, prev)
    elif kind == KIND_ADVISORY:
        body = _advisory_body(data, handle, public_b64, seq, prev)
    elif kind == KIND_ISOLATION:
        body = _isolation_body(data, handle, public_b64, seq, prev)
    elif kind == KIND_APPEAL:
        body = _appeal_body(data, handle, public_b64, seq, prev)
    else:
        raise NameRefuse(MALFORMED, "kind is not a name security statement")

    digest = statement_hash(body)
    if "pow" in data:
        if kind != KIND_NAME:
            raise NameRefuse(MALFORMED, "pow is only present on a friendly name claim")
        _check_pow(data.get("pow"), digest, str(data.get("sig") or ""), False)
    if not check_signature:
        return body
    signature = b64url_decode(str(data.get("sig") or ""))
    if signature is None or len(signature) != 64:
        raise NameRefuse(BAD_SIGNATURE, "sig must be 64-byte base64url")
    if data.get("record_hash") not in (None, "", digest):
        raise NameRefuse(BAD_SIGNATURE, "record_hash is not the statement hash")
    if not verify(raw_key, canonicalize(body).encode("utf-8"), signature):
        raise NameRefuse(BAD_SIGNATURE, "signature did not verify")
    out = dict(body)
    out["sig"] = b64url(signature)
    if "pow" in data:
        _check_pow(data.get("pow"), digest, out["sig"], True)
        out["pow"] = {
            "bits": int(data["pow"]["bits"]),
            "digest": pow_digest(digest, out["sig"], str(data["pow"]["nonce"])),
            "nonce": str(data["pow"]["nonce"]),
        }
    out["record_hash"] = digest
    return out


def _check_pow(stamp: Any, digest: str, sig: str, require_sig: bool) -> None:
    if not isinstance(stamp, Mapping):
        raise NameRefuse(POW_FAIL, "pow is { nonce, bits, digest }")
    extra = set(stamp) - {"nonce", "bits", "digest"}
    if extra:
        raise NameRefuse(MALFORMED, "pow fields are nonce, bits, and digest")
    nonce = str(stamp.get("nonce") or "")
    bits = stamp.get("bits")
    if not is_nonce(nonce):
        raise NameRefuse(POW_FAIL, "pow.nonce must be 1 to 64 lowercase hex characters")
    if isinstance(bits, bool) or not isinstance(bits, int) or bits < POW_BITS_MIN or bits > 256:
        raise NameRefuse(POW_WEAK, f"pow.bits must be at least {POW_BITS_MIN}")
    if not require_sig:
        return
    got = pow_digest(digest, sig, nonce)
    if stamp.get("digest") not in (None, "", got):
        raise NameRefuse(POW_FAIL, "pow.digest does not match the stamp")
    if leading_zero_bits(got) < bits:
        raise NameRefuse(POW_FAIL, "proof-of-work does not meet pow.bits")


def _name_body(data: Mapping[str, Any], handle: str, public_b64: str, seq: int, prev: str) -> dict[str, Any]:
    name, name_kind = _canonical_name(str(data.get("name") or ""))
    if str(data.get("name") or "") != name:
        raise NameRefuse(MALFORMED, f"sign the canonical name {name}")
    if name_kind == "self_cert":
        owner_handle = "#" + name.split(".", 1)[0].upper()
        if handle != owner_handle:
            raise NameRefuse(NOT_OWNER, "a self-certifying name follows the handle inside it")
    owner_raw = data.get("owner")
    owner = "" if owner_raw in (None, "") else str(owner_raw)
    if owner and not is_handle(owner):
        raise NameRefuse(MALFORMED, "owner is a #handle, or empty on release")
    prev_record = str(data.get("prev_record") or "")
    if not is_hash(prev_record):
        raise NameRefuse(MALFORMED, "prev_record must be 64-char hex")
    if "expires" not in data:
        raise NameRefuse(MALFORMED, "expires is null, or a unix time in milliseconds")
    expires = data.get("expires")
    if expires is not None and (isinstance(expires, bool) or not isinstance(expires, int) or expires < 0):
        raise NameRefuse(MALFORMED, "expires is null, or a unix time in milliseconds")
    target = _normalize_target(data.get("target"), owner, name_kind, handle)
    if name_kind == "self_cert" and (owner != handle or target is None):
        raise NameRefuse(SELF_CERT_FIXED, "a self-certifying name is not transferred or released")
    return {
        "expires": expires,
        "handle": handle,
        "kind": KIND_NAME,
        "name": name,
        "owner": owner,
        "prev": prev,
        "prev_record": prev_record,
        "public_key": public_b64,
        "seq": seq,
        "target": target,
        "v": FED_SPEC,
    }


def _normalize_target(target: Any, owner: str, name_kind: str, handle: str) -> Any:
    if owner == "":
        if target is not None:
            raise NameRefuse(MALFORMED, "release sets target to null and owner to empty")
        return None
    if not isinstance(target, Mapping):
        raise NameRefuse(MALFORMED, "target is { type: hash|ref|handle, value }")
    extra = set(target) - {"type", "value"}
    if extra:
        raise NameRefuse(MALFORMED, "target fields are type and value")
    kind = _target_type(str(target.get("type") or ""))
    if kind == "none":
        raise NameRefuse(MALFORMED, "target is { type: hash|ref|handle, value }")
    value = _check_target_value(kind, str(target.get("value") or ""))
    if "://" in value:
        raise NameRefuse(MALFORMED, "targets are hashes, ref names, or handles, not URLs")
    if name_kind == "self_cert" and owner != handle:
        raise NameRefuse(SELF_CERT_FIXED, "a self-certifying name stays with its handle")
    return {"type": kind, "value": value}


def _witness_body(
    data: Mapping[str, Any],
    handle: str,
    public_b64: str,
    seq: int,
    prev: str,
) -> dict[str, Any]:
    subject_hash = str(data.get("subject_hash") or "")
    subject_kind = str(data.get("subject_kind") or "")
    if not is_hash(subject_hash) or subject_kind != "name":
        raise NameRefuse(MALFORMED, "a witness names subject_kind name and a 64-hex subject_hash")
    return {
        "handle": handle,
        "kind": KIND_WITNESS,
        "prev": prev,
        "public_key": public_b64,
        "seq": seq,
        "subject_hash": subject_hash,
        "subject_kind": "name",
        "v": FED_SPEC,
    }


def _vouch_body(
    data: Mapping[str, Any],
    handle: str,
    public_b64: str,
    seq: int,
    prev: str,
) -> dict[str, Any]:
    subject = str(data.get("subject") or "")
    subject_key = str(data.get("subject_public_key") or "")
    raw = b64url_decode(subject_key)
    if not is_handle(subject) or raw is None or len(raw) != 32:
        raise NameRefuse(MALFORMED, "a vouch names a subject handle and its public key")
    if handle_from_public(raw) != subject:
        raise NameRefuse(NOT_OWNER, "vouched public key does not match the subject handle")
    if subject == handle:
        raise NameRefuse(MALFORMED, "a handle does not vouch for itself")
    return {
        "handle": handle,
        "kind": KIND_VOUCH,
        "prev": prev,
        "public_key": public_b64,
        "seq": seq,
        "subject": subject,
        "subject_public_key": subject_key,
        "v": FED_SPEC,
    }


def _advisory_body(
    data: Mapping[str, Any],
    handle: str,
    public_b64: str,
    seq: int,
    prev: str,
) -> dict[str, Any]:
    subject = str(data.get("subject") or "")
    note = str(data.get("note") or "")
    if not is_handle(subject):
        raise NameRefuse(MALFORMED, "an advisory names a subject handle")
    if not note or len(note) > ADVISORY_NOTE_MAX:
        raise NameRefuse(MALFORMED, f"note is 1 to {ADVISORY_NOTE_MAX} characters")
    return {
        "handle": handle,
        "kind": KIND_ADVISORY,
        "note": note,
        "prev": prev,
        "public_key": public_b64,
        "seq": seq,
        "subject": subject,
        "v": FED_SPEC,
    }


_CHECK_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_MODEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$")


def _check_label(value: str) -> str:
    text = str(value or "")
    if not _CHECK_RE.match(text):
        raise NameRefuse(MALFORMED, "check names the local check, 1 to 64 characters [a-z0-9._-]")
    return text


def _model_label(value: str) -> str:
    text = str(value or "")
    if not _MODEL_RE.match(text):
        raise NameRefuse(MALFORMED, "model is a version string, or absent")
    return text


def _isolation_body(
    data: Mapping[str, Any],
    handle: str,
    public_b64: str,
    seq: int,
    prev: str,
) -> dict[str, Any]:
    subject = str(data.get("subject") or "")
    reason = str(data.get("reason") or "")
    evidence = str(data.get("evidence_hash") or "")
    if not is_handle(subject):
        raise NameRefuse(MALFORMED, "isolation names a subject handle")
    if subject != handle:
        raise NameRefuse(NOT_OWNER, "the isolated handle signs its own isolation record")
    if reason not in ISOLATION_REASONS:
        raise NameRefuse(MALFORMED, "reason is NUDITY, CHILD, HATE, or CSAM")
    if not is_hash(evidence):
        raise NameRefuse(MALFORMED, "evidence_hash is 64 hex characters and not the content")
    return {
        "check": _check_label(str(data.get("check") or "")),
        "evidence_hash": evidence,
        "handle": handle,
        "kind": KIND_ISOLATION,
        "model": _model_label(str(data.get("model") or "")),
        "prev": prev,
        "public_key": public_b64,
        "reason": reason,
        "seq": seq,
        "subject": subject,
        "v": FED_SPEC,
    }


def _appeal_body(
    data: Mapping[str, Any],
    handle: str,
    public_b64: str,
    seq: int,
    prev: str,
) -> dict[str, Any]:
    isolation_hash = str(data.get("isolation_hash") or "")
    note = str(data.get("note") or "")
    if not is_hash(isolation_hash):
        raise NameRefuse(MALFORMED, "an appeal names the isolation statement hash")
    if not note or len(note) > ADVISORY_NOTE_MAX:
        raise NameRefuse(MALFORMED, f"note is 1 to {ADVISORY_NOTE_MAX} characters")
    return {
        "handle": handle,
        "isolation_hash": isolation_hash,
        "kind": KIND_APPEAL,
        "note": note,
        "prev": prev,
        "public_key": public_b64,
        "seq": seq,
        "v": FED_SPEC,
    }
