"""Mesh namespace for AZN-NAME-1.0.

``.aziel`` is the mesh TLD. ``.az`` is Azerbaijan's ccTLD and stays on
normal DNS except the Cap-7 / AZ.* allowlist copied from aziel-runtime
CAP7-SHUFFLE-1.0. This module does not register anything with ICANN.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from dataclasses import dataclass

from aznet.names.wire import (
    AUTHOR,
    CAP_PER_HANDLE,
    DNS_CCTLD_AZ,
    DNS_FALLTHROUGH,
    MALFORMED,
    MESH_TLD,
    NOT_MESH,
    SPEC,
)

# Factory SoT labels from aziel-runtime src/cap7-shuffle.js (CAP7_FACTORY_LABELS).
# Runtime mesh_name is ``{label}.az`` with icann_tld_az false. The naming
# standard stores the claim at ``{label}.aziel``. The ``.az`` spelling is
# an allowlisted alias, not a ccTLD answer.
CAP7_FACTORY_LABELS = (
    "azgrid",
    "azbooth",
    "azcloak",
    "azvault",
    "azshift",
    "azflag",
    "azstandby",
)

# Exactly these three are MirageGrid cloak decoys in CAP7-SHUFFLE-1.0.
CAP7_FALSE_SITE_LABELS = ("azbooth", "azflag", "azstandby")

# Four real duplications and the hub each one mirrors. Internet reach is the
# hub HTTPS link (public_icann on that layer). Cap-7 mesh names do not
# resolve to those hubs.
AZ_DOMAIN_REACH = (
    {
        "display_name": "AZ.AzielEliab.AZ",
        "mesh_key": "az.azieleliab.az",
        "cap7_label": "azgrid",
        "mirrors": "azieleliab.com",
        "hub": "https://www.azieleliab.com/",
    },
    {
        "display_name": "AZ.AzielCorpusLibrary.AZ",
        "mesh_key": "az.azielcorpuslibrary.az",
        "cap7_label": "azvault",
        "mirrors": "azielcorpuslibrary.net",
        "hub": "https://www.azielcorpuslibrary.net/",
    },
    {
        "display_name": "AZ.Godlock.AZ",
        "mesh_key": "az.godlock.az",
        "cap7_label": "azcloak",
        "mirrors": "godlock.uk",
        "hub": "https://godlock.uk/",
    },
    {
        "display_name": "AZ.HeDidntJump.AZ",
        "mesh_key": "az.hedidntjump.az",
        "cap7_label": "azshift",
        "mirrors": "hedidntjump.com",
        "hub": "https://www.hedidntjump.com/",
    },
)

_DROP_IN_BY_KEY = {row["mesh_key"]: row for row in AZ_DOMAIN_REACH}
_LABEL_TO_AZIEL = {label: f"{label}.{MESH_TLD}" for label in CAP7_FACTORY_LABELS}


def _label_ok(label: str) -> bool:
    if not label or len(label) > 63:
        return False
    if label[0] == "-" or label[-1] == "-":
        return False
    return all(ch.isdigit() or ("a" <= ch <= "z") or ch == "-" for ch in label)


def _is_hex64(label: str) -> bool:
    if len(label) != 64:
        return False
    return all(ch in "0123456789abcdef" for ch in label)


@dataclass(frozen=True)
class ClassifiedName:
    query: str
    name: str | None
    kind: str
    owner_handle: str | None
    false_site: bool
    code: str | None


def _clean(raw: str) -> str:
    text = str(raw or "").strip().lower().rstrip(".")
    if any(ch.isspace() for ch in text) or "://" in text or "@" in text:
        return ""
    return text


def classify(raw: str) -> ClassifiedName:
    """Classify a query. Ledger lookups use ``name`` (the canonical key)."""
    query = _clean(raw)
    if not query or any(part == "" for part in query.split(".")):
        return ClassifiedName(str(raw or ""), None, "malformed", None, False, MALFORMED)

    if query.startswith("#"):
        handle = query[1:]
        if handle.endswith("." + MESH_TLD):
            handle = handle[: -(len(MESH_TLD) + 1)]
        if not _is_hex64(handle):
            return ClassifiedName(query, None, "malformed", None, False, MALFORMED)
        owner = "#" + handle
        return ClassifiedName(query, f"{handle}.{MESH_TLD}", "self_cert", owner, False, None)

    if query in _DROP_IN_BY_KEY:
        return ClassifiedName(query, query, "az_allow", None, False, None)

    labels = query.split(".")
    if len(labels) == 2 and labels[1] == DNS_CCTLD_AZ and labels[0] in _LABEL_TO_AZIEL:
        label = labels[0]
        return ClassifiedName(
            query,
            _LABEL_TO_AZIEL[label],
            "az_allow",
            None,
            label in CAP7_FALSE_SITE_LABELS,
            None,
        )

    if len(labels) == 2 and labels[1] == MESH_TLD:
        label = labels[0]
        # 64 hex is the raw public key. It is longer than a DNS label on purpose:
        # regular DNS and regular browsers do not carry this name.
        if _is_hex64(label):
            return ClassifiedName(query, query, "self_cert", "#" + label, False, None)
        if not _label_ok(label):
            return ClassifiedName(query, None, "malformed", None, False, MALFORMED)
        false_site = label in CAP7_FALSE_SITE_LABELS
        return ClassifiedName(query, query, "friendly", None, false_site, None)

    if labels[-1] == DNS_CCTLD_AZ:
        return ClassifiedName(query, None, "dns_fallthrough", None, False, DNS_FALLTHROUGH)

    return ClassifiedName(query, None, "not_mesh", None, False, NOT_MESH)


def internet_reach(raw: str) -> dict | None:
    """Cite how the public internet reaches an AZ.* hub, or the Cap-7 mesh layer.

    This is not a mesh resolution. ``resolve`` does not call it for the target.
    Cap-7 entries keep ``resolves_to_hub`` false. AZ-domain entries cite the
    hub HTTPS link and do not claim this process registered ``.az``.
    """
    lowered = str(raw or "").strip().lower().rstrip("/")
    for prefix in ("https://", "http://"):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix) :]
    query = lowered.rstrip(".")
    if not query or " " in query:
        return None
    for row in AZ_DOMAIN_REACH:
        mirrors = row["mirrors"]
        hub_host = row["hub"].split("://", 1)[-1].strip("/")
        aliases = {
            row["mesh_key"],
            row["display_name"].lower(),
            mirrors,
            "www." + mirrors,
            hub_host,
        }
        if query in aliases:
            return {
                "layer": "az_domains",
                "display_name": row["display_name"],
                "mesh_key": row["mesh_key"],
                "cap7_label": row["cap7_label"],
                "mirrors": mirrors,
                "hub": row["hub"],
                "public_icann": True,
                "resolves_to_hub": True,
                "internet_reachable": True,
                "public_reach": "hub_https",
                "icann_tld_az": False,
                "icann_registration_by_this_code": False,
                "mesh_answer": False,
                "note": (
                    "Standard internet reaches this AZ domain through the hub HTTPS link. "
                    "That reach is not a mesh target and not an ICANN .az registration by AZNet."
                ),
            }
    classified = classify(raw if not query.startswith("#") else raw)
    label = None
    if classified.name and classified.name.endswith("." + MESH_TLD):
        head = classified.name[: -(len(MESH_TLD) + 1)]
        if head in _LABEL_TO_AZIEL:
            label = head
    if label is None and query.endswith("." + DNS_CCTLD_AZ):
        head = query[: -(len(DNS_CCTLD_AZ) + 1)]
        if head in _LABEL_TO_AZIEL and "." not in head:
            label = head
    if label is None:
        return None
    return {
        "layer": "cap7",
        "mesh_name": f"{label}.{MESH_TLD}",
        "historical_mesh_name": f"{label}.{DNS_CCTLD_AZ}",
        "false_site": label in CAP7_FALSE_SITE_LABELS,
        "resolves_to_hub": False,
        "standard_internet_reaches_cap7": False,
        "internet_reachable": False,
        "public_icann": False,
        "icann_tld_az": False,
        "icann_registration_by_this_code": False,
        "mesh_answer": True,
        "note": (
            "Cap-7 is the mesh duplication layer. Standard internet does not reach this name. "
            "The .az spelling is an allowlisted alias of the .aziel record, not the Azerbaijan ccTLD."
        ),
    }


def alignment_points() -> list[dict[str, str]]:
    return [
        {
            "id": "FED-MESH-1.0",
            "status": "open",
            "note": (
                "docs/designs/FED-MESH-1.0.md was not on AzielEliab/aziel-runtime main "
                "when this format was written. Wire bytes live in aznet/names/wire.py."
            ),
        },
        {
            "id": "handle-encoding",
            "status": "open",
            "note": (
                "Handle is '#' plus 64 lowercase hex characters of the raw 32-byte Ed25519 "
                "public key. A merged spec may require base32 or a hash of the key."
            ),
        },
        {
            "id": "signature-message",
            "status": "open",
            "note": (
                "Signed bytes are the prefix AZN-NAME-1.0 NUL plus canonical JSON of SIGNED_FIELDS. "
                "FED-MESH may use CBOR or an empty prefix."
            ),
        },
        {
            "id": "temporallock",
            "status": "open",
            "note": (
                "timeslate is a caller-supplied UTC second stamp (YYYY-MM-DDTHH:MM:SSZ). "
                "This library does not call the TemporalLock worker and does not prove clock sync."
            ),
        },
        {
            "id": "chainlock-anchor",
            "status": "open",
            "note": (
                "Anchors are a local append-only hash log (AZN-NAME-ANCHOR-1.0) in the name ledger. "
                "They are not a write to suite ChainLock CL-WP-0.4. Per-name prev and per-handle "
                "handle_prev sit inside the signed record."
            ),
        },
        {
            "id": "cap7-az-spelling",
            "status": "open",
            "note": (
                "aziel-runtime CAP7-SHUFFLE-1.0 mesh_name is {label}.az with icann_tld_az false. "
                "Claims are stored at {label}.aziel. The seven .az names are allowlisted aliases."
            ),
        },
        {
            "id": "late-earlier-claim",
            "status": "open",
            "note": (
                "Earliest timeslate wins among unanchored rivals in one ingest. A later-anchored "
                "claim that is contradicted by an earlier one freezes the name as FORK. "
                "History is not rewritten (NO-REWRITE)."
            ),
        },
        {
            "id": "relay-transport",
            "status": "open",
            "note": (
                "Sync is an in-process AZN-NAME-SYNC-1.0 envelope. qnm-node relay framing is not "
                "specified here. This library does not open a socket."
            ),
        },
        {
            "id": "self-cert-default-target",
            "status": "open",
            "note": (
                "With no anchored update, <handle>.aziel targets the node handle itself. "
                "FED-MESH may require an explicit record before any answer."
            ),
        },
        {
            "id": "qnm-node-id",
            "status": "open",
            "note": (
                "Suite mesh_join node_id is 8–80 chars [a-z0-9._-]. That identifier is not this handle."
            ),
        },
    ]


def honesty() -> dict:
    """Machine surface. Only what this code does."""
    return {
        "spec": SPEC,
        "author": AUTHOR,
        "product": "AZNet",
        "paired_software": "AZBrowser",
        "products_merged": False,
        "pairing": "order and token only",
        "mesh_tld": MESH_TLD,
        "regular_browsers_see_aziel": False,
        "icann_registration": False,
        "icann_tld_az": False,
        "az_cctld": "Azerbaijan",
        "az_default": "normal DNS",
        "az_allowlist_only": True,
        "cap_per_handle": CAP_PER_HANDLE,
        "cap7_is_mesh_duplication": True,
        "standard_internet_reaches_cap7": False,
        "internet_reaches_az_domains_via": "hub_https",
        "resolves_to_hub_on_cap7": False,
        "hosts_payloads": False,
        "keys_leave_nodes": False,
        "relay_socket": False,
        "lamb_lens": ["Service", "Clarity", "Peace"],
        "factory_labels": list(CAP7_FACTORY_LABELS),
        "false_sites": list(CAP7_FALSE_SITE_LABELS),
        "az_domain_hubs": [row["hub"] for row in AZ_DOMAIN_REACH],
        "alignment": alignment_points(),
        "note": (
            "Parallel namespace for AZBrowser and other callers of this resolver. "
            "Regular browsers do not see .aziel names. Nothing here is an ICANN registration. "
            "Internet reach of the AZ.* domains is the four hub sites. Cap-7 is the mesh duplication layer. "
            "AZNet stores name records and hashes, never payloads. Private keys are not an input to the ledger."
        ),
    }
