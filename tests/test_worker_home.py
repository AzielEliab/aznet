"""Worker homepage is AZNet software, not a downloads shell."""

from __future__ import annotations

from pathlib import Path

HOME = Path("workers/download-tracker/src/home.js").read_text(encoding="utf-8")
INDEX = Path("workers/download-tracker/src/index.js").read_text(encoding="utf-8")
RUNTIME = Path("workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
TOML = Path("workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")


def test_title_is_product_not_downloads_shell() -> None:
    assert "AZNet — Aziel Eliab" in HOME
    assert "AZNet downloads" not in HOME


def test_seo_and_softwareapplication_json_ld() -> None:
    assert "application/ld+json" in HOME
    assert "SoftwareApplication" in HOME
    assert "Aziel Eliab" in HOME
    assert "cite.json" in HOME
    assert "sitemap.xml" in HOME
    assert "AI_CRAWLER_AGENTS" in HOME
    assert "User-agent: *" in HOME
    assert "GPTBot" in HOME
    assert ".pytest_cache" not in HOME
    assert ".wrangler" not in HOME
    assert "Everblooming sigil" in HOME
    assert "/sigil.png" in HOME


def test_workspace_calls_real_ops() -> None:
    for path in ("/v1/pair", "/v1/unlock", "/v1/stamp", "/v1/verify", "/v1/memorial", "/v1/garden"):
        assert path in HOME or path in RUNTIME
    assert "btn-pair" in HOME
    assert "btn-unlock" in HOME
    assert "btn-stamp" in HOME
    assert "btn-memorial" in HOME
    assert "Garden Rolodex" in HOME or "Gold Pages" in HOME


def test_ui_witness_sections() -> None:
    for section in ("garden", "memorial", "stamps", "receipts", "pair", "unlock", "staticclock"):
        assert f'id="{section}"' in HOME


def test_black_white_gold() -> None:
    assert "--bg: #000000" in HOME or "--bg: #000" in HOME
    assert "--ink: #ffffff" in HOME or "--ink: #fff" in HOME
    assert "--gold: #c9a227" in HOME


def test_download_install_and_identity_remain() -> None:
    assert "/download?asset=" in HOME
    assert "aznet-0.1.0.tar.gz" in HOME
    assert "One-click install" in HOME
    assert "Aziel Eliab only" in HOME
    assert "Apache-2.0" in HOME
    assert "Forks welcome" in HOME or "Forks are welcome" in HOME
    assert "aznet-download-tracker" in TOML


def test_no_invented_or_live_zenodo_identifier() -> None:
    assert "identifier:" not in HOME.split("export function jsonLd")[1].split("export function handleSeoRoutes")[0]
    assert "No DOI is invented here" in HOME
    assert "DOI =" not in INDEX
    assert "ZENODO =" not in INDEX


def test_worker_serves_home_and_seo() -> None:
    assert "renderHome" in INDEX
    assert "handleSeoRoutes" in INDEX
    assert 'url.pathname === "/"' in INDEX
    assert "/download" in INDEX
    assert "function totalKey()" in INDEX
    assert "ASSETS.fetch" in INDEX or "env.ASSETS" in INDEX
    assert "/count" in INDEX
    assert "views: stats.views" in INDEX
    assert "downloads: stats.downloads" in INDEX
    assert "by_repo" in INDEX
    assert "by_branch" in INDEX
    assert "by_fork" in INDEX
    assert "totalKey()" in INDEX
    assert 'await increment(env, dims)' in INDEX


def test_readme_lists_count_stats_and_hubs() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    skill = Path("SKILL.md").read_text(encoding="utf-8")
    assert "`{views, downloads, total}`" in readme or "{views, downloads, total}" in readme
    assert "by_repo" in readme
    assert "www.azielcorpuslibrary.net/software" in readme
    assert "godlock.uk/software" in readme
    assert "www.azieleliab.com" in readme
    for text in (readme, skill, RUNTIME):
        assert "/count" in text
        assert "/stats" in text
        assert "by_repo" in text
        assert "by_branch" in text
        assert "by_fork" in text
        assert "azielcorpuslibrary.net/software" in text
        assert "godlock.uk/software" in text
    assert '"/count"' in RUNTIME
    assert '"/stats"' in RUNTIME
    assert '"/download"' in RUNTIME
    assert "/count" in HOME
    assert "/stats" in HOME


def test_apps_stay_separate() -> None:
    assert "pair_token" in HOME or "pair_token" in RUNTIME
    assert "pair_flag" in HOME or "pair_flag" in RUNTIME
    assert "separate apps" in HOME.lower() or "Separate apps" in HOME
    assert "iframe" not in HOME.lower()
    assert "azbrowser-download-tracker" not in HOME
    assert "fraggate-download-tracker" not in HOME


def test_pairing_and_forbidden_products() -> None:
    assert "github.com/AzielEliab/azbrowser" in HOME
    assert "FragGate" in HOME
    assert "StaticClock" in HOME
    assert "Lumen" not in HOME or "Do not wire" in RUNTIME
    for name in ("AZInterface", "AZ-OS Hub"):
        assert name not in HOME
