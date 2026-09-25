"""Local UI page exposes garden / pair / memorial / witness."""

from __future__ import annotations

from pathlib import Path

from aznet.chain import Ledger
from aznet.ui import PAGE, ensure_local_pair, pair_words, render_page


def test_ui_has_ops() -> None:
    for token in ("btn-pair", "btn-unlock", "btn-stamp", "btn-verify", "btn-memorial", "btn-witness"):
        assert token in PAGE
    assert "Gold Pages" in PAGE
    assert "Aziel Eliab" in PAGE
    assert "Re-pair" in PAGE
    assert "Pair with AZBrowser" not in PAGE
    for section in ("garden", "memorial", "stamps", "receipts", "pair", "unlock", "staticclock"):
        assert f'id="{section}"' in PAGE


def test_ui_is_a_human_page(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("AZNET_LEDGER", str(tmp_path / "ledger.jsonl"))
    assert "Advanced" in PAGE
    assert "Open Advanced" in PAGE
    assert "prefers-color-scheme" in PAGE
    assert ":focus-visible" in PAGE
    assert 'createElement("button")' in PAGE
    assert "hover reveal" not in PAGE
    assert "JSON.stringify(t" not in PAGE
    page = render_page()
    head, notes = page.split('id="notes"', 1)
    assert "Paired. Ready." in head
    assert "Not paired yet" not in head
    assert 'id="btn-pair-now" hidden' in head
    assert "THIS IS NOT" not in head
    assert "Not an alt internet" not in head
    assert "THIS IS NOT" in notes
    assert "127.0.0.1:8878" in head
    assert "Zone" in page or 'id="clock"' in page
    ledger = Ledger.load(tmp_path / "ledger.jsonl")
    assert ledger.pair_status() == "PAIRED"
    assert sum(1 for row in ledger.receipts if row.event_kind == "PAIR") == 1
    again = render_page()
    assert "Paired. Ready." in again
    ledger = Ledger.load(tmp_path / "ledger.jsonl")
    assert sum(1 for row in ledger.receipts if row.event_kind == "PAIR") == 1


def test_pair_words_and_broken_stay_put(tmp_path: Path, monkeypatch) -> None:
    assert pair_words("PAIRED", "LOCKED") == "Paired. Ready."
    assert pair_words("BROKEN", "LOCKED") == "Pair is broken. Re-pair to continue."
    path = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("AZNET_LEDGER", str(path))
    first = ensure_local_pair()
    assert first.pair_status() == "PAIRED"
    # A second call must not append another token.
    second = ensure_local_pair(Ledger.load(path))
    assert sum(1 for row in second.receipts if row.event_kind == "PAIR") == 1
