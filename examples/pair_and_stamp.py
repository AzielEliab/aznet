#!/usr/bin/env python3
"""Pair AZBrowser, FragGate unlock, stamp a public demo hash.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from pathlib import Path

from aznet.chain import Ledger
from aznet.garden import demo_cards


def main() -> None:
    path = Path("examples/_out") / "aznet_ledger.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    ledger = Ledger((), path=path)
    ledger.pair(timestamp="2026-09-06T12:00:00Z")
    ledger.unlock(timestamp="2026-09-06T12:01:00Z")
    card = demo_cards()[0]
    rec = ledger.stamp(card["hash_hex"], timestamp="2026-09-06T12:02:00Z")
    print(rec.receipt_hash)
    print(rec.hash_hex)


if __name__ == "__main__":
    main()
