"""AZN-SIDENET-1.0 — AZnet is the sidenet.

Additive mesh layer beside the public FragGate path. L0 stays the
existing catalog ops and the ``/v1/fraggate`` proxy. This module does
not add a Softwares slug, a second door, a socket, or an ICANN
registration.

Peer movement of a name-sync envelope is a qnm-node bearer. This
process does not open it, so that bearer stays SLOT.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any

from aznet.names.namespace import (
    AZ_DOMAIN_REACH,
    CAP7_FACTORY_LABELS,
    CAP7_FALSE_SITE_LABELS,
)

SPEC = "AZN-SIDENET-1.0"
AUTHOR = "Aziel Eliab"
PRODUCT = "AZnet"
CLIENT_SURFACE = "AZ Browser"
SLUG = "aznet"
QNM_NODE = "https://github.com/AzielEliab/qnm-node"
AZBROWSER = "https://github.com/AzielEliab/azbrowser"

# Public FragGate catalog ops. Same list as the Worker FRAGGATE_LIVE_OPS.
# ``sidenet`` is not one of them.
L0_LIVE_OPS = (
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

_QNM_BEARER = {
    "id": "qnm",
    "status": "SLOT",
    "appropriate": True,
    "via": "qnm-node",
    "cite": QNM_NODE,
    "socket": False,
    "opened_here": False,
    "moves": "AZN-NAME-SYNC-1.0 envelope between peers",
    "note": (
        "Peer movement belongs to qnm-node. This process does not open that bearer. "
        "A cite is not a live session."
    ),
}


class SidenetRefuse(ValueError):
    """A sidenet read tried to claim something this code does not do."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        super().__init__(detail)


def cap7_pairs() -> list[dict[str, Any]]:
    """Local Cap-7 mesh DNS pairs. Not a public DNS zone and not ICANN."""
    by_label = {row["cap7_label"]: row for row in AZ_DOMAIN_REACH}
    rows: list[dict[str, Any]] = []
    for label in CAP7_FACTORY_LABELS:
        false_site = label in CAP7_FALSE_SITE_LABELS
        hub = None if false_site else by_label[label]
        rows.append(
            {
                "label": label,
                "mesh_name": f"{label}.aziel",
                "alias": f"{label}.az",
                "false_site": false_site,
                "role": "false site" if false_site else "real duplication",
                "mirrors": None if hub is None else hub["mirrors"],
                "hub": None if hub is None else hub["hub"],
                "resolves_to_hub": False,
                "public_icann": False,
                "icann_registration_by_this_code": False,
                "local_mesh_dns": "LIVE",
                "public_dns": "SLOT",
                "standard_internet_reaches": False,
                "factory_owned_here": False,
                "hardcoded_update_host": False,
            }
        )
    return rows


def peer_bearer(name: str) -> dict[str, Any]:
    """Return the one appropriate peer bearer, or a refusal.

    qnm stays SLOT. No other name opens a socket.
    """
    key = str(name or "").strip().lower()
    if key == "qnm":
        return dict(_QNM_BEARER)
    return {
        "id": key or "absent",
        "status": "REFUSED",
        "appropriate": False,
        "socket": False,
        "opened_here": False,
        "code": "AZN-BEARER-REFUSED",
        "note": (
            "Peer movement, when a peer moves bytes, is a qnm-node bearer. "
            "This process does not open another bearer."
        ),
    }


