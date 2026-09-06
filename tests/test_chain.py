"""Lattice verify, pairing, stamps, memorial, tamper detection."""

from __future__ import annotations

import json
from pathlib import Path

from aznet.canon import GENESIS_PREV_HASH
from aznet.chain import Ledger
from aznet.errors import PairError, WitnessError
from aznet.lattice import walk
from aznet.witness import expected_witness


def test_pair_unlock_stamp_verify(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    a = ledger.pair(timestamp="2026-09-06T12:00:00Z")
    assert a.prev_hash == GENESIS_PREV_HASH
    b = ledger.unlock(timestamp="2026-09-06T12:01:00Z")
    assert b.prev_hash == a.receipt_hash
    c = ledger.stamp("a" * 64, timestamp="2026-09-06T12:02:00Z")
    assert c.hash_hex == "a" * 64
    assert c.payload == "ABSENT"
    assert ledger.verify().ok
    lat = walk(ledger)
    assert lat.ok
    assert lat.stamps == 1
    assert lat.pairs == 1
    assert lat.unlocks == 1


def test_stamp_refuses_without_pair(tmp_path: Path) -> None:
    ledger = Ledger((), path=tmp_path / "l.jsonl")
    try:
        ledger.stamp("b" * 64, timestamp="2026-09-06T12:00:00Z")
        raise AssertionError("stamp must refuse without pair")
    except PairError:
        pass


def test_tamper_fails_verify(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    ledger.pair(timestamp="2026-09-06T12:00:00Z")
    lines = path.read_text(encoding="utf-8").splitlines()
    obj = json.loads(lines[0])
    obj["note"] = "TAMPERED"
    path.write_text(json.dumps(obj) + "\n", encoding="utf-8")
    loaded = Ledger.load(path)
    result = loaded.verify()
    assert not result.ok
    assert result.errors


def test_memorial_non_actionable(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    ledger.pair(timestamp="2026-09-06T12:00:00Z")
    rec = ledger.memorial(reason="isolation", timestamp="2026-09-06T12:05:00Z")
    assert rec.event_kind == "MEMORIAL"
    assert rec.summary == "isolation"
    assert rec.genesis_hash
    assert rec.final_hash
    text = path.read_text(encoding="utf-8")
    assert "exploit" not in text.lower()
    assert ledger.verify().ok


def test_bad_witness_memorializes(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    ledger = Ledger((), path=path)
    try:
        ledger.witness("0" * 64, timestamp="2026-09-06T12:00:00Z")
        raise AssertionError("bad witness must fail")
    except WitnessError:
        pass
    assert any(r.event_kind == "MEMORIAL" and r.reason == "ui_altered" for r in ledger.receipts)
    ledger.witness(expected_witness(), timestamp="2026-09-06T12:01:00Z")
    assert any(r.event_kind == "WITNESS" for r in ledger.receipts)
