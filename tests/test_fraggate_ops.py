"""FragGate catalog names must be the Worker UI / agent path. Author Aziel Eliab only."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "workers/download-tracker/src/home.js").read_text(encoding="utf-8")
RUNTIME = (ROOT / "workers/download-tracker/src/runtime.js").read_text(encoding="utf-8")
README = (ROOT / "README.md").read_text(encoding="utf-8")
SKILL = (ROOT / "SKILL.md").read_text(encoding="utf-8")
TOML = (ROOT / "workers/download-tracker/wrangler.toml").read_text(encoding="utf-8")

FRAGGATE_LIVE_OPS = (
    "health",
    "pair_status",
    "garden_list",
    "stamp",
    "verify_hash",
    "memorial_list",
    "memorial_append",
    "receipt_verify",
    "skill",
)


def test_catalog_live_ops_are_documented() -> None:
    for op in FRAGGATE_LIVE_OPS:
        assert op in RUNTIME, op
        assert op in SKILL, op


def test_agent_docs_use_pair_status_not_pair_as_catalog_op() -> None:
    assert '"op":"pair_status"' in RUNTIME
    assert '"op":"pair"' not in RUNTIME
    assert "pair_status" in HOME
    assert "btn-doctor" not in HOME
    assert "doctor is not a FragGate live op" in RUNTIME or "not a FragGate live op" in SKILL


def test_one_fraggate_door_and_separate_from_azbrowser() -> None:
    for text in (README, SKILL, RUNTIME, HOME):
        assert "aziel-runtime.vibelock.workers.dev/mcp" in text
        assert "Aziel Eliab" in text
    assert "AZIEL_RUNTIME" in TOML
    assert "separate software" in README.lower() or "separate apps" in README.lower()
    assert "FragGate only" in SKILL or "FragGate only" in RUNTIME
    assert "azbrowser-download-tracker" not in HOME
    assert "slug" in RUNTIME and "aznet" in RUNTIME


def test_mcp_pointer_never_404() -> None:
    assert 'path === "/mcp"' in RUNTIME
    assert "not a product MCP" in RUNTIME
    assert "FRAGGATE_CALL" in RUNTIME
    assert "/v1/fraggate/list" in RUNTIME
    assert "/v1/fraggate/call" in RUNTIME
    assert "/v1/fraggate/describe" in RUNTIME
    assert "/v1/fraggate/verify" in RUNTIME
