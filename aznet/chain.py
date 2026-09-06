"""Append-only hash-chained lattice for AZNet. Author: Aziel Eliab only."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from aznet.canon import ABSENT, GENESIS_PREV_HASH, digest
from aznet.clock import advise, utc_now
from aznet.errors import AppendOnlyError, IntegrityRefuse, LedgerError, PairError, WitnessError
from aznet.receipt import Receipt

DEFAULT_LEDGER = "aznet_ledger.jsonl"


def default_ledger_path() -> Path:
    env = os.environ.get("AZNET_LEDGER")
    if env:
        return Path(env)
    return Path.cwd() / DEFAULT_LEDGER


def _append_line(path: Path, rec: Receipt) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    length: int
    first_hash: str | None
    last_hash: str | None
    errors: list[str]


class Ledger:
    """Append-only receipt lattice. Hashes only."""

    def __init__(self, receipts: Iterable[Receipt] = (), *, path: Path | None = None) -> None:
        self._receipts: tuple[Receipt, ...] = tuple(receipts)
        self._path = path

    @classmethod
    def load(cls, path: Path | str | None = None) -> Ledger:
        target = Path(path) if path is not None else default_ledger_path()
        if not target.is_file():
            return cls((), path=target)
        rows: list[Receipt] = []
        for line in target.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(Receipt.from_dict(json.loads(line)))
        return cls(rows, path=target)

    @property
    def receipts(self) -> tuple[Receipt, ...]:
        return self._receipts

    @property
    def path(self) -> Path | None:
        return self._path

    def tip(self) -> str:
        if not self._receipts:
            return GENESIS_PREV_HASH
        return self._receipts[-1].receipt_hash

    def genesis(self) -> str:
        if not self._receipts:
            return GENESIS_PREV_HASH
        return self._receipts[0].receipt_hash

    def latest(self, kind: str | None = None) -> Receipt | None:
        for rec in reversed(self._receipts):
            if kind is None or rec.event_kind == kind:
                return rec
        return None

    def pair_status(self) -> str:
        rec = self.latest("PAIR")
        return rec.pair_status if rec and rec.pair_status else "UNPAIRED"

    def unlock_status(self) -> str:
        rec = self.latest("UNLOCK")
        if self.pair_status() != "PAIRED":
            return "LOCKED"
        return rec.unlock_status if rec and rec.unlock_status else "LOCKED"

    def require_ready(self, *, for_memorial: bool = False) -> None:
        if for_memorial:
            return
        if self.pair_status() != "PAIRED":
            raise PairError("AZNet + AZBrowser are both required to run. Pair first. FragGate unlocks access.")
        if self.unlock_status() != "UNLOCKED":
            raise PairError("FragGate unlock required. Pairing alone does not open the garden.")

    def _append(self, rec: Receipt) -> Receipt:
        if self._path is not None:
            _append_line(self._path, rec)
        self._receipts = self._receipts + (rec,)
        return rec

    def refuse_mutate(self) -> None:
        raise AppendOnlyError("AZNet ledgers are append-only. Withdraw rather than coerce.")

    def pair(
        self,
        *,
        azbrowser: str = "https://github.com/AzielEliab/azbrowser",
        aznet_node: str = "device-local",
        timestamp: str | None = None,
        note: str = "",
    ) -> Receipt:
        clock = advise(timestamp)
        rec = Receipt.create(
            event_kind="PAIR",
            prev_hash=self.tip(),
            timestamp=clock["local"],
            pair_status="PAIRED",
            unlock_status="LOCKED",
            azbrowser=azbrowser,
            aznet_node=aznet_node,
            fraggate="required",
            staticclock=clock["stamp"],
            zone=clock["zone"],
            note=note or "AZNet + AZBrowser paired. FragGate still required.",
        )
        return self._append(rec)

    def unlock(
        self,
        *,
        timestamp: str | None = None,
        note: str = "",
    ) -> Receipt:
        if self.pair_status() != "PAIRED":
            raise PairError("FragGate unlock requires AZNet + AZBrowser pair first.")
        clock = advise(timestamp)
        rec = Receipt.create(
            event_kind="UNLOCK",
            prev_hash=self.tip(),
            timestamp=clock["local"],
            pair_status="PAIRED",
            unlock_status="UNLOCKED",
            azbrowser="https://github.com/AzielEliab/azbrowser",
            fraggate="unlocked",
            staticclock=clock["stamp"],
            zone=clock["zone"],
            note=note or "FragGate unlocked access. Side-net remains hash-only.",
        )
        return self._append(rec)

    def stamp(
        self,
        hash_hex: str,
        *,
        timestamp: str | None = None,
        note: str = "",
    ) -> Receipt:
        self.require_ready()
        clock = advise(timestamp)
        rec = Receipt.create(
            event_kind="STAMP",
            prev_hash=self.tip(),
            timestamp=clock["local"],
            hash_hex=hash_hex.lower(),
            pair_status="PAIRED",
            unlock_status="UNLOCKED",
            staticclock=clock["stamp"],
            zone=clock["zone"],
            note=note or "TemporalLock-style stamp. Hash only.",
        )
        return self._append(rec)

    def garden_entry(
        self,
        hash_hex: str,
        *,
        label: str,
        timestamp: str | None = None,
        note: str = "",
    ) -> Receipt:
        self.require_ready()
        if any(token in label.lower() for token in ("http://", "https://", "payload", "key=")):
            raise IntegrityRefuse("Garden labels are short tokens. No URLs, payloads, or keys.")
        clock = advise(timestamp)
        rec = Receipt.create(
            event_kind="GARDEN",
            prev_hash=self.tip(),
            timestamp=clock["local"],
            hash_hex=hash_hex.lower(),
            label=label[:48],
            pair_status="PAIRED",
            unlock_status="UNLOCKED",
            staticclock=clock["stamp"],
            zone=clock["zone"],
            note=note or "Gold Pages card. Hash only. No rank.",
        )
        return self._append(rec)

    def memorial(
        self,
        *,
        reason: str,
        genesis_hash: str | None = None,
        final_hash: str | None = None,
        timestamp: str | None = None,
        note: str = "",
    ) -> Receipt:
        clock = advise(timestamp)
        rec = Receipt.create(
            event_kind="MEMORIAL",
            prev_hash=self.tip(),
            timestamp=clock["local"],
            genesis_hash=genesis_hash or self.genesis(),
            final_hash=final_hash or self.tip(),
            reason=reason,
            summary=reason,
            pair_status=self.pair_status(),
            unlock_status=self.unlock_status(),
            staticclock=clock["stamp"],
            zone=clock["zone"],
            note=note or "Terminal compromise memorial. Non-actionable summary only.",
        )
        return self._append(rec)

    def withdraw(self, *, timestamp: str | None = None, note: str = "") -> Receipt:
        clock = advise(timestamp)
        rec = Receipt.create(
            event_kind="WITHDRAW",
            prev_hash=self.tip(),
            timestamp=clock["local"],
            pair_status=self.pair_status(),
            unlock_status="LOCKED",
            staticclock=clock["stamp"],
            zone=clock["zone"],
            note=note or "Withdrawal over coercion. Node silent.",
        )
        return self._append(rec)

    def witness(self, witness_hash: str, *, timestamp: str | None = None) -> Receipt:
        from aznet.witness import expected_witness

        clock = advise(timestamp)
        expected = expected_witness()
        if witness_hash != expected:
            self.memorial(reason="ui_altered", timestamp=clock["local"])
            raise WitnessError("UI witness failed. Terminated. Memorial written. Truth Is No Defense — .AZNet — AZ.")
        rec = Receipt.create(
            event_kind="WITNESS",
            prev_hash=self.tip(),
            timestamp=clock["local"],
            witness_hash=witness_hash,
            pair_status=self.pair_status(),
            unlock_status=self.unlock_status(),
            staticclock=clock["stamp"],
            zone=clock["zone"],
            note="UI witness intact.",
        )
        return self._append(rec)

    def verify(self) -> VerifyResult:
        errors: list[str] = []
        n = len(self._receipts)
        first = self._receipts[0].receipt_hash if n else None
        last = self._receipts[-1].receipt_hash if n else None
        for i, rec in enumerate(self._receipts):
            expected = digest(rec.to_dict())
            if rec.receipt_hash != expected:
                errors.append(f"index {i}: stored receipt_hash {rec.receipt_hash} != recomputed {expected}")
            if rec.payload != ABSENT or rec.keys != ABSENT or rec.user_content != ABSENT:
                errors.append(f"index {i}: I1 leakage")
            if i == 0:
                if rec.prev_hash != GENESIS_PREV_HASH:
                    errors.append("index 0: prev_hash != GENESIS")
                continue
            if rec.prev_hash != self._receipts[i - 1].receipt_hash:
                errors.append(f"index {i}: prev_hash != previous.receipt_hash")
        return VerifyResult(ok=not errors, length=n, first_hash=first, last_hash=last, errors=errors)

    def show(self) -> Sequence[Receipt]:
        return self._receipts

    def as_rows(self) -> list[dict]:
        return [rec.to_dict() for rec in self._receipts]
