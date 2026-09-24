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
    EQUIVOCATION,
    EXPIRED,
    FINAL,
    FORK,
    MALFORMED,
    MESH_TLD,
    NOT_MESH,
    OK,
    PENDING,
    REVOKED,
    SELF_CERT,
    SYNC_SPEC,
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
    finality: str | None = None
    witnesses: int = 0
    advisories: tuple[dict[str, Any], ...] = ()
    key_checked: bool = False

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
            "finality": self.finality,
            "witnesses": self.witnesses,
            "advisories": list(self.advisories),
            "key_checked": self.key_checked,
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
    fields.setdefault("finality", None)
    fields.setdefault("witnesses", 0)
    fields.setdefault("advisories", ())
    fields.setdefault("key_checked", False)
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
            "spec": SYNC_SPEC,
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


def resolve(
    source: NameLedger | Mapping[str, Any] | list[Any] | Path | str | None,
    query: str,
    *,
    now: str | None = None,
) -> ResolveResult:
    """Resolve ``query`` from the local ledger copy.

    ``now`` is a UTC timestamp supplied by the caller. Friendly claims stay
    PENDING until this ledger has held the establishing claim for 72 hours
    and at least three other handles have witnessed it. ``.az`` names that
    are not on the allowlist return ``DNS_FALLTHROUGH``. This function does
    not open a socket and does not serve a PENDING or equivocating target
    as a success.
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
    if classified.name and not classified.name.endswith("." + MESH_TLD):
        return _finish(
            ok=False,
            code=UNCLAIMED,
            query=classified.query,
            name=classified.name,
            dns="cite",
            detail=(
                f"{UNCLAIMED}: {classified.query} is a cite of a hub HTTPS site, not a FED-MESH name record"
            ),
        )

    ledger = source if isinstance(source, NameLedger) else _as_ledger(source)
    assert classified.name is not None
    if classified.kind == "self_cert" and not any(
        rec.get("name") == classified.name for rec in ledger.records
    ):
        return _finish(
            ok=True,
            code=SELF_CERT,
            query=classified.query,
            name=classified.name,
            owner=classified.owner_handle,
            target_kind="handle",
            target=classified.owner_handle,
            expiry_checked=now is not None,
            finality=FINAL,
            key_checked=False,
            detail=f"{SELF_CERT}: handle owns this name with no claim record",
        )

    decision = ledger.resolve_name(classified.name, now)
    advisories = tuple(ledger.matching_advisories(classified.name, decision.get("owner")))
    if decision["code"] == "ABSENT":
        return _finish(
            ok=False,
            code=UNCLAIMED,
            query=classified.query,
            name=classified.name,
            false_site=classified.false_site,
            expiry_checked=now is not None,
            advisories=advisories,
            detail=f"{UNCLAIMED}: no anchored claim",
        )
    code = str(decision["code"])
    served = code == OK
    detail = {
        OK: f"{OK}: earliest FINAL name record",
        PENDING: f"{PENDING}: claim is anchored and is not FINAL yet",
        FORK: f"{FORK}: two claims share an anchor time and were not merged",
        EQUIVOCATION: f"{EQUIVOCATION}: the handle signed two statements at one seq",
        EXPIRED: f"{EXPIRED}: expires is not after now",
        REVOKED: f"{REVOKED}: owner released the name",
    }.get(code, code)
    return _finish(
        ok=served,
        code=code,
        query=classified.query,
        name=classified.name,
        owner=decision.get("owner"),
        target_kind=decision.get("target_kind"),
        target=decision.get("target"),
        record_hash=decision.get("record_hash"),
        sequence=decision.get("seq"),
        timeslate=decision.get("anchored_at") or None,
        expiry_checked=now is not None,
        false_site=classified.false_site,
        finality=decision.get("finality"),
        witnesses=int(decision.get("witnesses") or 0),
        advisories=advisories,
        key_checked=bool(decision.get("key_checked")),
        detail=detail,
    )
