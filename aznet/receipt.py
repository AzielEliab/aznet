"""AZNet receipt. Hashes only. Author: Aziel Eliab only."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping

from aznet.canon import (
    ABSENT,
    ACTOR_OPERATOR,
    EVENT_KINDS,
    FORBIDDEN_KEYS,
    GENESIS_PREV_HASH,
    HASH_FIELDS,
    MARKER,
    MEMORIAL_REASONS,
    NOTE_MAX,
    PAIR_STATES,
    SPEC,
    UNLOCK_STATES,
    digest,
)
from aznet.errors import InvariantError, ReceiptError

_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_HASH = re.compile(r"^[0-9a-f]{64}$")


def assert_no_leakage(data: Mapping[str, Any] | None) -> None:
    """Refuse payloads, keys, user content, and exploit details."""
    src = data or {}
    for key in FORBIDDEN_KEYS:
        if key in src:
            raise InvariantError(f"I1: forbidden key {key} — hashes only, never payloads/keys/user content")
    for key in ("payload", "keys", "user_content"):
        val = src.get(key)
        if val not in (None, "", ABSENT):
            raise InvariantError(f"I1: {key} must be ABSENT")
    if src.get("actor") not in (None, "", ACTOR_OPERATOR):
        raise InvariantError("actor must be operator")
    summary = str(src.get("summary") or "")
    lowered = summary.lower()
    for token in ("exploit", "poc", "payload", "cve", "0day", "shellcode"):
        if token in lowered:
            raise InvariantError("I8: memorial summary is non-actionable — no exploit details")


def validate_note(note: str | None) -> str:
    text = "" if note is None else str(note)
    if len(text) > NOTE_MAX:
        raise InvariantError(f"note must be ≤{NOTE_MAX} characters")
    lowered = text.lower()
    for token in ("poc", "payload bytes", "private key", "shellcode"):
        if token in lowered:
            raise InvariantError("note must not carry payloads, keys, or attack details")
    return text


def require_hash(name: str, value: str | None, *, allow_empty: bool = False) -> str | None:
    if value in (None, ""):
        if allow_empty:
            return None
        raise ReceiptError(f"{name} must be a 64-char lowercase hex SHA-256")
    text = str(value).lower()
    if not _HASH.match(text):
        raise ReceiptError(f"{name} must be a 64-char lowercase hex SHA-256")
    return text


def require_iso(name: str, value: str | None, *, allow_empty: bool = False) -> str | None:
    if value in (None, ""):
        if allow_empty:
            return None
        raise ReceiptError(f"{name} must be UTC ISO-8601 with trailing Z (second precision)")
    if not _ISO.match(str(value)):
        raise ReceiptError(f"{name} must be UTC ISO-8601 with trailing Z (second precision)")
    return str(value)


@dataclass(frozen=True)
class Receipt:
    event_kind: str
    prev_hash: str
    receipt_hash: str
    timestamp: str
    date_stamp: str
    actor: str = ACTOR_OPERATOR
    spec: str = SPEC
    marker: str = MARKER
    payload: str = ABSENT
    keys: str = ABSENT
    user_content: str = ABSENT
    hash_hex: str | None = None
    label: str | None = None
    genesis_hash: str | None = None
    final_hash: str | None = None
    reason: str | None = None
    summary: str | None = None
    pair_status: str | None = None
    unlock_status: str | None = None
    azbrowser: str | None = None
    aznet_node: str | None = None
    fraggate: str | None = None
    staticclock: str | None = None
    zone: str | None = None
    witness_hash: str | None = None
    note: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {key: None for key in HASH_FIELDS}
        payload.update(
            {
                "actor": self.actor,
                "azbrowser": self.azbrowser,
                "aznet_node": self.aznet_node,
                "date_stamp": self.date_stamp,
                "event_kind": self.event_kind,
                "final_hash": self.final_hash,
                "fraggate": self.fraggate,
                "genesis_hash": self.genesis_hash,
                "hash_hex": self.hash_hex,
                "keys": ABSENT,
                "label": self.label,
                "marker": MARKER,
                "note": self.note,
                "pair_status": self.pair_status,
                "payload": ABSENT,
                "prev_hash": self.prev_hash,
                "reason": self.reason,
                "spec": SPEC,
                "staticclock": self.staticclock,
                "summary": self.summary,
                "timestamp": self.timestamp,
                "unlock_status": self.unlock_status,
                "user_content": ABSENT,
                "witness_hash": self.witness_hash,
                "zone": self.zone,
            }
        )
        payload["receipt_hash"] = self.receipt_hash
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Receipt:
        assert_no_leakage(data)
        kind = str(data.get("event_kind") or "")
        if kind not in EVENT_KINDS:
            raise ReceiptError(f"event_kind must be one of {','.join(EVENT_KINDS)}")
        rec = cls(
            event_kind=kind,
            prev_hash=str(data.get("prev_hash") or GENESIS_PREV_HASH),
            receipt_hash=str(data.get("receipt_hash") or ""),
            timestamp=str(data.get("timestamp") or ""),
            date_stamp=str(data.get("date_stamp") or ""),
            actor=ACTOR_OPERATOR,
            hash_hex=data.get("hash_hex"),
            label=data.get("label"),
            genesis_hash=data.get("genesis_hash"),
            final_hash=data.get("final_hash"),
            reason=data.get("reason"),
            summary=data.get("summary"),
            pair_status=data.get("pair_status"),
            unlock_status=data.get("unlock_status"),
            azbrowser=data.get("azbrowser"),
            aznet_node=data.get("aznet_node"),
            fraggate=data.get("fraggate"),
            staticclock=data.get("staticclock"),
            zone=data.get("zone"),
            witness_hash=data.get("witness_hash"),
            note=validate_note(data.get("note")),
        )
        return rec

    @classmethod
    def create(cls, **fields: Any) -> Receipt:
        assert_no_leakage(fields)
        kind = fields.get("event_kind")
        if kind not in EVENT_KINDS:
            raise ReceiptError(f"event_kind must be one of {','.join(EVENT_KINDS)}")
        ts = require_iso("timestamp", fields.get("timestamp"))
        assert ts is not None
        date_stamp = fields.get("date_stamp") or ts[:10]
        prev = fields.get("prev_hash") or GENESIS_PREV_HASH
        if not _HASH.match(str(prev)):
            raise ReceiptError("prev_hash must be a 64-char lowercase hex SHA-256")
        pair_status = fields.get("pair_status")
        if pair_status not in (None, "") and pair_status not in PAIR_STATES:
            raise ReceiptError(f"pair_status must be one of {','.join(PAIR_STATES)}")
        unlock_status = fields.get("unlock_status")
        if unlock_status not in (None, "") and unlock_status not in UNLOCK_STATES:
            raise ReceiptError(f"unlock_status must be one of {','.join(UNLOCK_STATES)}")
        reason = fields.get("reason")
        if kind == "MEMORIAL":
            if reason not in MEMORIAL_REASONS:
                raise ReceiptError(f"memorial reason must be one of {','.join(MEMORIAL_REASONS)}")
            require_hash("genesis_hash", fields.get("genesis_hash"))
            require_hash("final_hash", fields.get("final_hash"))
        if kind in {"GARDEN", "STAMP", "VERIFY"} or fields.get("hash_hex"):
            if fields.get("hash_hex"):
                require_hash("hash_hex", fields.get("hash_hex"))
        payload = {
            "event_kind": kind,
            "prev_hash": prev,
            "timestamp": ts,
            "date_stamp": date_stamp,
            "actor": ACTOR_OPERATOR,
            "spec": SPEC,
            "marker": MARKER,
            "payload": ABSENT,
            "keys": ABSENT,
            "user_content": ABSENT,
            "hash_hex": fields.get("hash_hex"),
            "label": fields.get("label"),
            "genesis_hash": fields.get("genesis_hash"),
            "final_hash": fields.get("final_hash"),
            "reason": reason,
            "summary": fields.get("summary"),
            "pair_status": pair_status,
            "unlock_status": unlock_status,
            "azbrowser": fields.get("azbrowser"),
            "aznet_node": fields.get("aznet_node"),
            "fraggate": fields.get("fraggate"),
            "staticclock": fields.get("staticclock"),
            "zone": fields.get("zone") or "UTC",
            "witness_hash": fields.get("witness_hash"),
            "note": validate_note(fields.get("note")),
        }
        rec = cls(
            event_kind=kind,
            prev_hash=prev,
            receipt_hash=digest(payload),
            timestamp=ts,
            date_stamp=date_stamp,
            hash_hex=payload["hash_hex"],
            label=payload["label"],
            genesis_hash=payload["genesis_hash"],
            final_hash=payload["final_hash"],
            reason=payload["reason"],
            summary=payload["summary"],
            pair_status=payload["pair_status"],
            unlock_status=payload["unlock_status"],
            azbrowser=payload["azbrowser"],
            aznet_node=payload["aznet_node"],
            fraggate=payload["fraggate"],
            staticclock=payload["staticclock"],
            zone=payload["zone"],
            witness_hash=payload["witness_hash"],
            note=payload["note"],
        )
        return rec