def _planes() -> list[dict[str, Any]]:
    return [
        {
            "id": "l0-fraggate",
            "status": "LIVE",
            "means": "path contract in this repository",
            "remote_probed": False,
            "unbroken": True,
            "second_door": False,
            "note": (
                "LIVE means the public FragGate path in this repo is intact: "
                "catalog ops and the /v1/fraggate proxy. This process did not "
                "probe the remote Worker on this call."
            ),
        },
        {
            "id": "local-hash-ledger",
            "status": "LIVE",
            "spec": "AZN-WP-0.1",
            "socket": False,
            "hosts_payloads": False,
            "note": "Device-local hash lattice. Receipts stay on this machine.",
        },
        {
            "id": "local-mesh-dns",
            "status": "LIVE",
            "spec": "AZN-NAME-1.0",
            "public_dns": "SLOT",
            "public_icann": False,
            "socket": False,
            "note": "Local .aziel resolver plus Cap-7 .az aliases. Public DNS is not answered here.",
        },
        {
            "id": "cap7-mesh-dns-pair",
            "status": "LIVE",
            "means": "local pair map",
            "public_dns": "SLOT",
            "public_icann": False,
            "factory_owned_here": False,
            "note": (
                "Seven factory labels paired to mesh names. The MirageGrid factory "
                "is not this repo. Shuffle land is a separate SLOT plane."
            ),
        },
        {
            "id": "qnm-peer-bearer",
            "status": "SLOT",
            "via": "qnm-node",
            "cite": QNM_NODE,
            "socket": False,
            "appropriate": True,
            "note": (
                "Peer movement of a name-sync envelope belongs to qnm-node. "
                "This process does not open that bearer. The cite is not a live session."
            ),
        },
        {
            "id": "shuffle-land",
            "status": "SLOT",
            "owner": "miragegrid",
            "called_here": False,
            "hardcoded_single_host": False,
            "note": (
                "Cap-7 shuffle land is MirageGrid's factory. This repo does not "
                "call it and does not hardcode one Cap-7 host."
            ),
        },
        {
            "id": "cold-shelf",
            "status": "SLOT",
            "independent": False,
            "archive_org": False,
            "codeberg": False,
            "usb": False,
            "doi": None,
            "note": (
                "No independent tip-pack is published by this repository. "
                "GitHub plus this Worker are one product tunnel, not a second shelf."
            ),
        },
        {
            "id": "hub-https",
            "status": "SLOT",
            "means": "not an AZnet survival copy",
            "probed": False,
            "public_icann": False,
            "icann_registration_by_this_code": False,
            "resolves_to_hub_from_cap7": False,
            "note": (
                "The four AZ domain hubs are public HTTPS cites. This process does not "
                "serve them, does not register them, and does not treat them as Cap-7 "
                "answers. SLOT means they are not an AZnet survival copy. It does not "
                "mean those sites were probed."
            ),
        },
        {
            "id": "public-icann",
            "status": "REFUSED",
            "public_icann": False,
            "icann_registration": False,
            "code": "AZN-NO-PUBLIC-ICANN",
            "note": (
                "This code does not register a TLD. .az outside the Cap-7 allowlist "
                "stays normal DNS. Cap-7 is not an ICANN answer."
            ),
        },
    ]


def _guard(doc: dict[str, Any]) -> None:
    if doc.get("public_icann") or doc.get("icann_registration"):
        raise SidenetRefuse("AZN-NO-PUBLIC-ICANN", "sidenet claimed a public ICANN registration")
    if doc.get("second_door") or doc.get("new_software_slug") or not doc.get("softwares_frozen"):
        raise SidenetRefuse("AZN-L0-BROKEN", "sidenet tried to add a door or a Softwares slug")
    if "sidenet" in doc["l0"]["ops"] or doc.get("sidenet_in_l0_ops") or doc.get("sidenet_is_catalog_op"):
        raise SidenetRefuse("AZN-L0-BROKEN", "sidenet was added to the public FragGate op list")
    if doc["l0"]["status"] != "LIVE" or not doc["l0"]["unbroken"] or doc["l0"]["remote_probed"]:
        raise SidenetRefuse("AZN-L0-BROKEN", "L0 path contract was marked probed or broken")
    for row in doc["cap7"]["pairs"]:
        if row["public_icann"] or row["resolves_to_hub"] or row["standard_internet_reaches"]:
            raise SidenetRefuse("AZN-NO-PUBLIC-ICANN", "Cap-7 pair claimed public reach")
        if row["local_mesh_dns"] != "LIVE" or row["public_dns"] != "SLOT":
            raise SidenetRefuse("AZN-LIE", "Cap-7 DNS status does not match this resolver")
    bearers = doc["peer_bearers"]
    if len(bearers) != 1 or bearers[0]["id"] != "qnm" or bearers[0]["status"] != "SLOT" or bearers[0]["socket"]:
        raise SidenetRefuse("AZN-LIE", "qnm peer bearer was marked live or a socket was opened")
    live = {row["id"] for row in doc["survival"] if row["status"] == "LIVE"}
    slot = {row["id"] for row in doc["survival"] if row["status"] == "SLOT"}
    refused = {row["id"] for row in doc["survival"] if row["status"] == "REFUSED"}
    if live != {"l0-fraggate", "local-hash-ledger", "local-mesh-dns", "cap7-mesh-dns-pair"}:
        raise SidenetRefuse("AZN-LIE", "a survival plane was marked LIVE that this code does not run")
    if slot != {"qnm-peer-bearer", "shuffle-land", "cold-shelf", "hub-https"}:
        raise SidenetRefuse("AZN-LIE", "SLOT survival planes drifted")
    if refused != {"public-icann"}:
        raise SidenetRefuse("AZN-NO-PUBLIC-ICANN", "public ICANN was not refused")
    if doc["independent_live_shelves"] != 0 or doc["multi_survival_complete"] or not doc["copies_one_tunnel"]:
        raise SidenetRefuse("AZN-LIE", "multi-survival was marked complete without an independent shelf")
    if doc["lie_to_survive"] or doc["rewrite_key"] or doc["hosts_payloads"] or doc["socket"]:
        raise SidenetRefuse("AZN-LIE", "sidenet claimed a payload, a socket, a rewrite key, or a lie")
    if doc["naming_lock"]["sidenet"] != "aznet" or doc["naming_lock"]["second_sidenet"]:
        raise SidenetRefuse("AZN-NAME-LOCK", "sidenet naming lock is AZnet only")
    if doc["naming_lock"].get("client_surface") != CLIENT_SURFACE or doc["pairing"]["peer_name"] != CLIENT_SURFACE:
        raise SidenetRefuse("AZN-NAME-LOCK", "client surface spelling is AZ Browser")
    if doc["pairing"]["peer"] != "azbrowser" or doc["product"] != PRODUCT:
        raise SidenetRefuse("AZN-NAME-LOCK", "pair slug or AZnet display drifted")
    if "AZBrowser" in str(doc):
        raise SidenetRefuse("AZN-NAME-LOCK", "old client spelling is still on the sidenet map")


