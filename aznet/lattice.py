"""Lattice walk for AZNet receipts. Author: Aziel Eliab only."""

from __future__ import annotations

from dataclasses import dataclass

from aznet.canon import HONEST, ROLE
from aznet.chain import Ledger, VerifyResult


@dataclass(frozen=True)
class LatticeResult:
    ok: bool
    length: int
    garden: int
    stamps: int
    memorials: int
    pairs: int
    unlocks: int
    first_hash: str | None
    last_hash: str | None
    errors: list[str]
    role: str
    note: str


def walk(ledger: Ledger) -> LatticeResult:
    rec = ledger.verify()
    errors = list(rec.errors)
    counts = {"GARDEN": 0, "STAMP": 0, "MEMORIAL": 0, "PAIR": 0, "UNLOCK": 0}
    for item in ledger.receipts:
        if item.event_kind in counts:
            counts[item.event_kind] += 1
    return LatticeResult(
        ok=not errors,
        length=rec.length,
        garden=counts["GARDEN"],
        stamps=counts["STAMP"],
        memorials=counts["MEMORIAL"],
        pairs=counts["PAIR"],
        unlocks=counts["UNLOCK"],
        first_hash=rec.first_hash,
        last_hash=rec.last_hash,
        errors=errors,
        role=ROLE,
        note=HONEST,
    )


def verify_lattice(ledger: Ledger) -> LatticeResult:
    return walk(ledger)


def as_verify_dict(result: VerifyResult) -> dict[str, object]:
    return {
        "ok": result.ok,
        "length": result.length,
        "first_hash": result.first_hash,
        "last_hash": result.last_hash,
        "errors": result.errors,
    }
