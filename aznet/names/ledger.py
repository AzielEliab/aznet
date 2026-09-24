"""Local name ledger: verify, anchor, and remember. Append-only.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from aznet.errors import NameRefuse
from aznet.names.namespace import classify
from aznet.names.record import prepare
from aznet.names.wire import (
    ABSENT,
    ANCHOR_SPEC,
    BAD_CHAIN,
    BAD_SEQUENCE,
    BAD_SIGNATURE,
    CAP_PER_HANDLE,
    FORK,
    GENESIS_PREV,
    IDEMPOTENT,
    LEAK,
    LEAK_KEYS,
    LOST_RACE,
    MALFORMED,
    NOT_OWNER,
    OK,
    OVER_CAP,
    SELF_CERT_FIXED,
    SYNC_SPEC,
    WAIT,
    anchor_hash,
    is_hash,
)

DEFAULT_NAMES = "aznet_names.jsonl"


def default_names_path() -> Path:
    env = os.environ.get("AZNET_NAMES")
    if env:
        return Path(env)
    return Path.cwd() / DEFAULT_NAMES


@dataclass(frozen=True)
class AdoptResult:
    ok: bool
    code: str
    record_hash: str | None
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "record_hash": self.record_hash,
            "detail": self.detail,
        }


def _result(ok: bool, code: str, record_hash: str | None, detail: str) -> AdoptResult:
    return AdoptResult(ok, code, record_hash, detail)


def _effective_owner(rec: Mapping[str, Any]) -> str | None:
    if rec["op"] == "release":
        return None
    if rec["op"] == "transfer":
        return str(rec["successor"])
    return str(rec["owner"])


class NameLedger:
    """Append-only cache of anchored name records. Hashes and handles only."""

    def __init__(self, *, path: Path | None = None) -> None:
        self._path = path
        self._records: list[dict[str, Any]] = []
        self._by_hash: dict[str, dict[str, Any]] = {}
        self._forks: set[str] = set()
        self._tip = GENESIS_PREV
        self._batch: list[dict[str, Any]] = []

    @property
    def path(self) -> Path | None:
        return self._path

    @property
    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._records)

    def is_frozen(self, name: str) -> bool:
        return name in self._forks

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
        if row.get("spec") != ANCHOR_SPEC or kind not in {"record", "fork"}:
            raise NameRefuse(MALFORMED, "name ledger line is not an anchor")
        if row.get("prev_hash") != self._tip:
            raise NameRefuse(BAD_CHAIN, "anchor prev_hash does not match the local tip")
        expect = anchor_hash(row)
        if row.get("anchor_hash") != expect or not is_hash(str(row.get("anchor_hash"))):
            raise NameRefuse(BAD_CHAIN, "anchor_hash does not match")
        if kind == "fork":
            self._forks.add(str(row.get("name") or ""))
            self._tip = str(row["anchor_hash"])
            return
        record = row.get("record")
        if not isinstance(record, Mapping):
            raise NameRefuse(MALFORMED, "anchor record missing")
        prepared = prepare(record)
        if prepared["record_hash"] != row.get("record_hash"):
            raise NameRefuse(BAD_SIGNATURE, "anchored record_hash mismatch")
        self._records.append(prepared)
        self._by_hash[prepared["record_hash"]] = prepared
        self._tip = str(row["anchor_hash"])

    def verify(self) -> dict[str, Any]:
        errors: list[str] = []
        if self._path is None or not self._path.is_file():
            return {"ok": True, "length": len(self._records), "errors": errors, "forks": sorted(self._forks)}
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
            if row.get("kind") == "record":
                try:
                    prepare(row["record"])
                except NameRefuse as exc:
                    errors.append(f"line {index}: {exc}")
                seen += 1
            tip = str(row.get("anchor_hash") or "")
        return {"ok": not errors, "length": seen, "errors": errors, "forks": sorted(self._forks)}

    def export_sync(self) -> dict[str, Any]:
        """Peer envelope. Records only. No seeds, no payload bytes."""
        return {
            "spec": SYNC_SPEC,
            "payload": ABSENT,
            "keys": ABSENT,
            "user_content": ABSENT,
            "records": [dict(rec) for rec in self._records],
        }

    def accept(self, record: Mapping[str, Any]) -> AdoptResult:
        report = self.ingest(
            {
                "spec": SYNC_SPEC,
                "payload": ABSENT,
                "keys": ABSENT,
                "user_content": ABSENT,
                "records": [dict(record)],
            }
        )
        row = report["results"][0]
        return AdoptResult(bool(row["ok"]), str(row["code"]), row["record_hash"], str(row["detail"]))

    def ingest(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
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
                pending.append((index, prepare(raw)))
            except NameRefuse as exc:
                results[index] = _result(False, exc.code, None, str(exc))
        while pending:
            self._batch = [rec for _index, rec in pending]
            rest: list[tuple[int, dict[str, Any]]] = []
            progressed = False
            snapshot = list(pending)
            for index, rec in snapshot:
                outcome = self._attempt(rec)
                if outcome.code == WAIT:
                    rest.append((index, rec))
                    continue
                results[index] = outcome
                progressed = True
                self._batch = [item for item in self._batch if item["record_hash"] != rec["record_hash"]]
            self._batch = []
            if not progressed:
                for index, rec in rest:
                    results[index] = _result(
                        False,
                        BAD_CHAIN,
                        rec["record_hash"],
                        f"{BAD_CHAIN}: prev is not anchored",
                    )
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
    ) -> None:
        row: dict[str, Any] = {
            "spec": ANCHOR_SPEC,
            "kind": kind,
            "prev_hash": self._tip,
            "record_hash": record_hash_hex,
            "name": name,
            "timeslate": timeslate,
        }
        row["anchor_hash"] = anchor_hash(row)
        if record is not None:
            row["record"] = dict(record)
        if self._path is not None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
        self._tip = row["anchor_hash"]

    def _freeze(self, name: str, timeslate: str, conflict_hash: str) -> None:
        if name in self._forks:
            return
        self._forks.add(name)
        stored = conflict_hash if is_hash(conflict_hash) else GENESIS_PREV
        self._append("fork", name, stored, timeslate, None)

    def _handle_tip(self, owner: str) -> dict[str, Any] | None:
        found = None
        for rec in self._records:
            if rec["owner"] == owner:
                found = rec
        return found

    def _active_names(self, owner: str) -> set[str]:
        tips: dict[str, dict[str, Any]] = {}
        for rec in self._records:
            if rec["name"] in self._forks:
                continue
            tips[rec["name"]] = rec
        active: set[str] = set()
        for name, rec in tips.items():
            if classify(name).kind == "self_cert":
                continue
            if rec["op"] == "release":
                continue
            if _effective_owner(rec) == owner:
                active.add(name)
        return active

    def _attempt(self, rec: Mapping[str, Any]) -> AdoptResult:
        digest = str(rec["record_hash"])
        name = str(rec["name"])
        if digest in self._by_hash:
            return _result(True, IDEMPOTENT, digest, f"{IDEMPOTENT}: record already anchored")
        if name in self._forks:
            return _result(False, FORK, digest, f"{FORK}: name is frozen; history is not rewritten")

        prev = str(rec["prev"])
        parent = None if prev == GENESIS_PREV else self._by_hash.get(prev)
        if prev != GENESIS_PREV and parent is None:
            if any(item["record_hash"] == prev for item in self._batch):
                return _result(False, WAIT, digest, WAIT)
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: name prev is not anchored")
        if parent is not None and parent["name"] != name:
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: prev belongs to another name")

        handle_prev = str(rec["handle_prev"])
        owner = str(rec["owner"])
        hparent = None if handle_prev == GENESIS_PREV else self._by_hash.get(handle_prev)
        if handle_prev != GENESIS_PREV and hparent is None:
            if any(item["record_hash"] == handle_prev for item in self._batch):
                return _result(False, WAIT, digest, WAIT)
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: handle_prev is not anchored")
        if hparent is not None and hparent["owner"] != owner:
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: handle_prev belongs to another owner")

        race = self._race(rec)
        if race is not None:
            return race

        chain = self._chain_rules(rec, parent)
        if chain is not None:
            return chain

        if not self._cap_ok(rec):
            return _result(False, OVER_CAP, digest, f"{OVER_CAP}: a handle holds {CAP_PER_HANDLE} friendly names")

        self._adopt(rec)
        return _result(True, OK, digest, f"{OK}: anchored")

    def _race(self, rec: Mapping[str, Any]) -> AdoptResult | None:
        digest = str(rec["record_hash"])
        rivals = [
            other
            for other in self._batch
            if other["record_hash"] != digest and other["name"] == rec["name"] and other["prev"] == rec["prev"]
        ]
        if any(other["timeslate"] < rec["timeslate"] for other in rivals):
            return _result(False, WAIT, digest, WAIT)
        ties = [other for other in rivals if other["timeslate"] == rec["timeslate"]]
        if ties:
            self._freeze(str(rec["name"]), str(rec["timeslate"]), str(ties[0]["record_hash"]))
            return _result(False, FORK, digest, f"{FORK}: equal TemporalLock timeslate; no winner is chosen")
        return None

    def _chain_rules(self, rec: Mapping[str, Any], parent: Mapping[str, Any] | None) -> AdoptResult | None:
        digest = str(rec["record_hash"])
        name = str(rec["name"])
        owner = str(rec["owner"])
        classified = classify(name)

        if parent is None:
            if rec["sequence"] != 1 or rec["prev"] != GENESIS_PREV:
                return _result(False, BAD_SEQUENCE, digest, f"{BAD_SEQUENCE}: a first record is sequence 1 at genesis")
        else:
            if rec["sequence"] != parent["sequence"] + 1:
                return _result(False, BAD_SEQUENCE, digest, f"{BAD_SEQUENCE}: sequence must follow the parent")
            if rec["timeslate"] < parent["timeslate"]:
                return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: timeslate moved backwards")
            if rec["timeslate"] == parent["timeslate"]:
                self._freeze(name, str(rec["timeslate"]), digest)
                return _result(False, FORK, digest, f"{FORK}: extension ties the parent timeslate")

        siblings = [item for item in self._records if item["name"] == name and item["prev"] == rec["prev"]]
        if siblings:
            sib = min(siblings, key=lambda item: item["timeslate"])
            if rec["timeslate"] > sib["timeslate"]:
                return _result(False, LOST_RACE, digest, f"{LOST_RACE}: an earlier claim is already anchored")
            self._freeze(name, str(rec["timeslate"]), digest)
            return _result(False, FORK, digest, f"{FORK}: a conflicting claim arrived after anchor; not rewritten")

        handle_tip = self._handle_tip(owner)
        if handle_tip is None:
            if rec["handle_prev"] != GENESIS_PREV:
                return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: first handle record must use genesis handle_prev")
        elif rec["handle_prev"] != handle_tip["record_hash"]:
            if rec["handle_prev"] != GENESIS_PREV and rec["handle_prev"] in self._by_hash:
                self._freeze(name, str(rec["timeslate"]), digest)
                return _result(False, FORK, digest, f"{FORK}: handle chain equivocation")
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: handle_prev is not the handle tip")

        op = str(rec["op"])
        if classified.kind == "self_cert":
            if op in {"claim", "transfer", "release"}:
                return _result(
                    False,
                    SELF_CERT_FIXED,
                    digest,
                    f"{SELF_CERT_FIXED}: the handle name is not claimed, transferred, or released",
                )
            if op not in {"update", "renew"}:
                return _result(False, MALFORMED, digest, f"{MALFORMED}: self-cert records are updates")
            return None

        if op == "claim":
            if parent is not None and parent["op"] != "release":
                return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: claim follows genesis or a release")
            return None
        if parent is None:
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: {op} needs a parent claim")
        if _effective_owner(parent) != owner:
            return _result(False, NOT_OWNER, digest, f"{NOT_OWNER}: signer is not the current owner")
        if op == "renew" and rec["renewal"] != "expiring":
            return _result(False, MALFORMED, digest, f"{MALFORMED}: renew uses renewal expiring")
        if op == "renew" and parent["expires_at"] and rec["expires_at"] <= parent["expires_at"]:
            return _result(False, BAD_CHAIN, digest, f"{BAD_CHAIN}: renew must extend expiry")
        if op not in {"update", "transfer", "release", "renew"}:
            return _result(False, MALFORMED, digest, f"{MALFORMED}: unsupported op")
        return None

    def _cap_ok(self, rec: Mapping[str, Any]) -> bool:
        if classify(str(rec["name"])).kind == "self_cert":
            return True
        if rec["op"] == "release":
            return True
        owner = _effective_owner(rec)
        if owner is None:
            return True
        active = self._active_names(owner)
        if rec["name"] in active:
            return True
        return len(active) < CAP_PER_HANDLE

    def _adopt(self, rec: Mapping[str, Any]) -> None:
        stored = dict(rec)
        self._records.append(stored)
        self._by_hash[stored["record_hash"]] = stored
        self._append("record", stored["name"], stored["record_hash"], stored["timeslate"], stored)
