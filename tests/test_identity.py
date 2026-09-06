"""Public identity is Aziel Eliab only."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    "Col" + "lin H" + "orton",
    "Ja" + "ck Al" + "tman",
    "GodLock" + ".AZ",
)

SKIP_SUFFIXES = {".png", ".tar.gz", ".jpg", ".woff"}


def test_tree_names_aziel_eliab_only() -> None:
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES or path.name.endswith(".tar.gz"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for name in FORBIDDEN:
            if name in text and "forbidden" not in text.lower() and ' + "' not in text:
                if path.name == "doctor.py":
                    continue
                hits.append(f"{path}: {name}")
    assert hits == []


def test_readme_author() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Aziel Eliab" in readme
    assert "Apache-2.0" in readme
    assert "AZNet" in readme
    assert "AZBrowser" in readme
