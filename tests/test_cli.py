"""CLI: version, pair, unlock, stamp, verify."""

from __future__ import annotations

import json
from pathlib import Path

from aznet import __version__
from aznet.cli import main


def test_cli_version(capsys) -> None:
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"aznet {__version__}"


def test_cli_pair_unlock_stamp_verify(tmp_path: Path, capsys) -> None:
    path = tmp_path / "aznet_ledger.jsonl"
    assert main(["pair", "--ledger", str(path)]) == 0
    capsys.readouterr()
    assert main(["unlock", "--ledger", str(path)]) == 0
    capsys.readouterr()
    rc = main(["stamp", "--ledger", str(path), "--hash", "c" * 64])
    assert rc == 0
    capsys.readouterr()
    rc = main(["verify", str(path)])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["length"] == 3
    rc = main(["receipts", str(path)])
    assert rc == 0
    shown = capsys.readouterr().out
    assert "ABSENT" in shown
    assert "STAMP" in shown


def test_cli_stamp_without_pair(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    assert main(["stamp", "--ledger", str(path), "--hash", "d" * 64]) == 2


def test_cli_verify_missing(tmp_path: Path) -> None:
    assert main(["verify", str(tmp_path / "missing.jsonl")]) == 2


def test_cli_garden_and_time(capsys) -> None:
    assert main(["garden"]) == 0
    garden = json.loads(capsys.readouterr().out)
    assert garden["favorites"] is False
    assert garden["cards"]
    assert main(["time"]) == 0
    clock = json.loads(capsys.readouterr().out)
    assert clock["note"].startswith("StaticClock")
