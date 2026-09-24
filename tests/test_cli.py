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
    rc = main(["verify", "--json", str(path)])
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
    human_garden = capsys.readouterr().out
    assert "Gold Pages" in human_garden
    assert not human_garden.lstrip().startswith("{")
    assert main(["garden", "--json"]) == 0
    garden = json.loads(capsys.readouterr().out)
    assert garden["favorites"] is False
    assert garden["cards"]
    assert main(["--json", "time"]) == 0
    clock = json.loads(capsys.readouterr().out)
    assert clock["note"].startswith("StaticClock")
    assert main(["time"]) == 0
    human_time = capsys.readouterr().out
    assert "Zone" in human_time
    assert "StaticClock" in human_time
    assert not human_time.lstrip().startswith("{")


def test_cli_welcome_help_and_misuse(capsys) -> None:
    assert main([]) == 0
    welcome = capsys.readouterr().out
    assert "aznet pair" in welcome
    assert "aznet ui" in welcome
    assert "Not an alt" not in welcome
    assert "required" not in welcome.lower()
    assert main(["--help"]) == 0
    help_text = capsys.readouterr().out
    assert "Common commands:" in help_text
    assert "aznet doctor" in help_text
    assert "Not an alt" not in help_text
    assert main(["bogus"]) == 2
    err = capsys.readouterr().err
    assert 'Unknown command "bogus"' in err
    assert "aznet --help" in err
    assert main(["stamp"]) == 2
    missing = capsys.readouterr().err
    assert "64-character" in missing
    assert "aznet stamp --hash" in missing