def surface() -> dict[str, Any]:
    """Machine map. Statuses are constants. Callers cannot promote a plane."""
    planes = _planes()
    pairs = cap7_pairs()
    doc: dict[str, Any] = {
        "spec": SPEC,
        "author": AUTHOR,
        "product": PRODUCT,
        "slug": SLUG,
        "naming_lock": {
            "sidenet": SLUG,
            "display": PRODUCT,
            "client_surface": CLIENT_SURFACE,
            "second_sidenet": False,
            "phrase": "AZnet is the sidenet",
        },
        "softwares_frozen": True,
        "new_software_slug": False,
        "software_tab_added": False,
        "second_door": False,
        "door": "fraggate",
        "l0": {
            "name": "public FragGate path",
            "status": "LIVE",
            "unbroken": True,
            "remote_probed": False,
            "replaces": False,
            "ops": list(L0_LIVE_OPS),
        },
        "sidenet_in_l0_ops": False,
        "sidenet_is_catalog_op": False,
        "additive": True,
        "layers_replace_l0": False,
        "pairing": {
            "peer": "azbrowser",
            "peer_name": CLIENT_SURFACE,
            "product_name": PRODUCT,
            "url": AZBROWSER,
            "kind": "order and token",
            "products_merged": False,
            "tunnel": False,
            "vpn": False,
            "both_required": True,
            "cap7_mesh_dns": "this map",
        },
        "cap7": {
            "count": len(pairs),
            "local_mesh_dns": "LIVE",
            "public_dns": "SLOT",
            "public_icann": False,
            "icann_registration": False,
            "icann_tld_az": False,
            "standard_internet_reaches_cap7": False,
            "resolves_to_hub": False,
            "factory_owned_here": False,
            "shuffle_land": "SLOT",
            "hardcoded_single_host": False,
            "pairs": pairs,
        },
        "peer_bearers": [dict(_QNM_BEARER)],
        "survival": planes,
        "live_planes": [row["id"] for row in planes if row["status"] == "LIVE"],
        "slot_planes": [row["id"] for row in planes if row["status"] == "SLOT"],
        "refused_planes": [row["id"] for row in planes if row["status"] == "REFUSED"],
        "independent_live_shelves": 0,
        "multi_survival_complete": False,
        "copies_one_tunnel": True,
        "lie_to_survive": False,
        "rewrite_key": False,
        "public_icann": False,
        "icann_registration": False,
        "hosts_payloads": False,
        "socket": False,
        "relay_gossip": False,
        "executes_peer_code": False,
        "qnm": {
            "cite": QNM_NODE,
            "bearer_status": "SLOT",
            "socket_opened_here": False,
        },
        "note": (
            "AZnet is the sidenet. The client surface is AZ Browser. The layer is additive: L0 is the public FragGate "
            "path and stays unbroken. Softwares stays frozen. Cap-7 mesh DNS pairing "
            "is a local map. The qnm peer bearer is SLOT because this process does "
            "not open it. Survival planes are LIVE only where this code runs, and "
            "SLOT where a copy or bearer is not here. There is no public ICANN "
            "registration. One product tunnel is not a finished multi-survival set."
        ),
    }
    _guard(doc)
    return doc
