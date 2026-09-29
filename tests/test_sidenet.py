"""AZN-SIDENET-1.0 stays additive, honest, and off the public FragGate op list."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from aznet.cli import main
from aznet.sidenet import L0_LIVE_OPS, peer_bearer, surface

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "workers/download-tracker/src/runtime.js"


def test_naming_lock_and_l0_unbroken() -> None:
    doc = surface()
    assert doc["spec"] == "AZN-SIDENET-1.0"
    assert doc["author"] == "Aziel Eliab"
    assert doc["naming_lock"]["sidenet"] == "aznet"
    assert doc["naming_lock"]["display"] == "AZnet"
    assert doc["naming_lock"]["client_surface"] == "AZ Browser"
    assert doc["product"] == "AZnet"
    assert doc["naming_lock"]["second_sidenet"] is False
    assert "AZBrowser" not in json.dumps(doc)
    assert doc["softwares_frozen"] is True
    assert doc["new_software_slug"] is False
    assert doc["second_door"] is False
    assert doc["door"] == "fraggate"
    assert doc["l0"]["status"] == "LIVE"
    assert doc["l0"]["unbroken"] is True
    assert doc["l0"]["remote_probed"] is False
    assert tuple(doc["l0"]["ops"]) == L0_LIVE_OPS
    assert "sidenet" not in doc["l0"]["ops"]
    assert doc["sidenet_in_l0_ops"] is False
    assert doc["sidenet_is_catalog_op"] is False
    assert doc["layers_replace_l0"] is False
    text = RUNTIME.read_text(encoding="utf-8")
    match = re.search(r"const FRAGGATE_LIVE_OPS = Object\.freeze\(\[([^\]]+)\]", text)
    assert match is not None
    ops = tuple(re.findall(r'"([^"]+)"', match.group(1)))
    assert ops == L0_LIVE_OPS
    assert "sidenet" not in ops


def test_cap7_mesh_dns_pairing_is_local_and_not_icann() -> None:
    doc = surface()
    cap7 = doc["cap7"]
    assert cap7["count"] == 7
    assert cap7["local_mesh_dns"] == "LIVE"
    assert cap7["public_dns"] == "SLOT"
    assert cap7["public_icann"] is False
    assert cap7["icann_registration"] is False
    assert cap7["standard_internet_reaches_cap7"] is False
    assert cap7["resolves_to_hub"] is False
    assert cap7["factory_owned_here"] is False
    assert cap7["shuffle_land"] == "SLOT"
    labels = [row["label"] for row in cap7["pairs"]]
    assert labels == ["azgrid", "azbooth", "azcloak", "azvault", "azshift", "azflag", "azstandby"]
    by_label = {row["label"]: row for row in cap7["pairs"]}
    assert by_label["azgrid"]["mesh_name"] == "azgrid.aziel"
    assert by_label["azgrid"]["alias"] == "azgrid.az"
    assert by_label["azgrid"]["mirrors"] == "azieleliab.com"
    assert by_label["azgrid"]["resolves_to_hub"] is False
    assert by_label["azgrid"]["public_icann"] is False
    assert by_label["azbooth"]["false_site"] is True
    assert by_label["azbooth"]["hub"] is None
    assert "baku" not in labels
    assert doc["public_icann"] is False
    assert doc["icann_registration"] is False
    assert doc["pairing"]["products_merged"] is False
    assert doc["pairing"]["peer"] == "azbrowser"
    assert doc["pairing"]["peer_name"] == "AZ Browser"
    assert doc["pairing"]["product_name"] == "AZnet"
    assert doc["pairing"]["tunnel"] is False


def test_qnm_bearer_stays_slot_and_other_bearers_refuse() -> None:
    qnm = peer_bearer("qnm")
    assert qnm["status"] == "SLOT"
    assert qnm["socket"] is False
    assert qnm["opened_here"] is False
    assert qnm["appropriate"] is True
    for name in ("tor", "wireguard", "icann", "public-dns", "gossip"):
        refused = peer_bearer(name)
        assert refused["status"] == "REFUSED"
        assert refused["socket"] is False
        assert refused["code"] == "AZN-BEARER-REFUSED"
    doc = surface()
    assert doc["peer_bearers"] == [qnm]
    assert doc["qnm"]["bearer_status"] == "SLOT"
    assert doc["socket"] is False
    assert doc["hosts_payloads"] is False
    assert doc["executes_peer_code"] is False


def test_survival_live_slot_is_honest() -> None:
    doc = surface()
    assert doc["live_planes"] == [
        "l0-fraggate",
        "local-hash-ledger",
        "local-mesh-dns",
        "cap7-mesh-dns-pair",
    ]
    assert doc["slot_planes"] == ["qnm-peer-bearer", "shuffle-land", "cold-shelf", "hub-https"]
    assert doc["refused_planes"] == ["public-icann"]
    assert doc["independent_live_shelves"] == 0
    assert doc["multi_survival_complete"] is False
    assert doc["copies_one_tunnel"] is True
    assert doc["lie_to_survive"] is False
    assert doc["rewrite_key"] is False
    by_id = {row["id"]: row for row in doc["survival"]}
    assert by_id["l0-fraggate"]["remote_probed"] is False
    assert by_id["cold-shelf"]["doi"] is None
    assert by_id["cold-shelf"]["archive_org"] is False
    assert by_id["shuffle-land"]["called_here"] is False
    assert by_id["hub-https"]["probed"] is False
    assert by_id["public-icann"]["status"] == "REFUSED"


def test_worker_surface_matches_library() -> None:
    raw = subprocess.check_output(
        [
            "node",
            "--input-type=module",
            "-e",
            "import { sidenetSurface } from './workers/download-tracker/src/sidenet.js';"
            "process.stdout.write(JSON.stringify(sidenetSurface()));",
        ],
        cwd=ROOT,
    )
    assert json.loads(raw) == surface()


def test_cli_sidenet_json() -> None:
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        assert main(["sidenet", "--json"]) == 0
    doc = json.loads(buf.getvalue())
    assert doc["naming_lock"]["sidenet"] == "aznet"
    assert doc["icann_registration"] is False
