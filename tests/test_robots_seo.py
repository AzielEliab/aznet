"""robots.txt / llms / sitemap / cite are AI Allow surfaces, not directory dumps."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
INDEX = (ROOT / "workers/download-tracker/src/index.js").read_text(encoding="utf-8")
PUBLIC_ROBOTS = (ROOT / "workers/download-tracker/public/robots.txt").read_text(encoding="utf-8")
TOML = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")

REQUIRED_AGENTS = (
    "GPTBot",
    "ChatGPT-User",
    "OAI-SearchBot",
    "Google-Extended",
    "Googlebot",
    "ClaudeBot",
    "Claude-SearchBot",
    "Claude-User",
    "anthropic-ai",
    "PerplexityBot",
    "Perplexity-User",
    "bingbot",
    "Meta-ExternalAgent",
    "Applebot-Extended",
    "Amazonbot",
    "CCBot",
    "cohere-ai",
    "Diffbot",
    "Bytespider",
    "Omgilibot",
)

DIR_GARBAGE = (
    ".pytest_cache",
    ".wrangler",
    "node_modules",
    "__pycache__",
    ".venv",
    "public/.gitkeep",
)

LISTING_APIS = (
    "readdirSync",
    "readdir(",
    "opendir",
    "fs.readdir",
    "ASSETS.list",
    "Path('.').iterdir",
    "os.listdir",
)


def _robots_fn() -> str:
    match = re.search(r"export function robotsTxt\(\) \{.*?\n\}\n\nexport function llmsTxt", HOME, re.S)
    assert match, "robotsTxt() must exist"
    return match.group(0)


def test_robots_starts_with_star_allow_not_directory_names() -> None:
    body = PUBLIC_ROBOTS
    assert body.startswith("User-agent: *\nAllow: /\n")
    assert "Content-Signal: search=yes, ai-input=yes, ai-train=yes" in body
    assert "Sitemap: https://aznet-download-tracker.vibelock.workers.dev/sitemap.xml" in body
    first_agent = body.splitlines()[0]
    assert first_agent == "User-agent: *"
    for junk in DIR_GARBAGE:
        assert junk not in body
        assert junk not in first_agent


def test_robots_lists_ai_allow_policy_agents() -> None:
    for agent in REQUIRED_AGENTS:
        assert f"User-agent: {agent}" in PUBLIC_ROBOTS
        assert f"User-agent: {agent}\nAllow: /" in PUBLIC_ROBOTS
    assert "Disallow: /" not in PUBLIC_ROBOTS
    assert "meta-externalagent" not in PUBLIC_ROBOTS


def test_robots_builder_is_hardcoded_allow_list() -> None:
    fn = _robots_fn()
    assert "AI_CRAWLER_AGENTS" in fn
    assert "User-agent: *" in fn or '"User-agent: *"' in HOME
    for api in LISTING_APIS:
        assert api not in fn
        assert api not in HOME.split("export function renderHome")[0]
    for junk in DIR_GARBAGE:
        assert junk not in fn


def test_worker_and_static_robots_stay_aligned() -> None:
    for agent in REQUIRED_AGENTS:
        assert f'"{agent}"' in HOME
        assert f"User-agent: {agent}" in PUBLIC_ROBOTS
    assert "run_worker_first" in TOML
    assert '"/robots.txt"' in TOML
    assert '"/cite"' in TOML or "/cite" in TOML


def test_llms_and_cite_are_not_directory_listings() -> None:
    assert "function llmsTxt()" in HOME
    assert "Author: Aziel Eliab" in HOME
    assert "cite.json" in HOME
    assert "www.azielcorpuslibrary.net" in HOME
    assert "ChatGPT (GPT Actions / OpenAI)" in HOME
    assert "other MCP/OpenAPI-capable assistants" in HOME
    llms = HOME.split("export function llmsTxt()")[1].split("export function handleSeoRoutes")[0]
    cite = HOME.split("export function citePayload()")[1].split("export function jsonLd()")[0]
    sitemap = HOME.split("export function sitemapXml()")[1].split("export function robotsTxt()")[0]
    for junk in DIR_GARBAGE:
        assert junk not in llms
        assert junk not in cite
        assert junk not in sitemap
    assert 'aka: AUTHOR_AKA' in cite or 'aka:' in cite
    assert "library:" in cite
    assert "identity:" in cite
    assert "Aziel Eliab only" in cite
    for path in ("/download", "/cite.json", "/llms.txt", "/openapi.json"):
        assert path in sitemap
    assert ".pytest_cache" not in sitemap
    assert "handleSeoRoutes" in INDEX
    assert 'path === "/cite"' in HOME or 'path === "/cite.json" || path === "/cite"' in HOME
