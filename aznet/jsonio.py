"""JSON / JSONL import/export for AZNet. Author: Aziel Eliab."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aznet import __version__
from aznet.chain import Ledger, default_ledger_path
from aznet.receipt import Receipt

AUTHOR = "Aziel Eliab"
PRODUCT = "AZNet"
STATE_NAME = ".aznet-state.json"


def _as_path(path: str | Path) -> Path:
    return Path(path)


def _parse_rows(text: str) -> list[Any]:
    stripped = text.lstrip()
    if stripped.startswith("["):
        doc = json.loads(text)
        return list(doc)
    if stripped.startswith("{"):
        obj = json.loads(text)
        if isinstance(obj, dict):
            rows = obj.get("ledger") or obj.get("chain") or obj.get("receipts")
            if isinstance(rows, list):
                return rows
            return [obj]
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def import_json(path: str | Path) -> dict[str, Any]:
    pth = _as_path(path)
    text = pth.read_text(encoding="utf-8")
    dest = Path.cwd() / STATE_NAME
    dest.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    try:
        rows = _parse_rows(text)
        keys = sorted({str(k) for row in rows if isinstance(row, dict) for k in row.keys()})
    except Exception:
        keys = []
        rows = []
    return {
        "ok": True,
        "imported": str(pth),
        "stored": str(dest),
        "keys": keys,
        "count": len(rows) if isinstance(rows, list) else 0,
        "author": AUTHOR,
        "product": PRODUCT,
        "version": __version__,
    }


def export_json(path: str | Path) -> dict[str, Any]:
    pth = _as_path(path)
    src = Path.cwd() / STATE_NAME
    payload: Any = {}
    if src.exists():
        try:
            payload = json.loads(src.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    ledger_path = default_ledger_path()
    ledger_rows: list[Any] = []
    if ledger_path.is_file():
        ledger_rows = [
            json.loads(line)
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    doc = {
        "product": PRODUCT,
        "package": "aznet",
        "version": __version__,
        "author": AUTHOR,
        "payload": payload,
        "ledger": ledger_rows,
    }
    pth.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "exported": str(pth),
        "author": AUTHOR,
        "product": PRODUCT,
        "version": __version__,
    }


def import_ledger(path: str | Path, dest: str | Path | None = None) -> Ledger:
    src = _as_path(path)
    rows = _parse_rows(src.read_text(encoding="utf-8"))
    target = Path(dest) if dest is not None else default_ledger_path()
    if target.exists() and target.stat().st_size > 0:
        raise ValueError(f"refusing to overwrite existing ledger {target}; append-only")
    receipts = [Receipt.from_dict(row) for row in rows]
    return Ledger(receipts, path=target)
