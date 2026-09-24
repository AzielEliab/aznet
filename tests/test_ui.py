"""Local UI page exposes garden / pair / memorial / witness."""

from __future__ import annotations

from aznet.ui import PAGE, render_page


def test_ui_has_ops() -> None:
    for token in ("btn-pair", "btn-unlock", "btn-stamp", "btn-verify", "btn-memorial", "btn-witness"):
        assert token in PAGE
    assert "Gold Pages" in PAGE
    assert "Aziel Eliab" in PAGE
    for section in ("garden", "memorial", "stamps", "receipts", "pair", "unlock", "staticclock"):
        assert f'id="{section}"' in PAGE


def test_ui_is_a_human_page() -> None:
    assert "Advanced" in PAGE
    assert "Pair AZBrowser" in PAGE
    assert "prefers-color-scheme" in PAGE
    assert ":focus-visible" in PAGE
    assert 'createElement("button")' in PAGE
    assert "hover reveal" not in PAGE
    assert "JSON.stringify(t" not in PAGE
    page = render_page()
    head, notes = page.split('id="notes"', 1)
    assert "Not paired yet — click Pair." in head
    assert "THIS IS NOT" not in head
    assert "Not an alt internet" not in head
    assert "THIS IS NOT" in notes
    assert "Zone" in page or 'id="clock"' in page
