"""Local UI page exposes garden / pair / memorial / witness."""

from __future__ import annotations

from aznet.ui import PAGE


def test_ui_has_ops() -> None:
    for token in ("btn-pair", "btn-unlock", "btn-stamp", "btn-verify", "btn-memorial", "btn-witness"):
        assert token in PAGE
    assert "Gold Pages" in PAGE
    assert "Aziel Eliab" in PAGE
    for section in ("garden", "memorial", "stamps", "receipts", "pair", "unlock", "staticclock"):
        assert f'id="{section}"' in PAGE
