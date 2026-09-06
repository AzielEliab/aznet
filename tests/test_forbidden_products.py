"""Do not wire Lumen, AZInterface, AZ-OS Hub, or Interface products."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_WIRE = (
    "lumen" + "-download-tracker",
    "azinterface" + "-download-tracker",
    "azos" + "-hub",
    "az-os" + "-hub",
    "/p/" + "lumen",
    "/p/" + "azinterface",
)


def test_no_forbidden_product_wiring() -> None:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.suffix in {".png", ".tar.gz"} or path.name.endswith(".tar.gz"):
            continue
        if path.name == "test_forbidden_products.py":
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except Exception:
            continue
        for token in FORBIDDEN_WIRE:
            if token in text:
                hits.append(f"{path}: {token}")
    assert hits == []


def test_azbrowser_is_the_pair() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "github.com/AzielEliab/azbrowser" in readme
    assert "AZNet + AZBrowser" in readme or "AZNet + [AZBrowser]" in readme
