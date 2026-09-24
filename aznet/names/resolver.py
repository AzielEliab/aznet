"""Resolve a mesh name from a local ledger copy.

Lamb Lens order for a lookup: Service (return the verified target),
Clarity (the code names the failure), Peace (a fork is refused, not merged).

Author: Aziel Eliab only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from aznet.names.ledger import NameLedger
from aznet.names.namespace import classify
from aznet.names.wire import (
    DNS_FALLTHROUGH,
    EXPIRED,
    FORK,
    MALFORMED,
    NOT_MESH,
    OK,
    REVOKED,
    SELF_CERT,
    UNCLAIMED,
    is_timeslate,
)


@dataclass(frozen=True)
class ResolveResult:
    ok: bool
    code: str
    query: str
    name: str | None
    owner: str | None
    target_kind: str | None
    target: str | None
    record_hash: str | None
    sequence: int | None
    timeslate: str | None
    expiry_checked: bool
    resolves_to_hub: bool
    false_site: bool
    dns: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "query": self.query,
            "name": self.name,
            "owner": self.owner,
            "target_kind": self.target_kind,
            "target": self.target,
            "record_hash": self.record_hash,
            "sequence": self.sequence,
            "timeslate": self.timeslate,
            "expiry_checked": self.expiry_checked,
            "resolves_to_hub": self.resolves_to_hub,
            "false_site": self.false_site,
            "dns": self.dns,
            "detail": self.detail,
            "hosts_payloads": False,
            "icann_registration": False,
        }


def _finish(**fields: Any) -> ResolveResult:
    fields.setdefault("name", None)
    fields.setdefault("owner", None)
    fields.setdefault("target_kind", None)
    fields.setdefault("target", None)
    fields.setdefault("record_hash", None)
    fields.setdefault("sequence", None)
    fields.setdefault("timeslate", None)
    fields.setdefault("expiry_checked", False)
    fields.setdefault("resolves_to_hub", False)
    fields.setdefault("false_site", False)
    fields.setdefault("dns", "not_applicable")
    return ResolveResult(**fields)


def _as_ledger(source: NameLedger | Mapping[str, Any] | list[Any] | Path | str | None) -> NameLedger:
    if isinstance(source, NameLedger):
        return source
    if source is None:
        return NameLedger()
    if isinstance(source, Path):
        return NameLedger.load(source)
    if isinstance(source, str):
        return NameLedger.load(source)
    ledger = NameLedger()
    if isinstance(source, list):
        envelope = {
            "spec": "AZN-NAME-SYNC-1.0",
            "payload": "ABSENT",
            "keys": "ABSENT",
            "user_content": "ABSENT",
            "records": source,
        }
        ledger.ingest(envelope)
        return ledger
    if isinstance(source, Mapping) and "records" in source:
        ledger.ingest(source)
        return ledger
    raise TypeError("resolve source must be a NameLedger, path, record list, or sync envelope")


def _tip(ledger: NameLedger, name: str) -> dict[str, Any] | None:
    found = None
    for rec in ledger.records:
        if rec["name"] == name:
            found = rec
    return found


def _expired(rec: Mapping[str, Any], now: str | None) -> bool:
    if not now or not rec.get("expires_at"):
        return False
    return str(rec["expires_at"]) <= now


def resolve(
    source: NameLedger | Mapping[str, Any] | list[Any] | Path | str | None,
    query: str,
    *,
    now: str | None = None,
) -> ResolveResult:
    """Resolve ``query`` from the local ledger copy.

    ``now`` is a TemporalLock timeslate supplied by the caller. When it is
    omitted, expiry is not evaluated and ``expiry_checked`` is false.
    ``.az`` names that are not on the allowlist return ``DNS_FALLTHROUGH``
    and no mesh target. This function does not open a socket.
    """
    if now is not None and not is_timeslate(now):
        return _finish(
            ok=False,
            code=MALFORMED,
            query=str(query or ""),
            detail=f"{MALFORMED}: now must be YYYY-MM-DDTHH:MM:SSZ",
        )
    classified = classify(query)
    if classified.kind == "malformed":
        return _finish(ok=False, code=MALFORMED, query=classified.query, detail=f"{MALFORMED}: name is not a mesh name")
    if classified.kind == "dns_fallthrough":
        return _finish(
            ok=False,
            code=DNS_FALLTHROUGH,
            query=classified.query,
            dns="fallthrough",
            detail=(
                f"{DNS_FALLTHROUGH}: .az is Azerbaijan's ccTLD; this name is not on the Cap-7 allowlist "
                "and falls through to normal DNS"
            ),
        )
    if classified.kind == "not_mesh":
        return _finish(
            ok=False,
            code=NOT_MESH,
            query=classified.query,
            dns="not_mesh",
            detail=f"{NOT_MESH}: not an .aziel name and not an allowlisted .az name",
        )

    ledger = source if isinstance(source, NameLedger) else _as_ledger(source)
    assert classified.name is not None
    if ledger.is_frozen(classified.name):
        return _finish(
            ok=False,
            code=FORK,
            query=classified.query,
            name=classified.name,
            false_site=classified.false_site,
            expiry_checked=now is not None,
            detail=f"{FORK}: conflicting records share a history and were not merged",
        )

    tip = _tip(ledger, classified.name)
    if classified.kind == "self_cert" and tip is None:
        return _finish(
            ok=True,
            code=SELF_CERT,
            query=classified.query,
            name=classified.name,
            owner=classified.owner_handle,
            target_kind="node",
            target=classified.owner_handle,
            expiry_checked=now is not None,
            detail=f"{SELF_CERT}: handle owns this name with no claim record",
        )
    if tip is None:
        return _finish(
            ok=False,
            code=UNCLAIMED,
            query=classified.query,
            name=classified.name,
            false_site=classified.false_site,
            expiry_checked=now is not None,
            detail=f"{UNCLAIMED}: no anchored claim",
        )
    if tip["op"] == "release":
        return _finish(
            ok=False,
            code=REVOKED,
            query=classified.query,
            name=classified.name,
            owner=None,
            record_hash=tip["record_hash"],
            sequence=tip["sequence"],
            timeslate=tip["timeslate"],
            false_site=classified.false_site,
            expiry_checked=now is not None,
            detail=f"{REVOKED}: owner released the name",
        )
    owner = tip["successor"] if tip["op"] == "transfer" else tip["owner"]
    if _expired(tip, now):
        return _finish(
            ok=False,
            code=EXPIRED,
            query=classified.query,
            name=classified.name,
            owner=owner,
            target_kind=tip["target_kind"],
            target=tip["target"],
            record_hash=tip["record_hash"],
            sequence=tip["sequence"],
            timeslate=tip["timeslate"],
            expiry_checked=True,
            false_site=classified.false_site,
            detail=f"{EXPIRED}: expires_at {tip['expires_at']} is not after now",
        )
    return _finish(
        ok=True,
        code=OK,
        query=classified.query,
        name=classified.name,
        owner=owner,
        target_kind=tip["target_kind"],
        target=tip["target"],
        record_hash=tip["record_hash"],
        sequence=tip["sequence"],
        timeslate=tip["timeslate"],
        expiry_checked=now is not None,
        false_site=classified.false_site,
        detail=f"{OK}: anchored name record",
    )
