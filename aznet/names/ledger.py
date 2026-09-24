"""Local name ledger with proof-of-work, witnesses, equivocation, and advisories.

Append-only. No socket. No peer code is executed. Competing friendly claims
are both kept. Resolution, not ingest, picks the earliest FINAL claim.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from aznet.errors import NameRefuse
from aznet.names.namespace import classify
from aznet.names.record import pow_meets, prepare_statement, timeslate_ms
from aznet.names.wire import (
    ABSENT,
    ANCHOR_SPEC,
    BAD_CHAIN,
    BAD_SEQUENCE,
    CAP_PER_HANDLE,
    EQUIVOCATION,
    EXPIRED,
    FINAL,
    FORK,
    GENESIS_PREV,
    IDEMPOTENT,
    KIND_ADVISORY,
    KIND_NAME,
    KIND_VOUCH,
    KIND_WITNESS,
    LEAK,
    LEAK_KEYS,
    MALFORMED,
    NOT_OWNER,
    OK,
    OVER_CAP,
    PENDING,
    POW_FAIL,
    REVOKED,
    ROLLBACK,
    SELF_CERT_FIXED,
    SYNC_SPEC,
    WAIT,
    WITNESS_AGE_SECONDS,
    WITNESS_K,
    anchor_hash,
    is_handle,
    is_hash,
    is_timeslate,
)

DEFAULT_NAMES = "aznet_names.jsonl"


def default_names_path() -> Path:
    env = os.environ.get("AZNET_NAMES")
    if env:
        return Path(env)
    return Path.cwd() / DEFAULT_NAMES


def _parse_time(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


@dataclass(frozen=True)
class AdoptResult:
    ok: bool
    code: str
    record_hash: str | None
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "code": self.code, "record_hash": self.record_hash, "detail": self.detail}


def _result(ok: bool, code: str, record_hash: str | None, detail: str) -> AdoptResult:
    return AdoptResult(ok, code, record_hash, detail)


class NameLedger:
    """Append-only cache of name security statements. Hashes and handles only."""

    def __init__(self, *, path: Path | None = None) -> None:
        self._path = path
        self._records: list[dict[str, Any]] = []
        self._by_hash: dict[str, dict[str, Any]] = {}
        self._anchored_at: dict[str, str] = {}
        self._equiv: set[str] = set()
        self._equiv_proofs: list[dict[str, Any]] = []
        self._subs: set[str] = set()
        self._tip = GENESIS_PREV
        self._batch: list[dict[str, Any]] = []

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._records)

    def is_equivocating(self, handle: str) -> bool:
        return handle in self._equiv

    def anchored_at(self, record_hash: str) -> str:
        return self._anchored_at.get(record_hash, "")

    def subscriptions(self) -> tuple[str, ...]:
        return tuple(sorted(self._subs))

    @classmethod
    def load(cls, path: Path | str | None = None) -> NameLedger:
        target = Path(path) if path is not None else default_names_path()
        ledger = cls(path=target)
        if not target.is_file():
            return ledger
        for line in target.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            ledger._replay(json.loads(line))
        return ledger

    def _replay(self, row: Mapping[str, Any]) -> None:
        kind = row.get("kind")
        if row.get("spec") != ANCHOR_SPEC or kind not in {"record", "equivocation", "subscribe"}:
            raise NameRefuse(MALFORMED, "name ledger line is not an anchor")
        if row.get("prev_hash") != self._tip:
            raise NameRefuse(BAD_CHAIN, "anchor prev_hash does not match the local tip")
        if row.get("anchor_hash") != anchor_hash(row) or not is_hash(str(row.get("anchor_hash"))):
            raise NameRefuse(BAD_CHAIN, "anchor_hash does not match")
        if kind == "subscribe":
            self._subs.add(str(row.get("name") or ""))
            self._tip = str(row["anchor_hash"])
            return
        record = row.get("record")
        if not isinstance(record, Mapping):
            raise NameRefuse(MALFORMED, "anchor record missing")
        prepared = prepare_statement(record)
        if prepared["record_hash"] != row.get("record_hash"):
            raise NameRefuse(BAD_CHAIN, "anchored record_hash mismatch")
        self._anchored_at[prepared["record_hash"]] = str(row.get("anchored_at") or "")
        if kind == "equivocation":
            self._equiv.add(prepared["handle"])
            self._equiv_proofs.append(prepared)
        else:
            self._records.append(prepared)
            self._by_hash[prepared["record_hash"]] = prepared
        self._tip = str(row["anchor_hash"])

    def verify(self) -> dict[str, Any]:
        errors: list[str] = []
        if self._path is None or not self._path.is_file():
            return {"ok": True, "length": len(self._records), "errors": errors, "equivocating": sorted(self._equiv)}
        tip = GENESIS_PREV
        seen = 0
        for index, line in enumerate(self._path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("prev_hash") != tip:
                errors.append(f"line {index}: prev_hash break")
            if row.get("anchor_hash") != anchor_hash(row):
                errors.append(f"line {index}: anchor_hash break")
            if row.get("kind") in {"record", "equivocation"}:
                try:
                    prepare_statement(row["record"])
                except NameRefuse as exc:
                    errors.append(f"line {index}: {exc}")
                seen += 1
            tip = str(row.get("anchor_hash") or "")
        return {"ok": not errors, "length": seen, "errors": errors, "equivocating": sorted(self._equiv)}

    def export_sync(self) -> dict[str, Any]:
        """Peer envelope. Statements only. Local subscriptions and anchor times stay here."""
        seen: set[str] = set()
        records: list[dict[str, Any]] = []
        for rec in list(self._records) + list(self._equiv_proofs):
            if rec["record_hash"] in seen:
                continue
            seen.add(rec["record_hash"])
            records.append(dict(rec))
        return {
            "spec": SYNC_SPEC,
            "payload": ABSENT,
            "keys": ABSENT,
            "user_content": ABSENT,
            "records": records,
        }

    def subscribe(self, handle: str) -> None:
        """Local choice. Not a mesh act and not included in sync."""
        if not is_handle(handle):
            raise NameRefuse(MALFORMED, "subscribe needs a handle")
        if handle in self._subs:
            return
        self._subs.add(handle)
        digest = hashlib.sha256(handle.encode("utf-8")).hexdigest()
        self._append("subscribe", handle, digest, "", None, prior_hash="", anchored_at="")

    def accept(self, record: Mapping[str, Any], *, now: str | None = None) -> AdoptResult:
        report = self.ingest(
            {
                "spec": SYNC_SPEC,
                "payload": ABSENT,
                "keys": ABSENT,
                "user_content": ABSENT,
                "records": [dict(record)],
            },
            now=now,
        )
        row = report["results"][0]
        return AdoptResult(bool(row["ok"]), str(row["code"]), row["record_hash"], str(row["detail"]))

    def ingest(self, envelope: Mapping[str, Any], *, now: str | None = None) -> dict[str, Any]:
        if now is not None and not is_timeslate(now):
            raise NameRefuse(MALFORMED, "now must be YYYY-MM-DDTHH:MM:SSZ")
        self._refuse_envelope(envelope)
        raw_records = envelope.get("records")
        if not isinstance(raw_records, list):
            raise NameRefuse(MALFORMED, "sync records must be a list")
        results: list[AdoptResult | None] = [None] * len(raw_records)
        pending: list[tuple[int, dict[str, Any]]] = []
        for index, raw in enumerate(raw_records):
            try:
                if not isinstance(raw, Mapping):
                    raise NameRefuse(MALFORMED, "record must be an object")
                pending.append((index, prepare_statement(raw)))
            except NameRefuse as exc:
                results[index] = _result(False, exc.code, None, str(exc))
        while pending:
            self._batch = [rec for _index, rec in pending]
            rest: list[tuple[int, dict[str, Any]]] = []
            progressed = False
            for index, rec in list(pending):
                outcome = self._attempt(rec, now)
                if outcome.code == WAIT:
                    rest.append((index, rec))
                    continue
                results[index] = outcome
                progressed = True
                self._batch = [item for item in self._batch if item["record_hash"] != rec["record_hash"]]
            self._batch = []
            if not progressed:
                for index, rec in rest:
                    results[index] = _result(False, BAD_CHAIN, rec["record_hash"], f"{BAD_CHAIN}: prev is not anchored")
                break
            pending = rest
        return {
            "spec": SYNC_SPEC,
            "ok": all(item is not None and item.ok for item in results) if results else True,
            "results": [
                item.to_dict() if item is not None else _result(False, MALFORMED, None, MALFORMED).to_dict()
                for item in results
            ],
        }

    def claim_finality(self, record: Mapping[str, Any], now: str | None) -> str:
        """PENDING until this node has held the establishing claim long enough, with K witnesses."""
        if self.is_equivocating(str(record.get("handle") or "")):
            return EQUIVOCATION
        owner = str(record.get("owner") or "")
        if owner and self.is_equivocating(owner):
            return EQUIVOCATION
        root = self._establishing(record)
        if self.is_equivocating(str(root.get("handle") or "")):
            return EQUIVOCATION
        if classify(str(root.get("name") or "")).kind == "self_cert":
            return FINAL
        if root.get("kind") != KIND_NAME or not root.get("owner") or root.get("target") is None:
            return PENDING
        if now is None or not is_timeslate(now):
            return PENDING
        opened = self._anchored_at.get(str(root["record_hash"]), "")
        if not opened:
            return PENDING
        age = (_parse_time(now) - _parse_time(opened)).total_seconds()
        if age >= WITNESS_AGE_SECONDS and len(self.valid_witnesses(root, now)) >= WITNESS_K:
            return FINAL
        return PENDING

    def valid_witnesses(self, claim: Mapping[str, Any], now: str) -> list[dict[str, Any]]:
        found: dict[str, dict[str, Any]] = {}
        for rec in self._records:
            if rec.get("kind") != KIND_WITNESS:
                continue
            if rec.get("subject_hash") != claim["record_hash"]:
                continue
            if rec.get("subject_handle") != claim["handle"]:
                continue
            if rec["handle"] == claim["handle"] or self.is_equivocating(rec["handle"]):
                continue
            if rec["timeslate"] > now:
                continue
            found[rec["handle"]] = rec
        return list(found.values())

    def trust_view(self, handle: str) -> dict[str, Any]:
        """Local signals only. Not a ranking and not a score."""
        acts = [rec for rec in self._records if rec.get("handle") == handle]
        vouches = [
            {"by": rec["handle"], "timeslate": rec["timeslate"], "record_hash": rec["record_hash"]}
            for rec in self._records
            if rec.get("kind") == KIND_VOUCH and rec.get("subject_handle") == handle
        ]
        first = min((self._anchored_at.get(rec["record_hash"], "") or rec.get("timeslate", "") for rec in acts), default="")
        return {
            "handle": handle,
            "equivocating": self.is_equivocating(handle),
            "first_seen": first or None,
            "act_count": len(acts),
            "vouches": vouches,
            "vouches_change_finality": False,
            "note": "Local trust signals only. Not a ranking. Vouches do not make a claim FINAL.",
        }

    def matching_advisories(self, name: str | None, owner: str | None) -> list[dict[str, Any]]:
        """Entries from advisory lists this node has subscribed to. Others are ignored."""
        latest: dict[str, dict[str, Any]] = {}
        for rec in self._records:
            if rec.get("kind") != KIND_ADVISORY or rec["handle"] not in self._subs:
                continue
            current = latest.get(rec["handle"])
            if current is None or rec["seq"] >= current["seq"]:
                latest[rec["handle"]] = rec
        matches: list[dict[str, Any]] = []
        for rec in latest.values():
            for entry in rec["entries"]:
                if (name and entry["name"] == name) or (owner and entry["subject_handle"] == owner):
                    matches.append(
                        {
                            "list_id": rec["list_id"],
                            "by": rec["handle"],
                            "name": entry["name"],
                            "subject_handle": entry["subject_handle"],
                            "note": entry["note"],
                            "record_hash": rec["record_hash"],
                        }
                    )
        return matches

    def _refuse_envelope(self, envelope: Mapping[str, Any]) -> None:
        if not isinstance(envelope, Mapping):
            raise NameRefuse(MALFORMED, "sync envelope must be an object")
        if LEAK_KEYS.intersection(envelope):
            raise NameRefuse(LEAK, "sync envelopes do not carry keys or payloads")
        if envelope.get("spec") != SYNC_SPEC:
            raise NameRefuse(MALFORMED, f"sync spec must be {SYNC_SPEC}")
        for key in ("payload", "keys", "user_content"):
            if envelope.get(key) != ABSENT:
                raise NameRefuse(LEAK, f"sync {key} must be ABSENT")

    def _append(
        self,
        kind: str,
        name: str,
        record_hash_hex: str,
        timeslate: str,
        record: Mapping[str, Any] | None,
        *,
        prior_hash: str,
        anchored_at: str,
    ) -> None:
        row: dict[str, Any] = {
            "spec": ANCHOR_SPEC,
            "kind": kind,
            "prev_hash": self._tip,
            "record_hash": record_hash_hex,
            "prior_hash": prior_hash,
            "name": name,
            "timeslate": timeslate,
            "anchored_at": anchored_at,
        }
        row["anchor_hash"] = anchor_hash(row)
        if record is not None:
            row["record"] = dict(record)
        if self._path is not None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
        self._tip = row["anchor_hash"]

    def _flag(self, left: Mapping[str, Any], right: Mapping[str, Any], now: str | None) -> None:
        handle = str(left["handle"])
        self._equiv.add(handle)
        known = {rec["record_hash"] for rec in self._equiv_proofs}
        for rec in (left, right):
            if rec["record_hash"] in known or rec["record_hash"] in self._by_hash:
                continue
            known.add(rec["record_hash"])
            stored = dict(rec)
            self._equiv_proofs.append(stored)
            other = right["record_hash"] if rec["record_hash"] == left["record_hash"] else left["record_hash"]
            self._anchored_at[stored["record_hash"]] = now or ""
            self._append(
                "equivocation",
                handle,
                stored["record_hash"],
                str(stored.get("timeslate") or now or ""),
                stored,
                prior_hash=str(other),
                anchored_at=now or "",
            )

    def _handle_tip(self, handle: str) -> dict[str, Any] | None:
        found = None
        for rec in self._records:
            if rec.get("handle") == handle:
                found = rec
        return found

    def _establishing(self, record: Mapping[str, Any]) -> dict[str, Any]:
        current = dict(record)
        seen: set[str] = set()
        while current.get("prev_record") not in (None, GENESIS_PREV):
            parent_hash = str(current["prev_record"])
            if parent_hash in seen:
                break
            seen.add(str(current["record_hash"]))
            parent = self._by_hash.get(parent_hash)
            if parent is None or parent.get("name") != current.get("name"):
                break
            if parent.get("owner") == "" or parent.get("target") is None:
                break
            current = parent
        return current

    def _names(self) -> list[dict[str, Any]]:
        return [rec for rec in self._records if rec.get("kind") == KIND_NAME]

    def _children(self, name: str) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for rec in self._names():
            if rec["name"] == name:
                grouped.setdefault(str(rec["prev_record"]), []).append(rec)
        return grouped

    def _epoch_root(self, rec: Mapping[str, Any]) -> bool:
        if rec.get("prev_record") == GENESIS_PREV:
            return True
        parent = self._by_hash.get(str(rec.get("prev_record")))
        return bool(parent and parent.get("name") == rec.get("name") and (parent.get("owner") == "" or parent.get("target") is None))

    def _walk(self, name: str, root: Mapping[str, Any]) -> tuple[dict[str, Any], bool]:
        grouped = self._children(name)
        current = dict(root)
        seen: set[str] = set()
        while current["record_hash"] not in seen:
            seen.add(current["record_hash"])
            kids = list(grouped.get(current["record_hash"], []))
            if not kids:
                return current, False
            kids.sort(key=lambda item: (self._anchored_at.get(item["record_hash"], ""), item["record_hash"]))
            if len(kids) >= 2 and self._anchored_at.get(kids[0]["record_hash"], "") == self._anchored_at.get(kids[1]["record_hash"], ""):
                return kids[0], True
            current = kids[0]
        return current, True

    def _chains(self, name: str) -> list[dict[str, Any]]:
        chains = []
        for rec in self._names():
            if rec["name"] != name or not self._epoch_root(rec):
                continue
            tip, forked = self._walk(name, rec)
            chains.append({"root": rec, "tip": tip, "forked": forked})
        return chains

    def _live_owner(self, rec: Mapping[str, Any], now: str | None) -> str | None:
        owner = str(rec.get("owner") or "")
        if not owner or rec.get("target") is None:
            return None
        expires = rec.get("expires")
        if now and expires is not None and int(expires) <= timeslate_ms(now):
            return None
        return owner

    def _active_names(self, owner: str, now: str | None) -> set[str]:
        found: set[str] = set()
        names = {rec["name"] for rec in self._names() if classify(rec["name"]).kind != "self_cert"}
        for name in names:
            for chain in self._chains(name):
                tip = chain["tip"]
                root = chain["root"]
                if self.is_equivocating(str(root["handle"])) or self.is_equivocating(str(tip["handle"])):
                    continue
                if tip.get("owner") and self.is_equivocating(str(tip["owner"])):
                    continue
                holder = self._live_owner(root if chain["forked"] else tip, now)
                if holder == owner:
                    found.add(name)
        return found

    def _stamp(self, rec: Mapping[str, Any]) -> str:
        return self._anchored_at.get(str(rec["record_hash"]), "")

    def resolve_name(self, name: str, now: str | None) -> dict[str, Any]:
        """Pick the chain this node will serve. Callers still apply DNS classification."""
        chains = self._chains(name)
        if not chains:
            return {"code": "ABSENT"}
        ranked: list[tuple[str, dict[str, Any]]] = []
        for chain in chains:
            tip = chain["tip"]
            root = chain["root"]
            if chain["forked"]:
                status = FORK
            elif self.is_equivocating(str(root["handle"])) or self.is_equivocating(str(tip["handle"])):
                status = EQUIVOCATION
            elif tip.get("owner") and self.is_equivocating(str(tip["owner"])):
                status = EQUIVOCATION
            elif not tip.get("owner") or tip.get("target") is None:
                status = REVOKED
            elif now and tip.get("expires") is not None and int(tip["expires"]) <= timeslate_ms(now):
                status = EXPIRED
            else:
                status = self.claim_finality(tip, now)
            ranked.append((status, chain))
        chosen = self._choose(ranked)
        status, chain = chosen
        tip = chain["tip"]
        root = self._establishing(tip)
        witnesses = self.valid_witnesses(root, now) if now else []
        target = tip.get("target")
        hidden = status in {FORK, EQUIVOCATION, REVOKED}
        return {
            "code": status,
            "owner": None if hidden else (str(tip.get("owner") or "") or None),
            "target": None if hidden or not isinstance(target, Mapping) else str(target.get("value") or ""),
            "target_kind": None if hidden or not isinstance(target, Mapping) else str(target.get("type") or ""),
            "record_hash": None if hidden else tip.get("record_hash"),
            "seq": None if hidden else tip.get("seq"),
            "anchored_at": "" if hidden else self._stamp(root),
            "finality": FINAL if status == OK else PENDING if status == PENDING else None,
            "witnesses": 0 if hidden else len(witnesses),
            "expires": None if hidden else tip.get("expires"),
            "key_checked": not hidden,
        }

    def _choose(self, ranked: list[tuple[str, dict[str, Any]]]) -> tuple[str, dict[str, Any]]:
        def earliest(rows: list[tuple[str, dict[str, Any]]]) -> tuple[str, dict[str, Any]]:
            rows.sort(key=lambda item: (self._stamp(item[1]["root"]), item[1]["root"]["record_hash"]))
            if len(rows) >= 2 and self._stamp(rows[0][1]["root"]) == self._stamp(rows[1][1]["root"]):
                return FORK, rows[0][1]
            return rows[0]

        finals = [item for item in ranked if item[0] == FINAL]
        if finals:
            status, chain = earliest(finals)
            return (OK, chain) if status == FINAL else (FORK, chain)
        pendings = [item for item in ranked if item[0] == PENDING]
        if pendings:
            return earliest(pendings)
        for code in (EXPIRED, REVOKED, FORK, EQUIVOCATION):
            matched = [item for item in ranked if item[0] == code]
            if matched:
                if code in {EXPIRED, REVOKED}:
                    return earliest(matched)
                return matched[0]
        return ranked[0]

    def _attempt(self, rec: Mapping[str, Any], now: str | None) -> AdoptResult:
        digest = str(rec["record_hash"])
        handle = str(rec["handle"])
        if digest in self._by_hash or any(item["record_hash"] == digest for item in self._equiv_proofs):
            return _result(True, IDEMPOTENT, digest, f"{IDEMPOTENT}: statement already anchored")
        if handle in self._equiv:
            return _result(False, EQUIVOCATION, digest, f"{EQUIVOCATION}: handle signed conflicting statements at one seq")
        conflict = self._equivocation(rec, now)
        if conflict is not None:
            return conflict
        parent = self._handle_parent(rec)
        if isinstance(parent, AdoptResult):
            return parent
        if rec["kind"] == KIND_NAME:
            name_result = self._name_rules(rec, now)
            if name_result is not None:
                return name_result
        elif rec["kind"] == KIND_WITNESS:
            witnessed = self._witness_rules(rec, now)
            if isinstance(witnessed, AdoptResult):
                return witnessed
        self._adopt(rec, now)
        return _result(True, OK, digest, f"{OK}: anchored")

    def _equivocation(self, rec: Mapping[str, Any], now: str | None) -> AdoptResult | None:
        digest = str(rec["record_hash"])
        rivals = [
            other
            for other in list(self._records) + list(self._batch)
            if other["handle"] == rec["handle"] and other["seq"] == rec["seq"] and other["record_hash"] != digest
        ]
        if not rivals:
            return None
        self._flag(rec, rivals[0], now)
        tip = self._handle_tip(str(rec["handle"]))
        prev = str(rec["prev"])
        older = tip is not None and int(rec["seq"]) < int(tip["seq"])
        unknown_prev = prev != GENESIS_PREV and prev not in self._by_hash
        if older or unknown_prev:
            return _result(False, ROLLBACK, digest, f"{ROLLBACK}: seq does not extend the handle tip")
        return _result(
            False,
            EQUIVOCATION,
            digest,
            f"{EQUIVOCATION}: two statements share a handle and seq; neither is served",
        )

    def _handle_parent(self, rec: Mapping[str, Any]) -> AdoptResult | Mapping[str, Any] | None:
        digest = str(rec["record_hash"])
        prev = str(rec["prev"])
        tip = self._handle_tip(str(rec["handle"]))
        if prev == GENESIS_PREV:
            if rec["seq"] != 1:
                return _result(False, BAD_SEQUENCE, digest, f"{BAD_SEQUENCE}: the first act is seq 1")
            if tip is not None:
                return _result(False, ROLLBACK, digest, f"{ROLLBACK}: handle chain already moved past genesis")
            return None
        parent = self._by_hash.get(prev)
        if parent is None:
            if any(item["record_hash"] == prev for item in self._batch):
                return _result(False, WAIT, digest, WAIT)
            if tip is not None and rec["seq"] <= tip["seq"]:
                return _result(False, ROLLBACK, digest, f"{ROLLBACK}: seq is not newer than the handle tip")
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: handle prev is not anchored")
        if parent["handle"] != rec["handle"]:
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: prev belongs to another handle")
        if tip is not None and parent["record_hash"] != tip["record_hash"]:
            if rec["seq"] <= tip["seq"]:
                return _result(False, ROLLBACK, digest, f"{ROLLBACK}: seq does not extend the handle tip")
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: prev is not the handle tip")
        if rec["seq"] != parent["seq"] + 1:
            return _result(False, BAD_SEQUENCE, digest, f"{BAD_SEQUENCE}: seq must follow the handle tip")
        return parent

    def _name_rules(self, rec: Mapping[str, Any], now: str | None) -> AdoptResult | None:
        digest = str(rec["record_hash"])
        name = str(rec["name"])
        classified = classify(name)
        parent = None if rec["prev_record"] == GENESIS_PREV else self._by_hash.get(str(rec["prev_record"]))
        if rec["prev_record"] != GENESIS_PREV and parent is None:
            if any(item["record_hash"] == rec["prev_record"] for item in self._batch):
                return _result(False, WAIT, digest, WAIT)
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: prev_record is not anchored")
        if parent is not None and parent.get("name") != name:
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: prev_record belongs to another name")
        if parent is not None and now and self._stamp(parent) and now < self._stamp(parent):
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: anchored_at moved backwards")
        if classified.kind == "self_cert":
            if rec["owner"] != rec["handle"] or rec["target"] is None:
                return _result(False, SELF_CERT_FIXED, digest, f"{SELF_CERT_FIXED}: the handle name is not transferred or released")
            return None
        if now and rec.get("expires") is not None and int(rec["expires"]) <= timeslate_ms(now):
            return _result(False, EXPIRED, digest, f"{EXPIRED}: expires is already past")
        released_parent = parent is not None and (parent.get("owner") == "" or parent.get("target") is None)
        new_claim = rec["owner"] == rec["handle"] and rec["target"] is not None and (parent is None or released_parent)
        if new_claim:
            try:
                pow_meets(rec)
            except NameRefuse as exc:
                return _result(False, exc.code, digest, str(exc))
        elif parent is None:
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: an update, transfer, or release needs a parent record")
        elif str(parent.get("owner") or "") != rec["handle"]:
            return _result(False, NOT_OWNER, digest, f"{NOT_OWNER}: signer is not the current owner")
        if new_claim or (rec["owner"] and rec["owner"] != rec["handle"]):
            owner = str(rec["owner"])
            active = self._active_names(owner, now)
            if name not in active and len(active) >= CAP_PER_HANDLE:
                return _result(False, OVER_CAP, digest, f"{OVER_CAP}: a handle holds {CAP_PER_HANDLE} friendly names")
        return None

    def _witness_rules(self, rec: Mapping[str, Any], now: str | None) -> AdoptResult | None:
        subject = self._by_hash.get(str(rec["subject_hash"]))
        if subject is None:
            if any(item["record_hash"] == rec["subject_hash"] for item in self._batch):
                return _result(False, WAIT, rec["record_hash"], WAIT)
            return _result(False, BAD_CHAIN, rec["record_hash"], f"{BAD_CHAIN}: witnessed claim is not anchored")
        if subject.get("kind") != KIND_NAME or not subject.get("owner") or subject.get("target") is None:
            return _result(False, BAD_CHAIN, rec["record_hash"], f"{BAD_CHAIN}: a witness points at a live name record")
        if subject.get("handle") != rec["subject_handle"]:
            return _result(False, BAD_CHAIN, rec["record_hash"], f"{BAD_CHAIN}: subject handle does not match the claim")
        if now and rec["timeslate"] > now:
            return _result(False, BAD_CHAIN, rec["record_hash"], f"{BAD_CHAIN}: witness timeslate is after now")
        return None

    def _adopt(self, rec: Mapping[str, Any], now: str | None) -> None:
        stored = dict(rec)
        self._records.append(stored)
        self._by_hash[stored["record_hash"]] = stored
        stamp = now or ""
        self._anchored_at[stored["record_hash"]] = stamp
        label = str(stored.get("name") or stored.get("subject_hash") or stored["handle"])
        self._append(
            "record",
            label,
            stored["record_hash"],
            str(stored.get("timeslate") or stamp),
            stored,
            prior_hash="",
            anchored_at=stamp,
        )
