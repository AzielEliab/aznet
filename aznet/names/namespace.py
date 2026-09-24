"""Mesh namespace for AZN-NAME-1.0.

``.aziel`` is the mesh TLD. ``.az`` is Azerbaijan's ccTLD and stays on
normal DNS except the Cap-7 / AZ.* allowlist copied from aziel-runtime
CAP7-SHUFFLE-1.0. This module does not register anything with ICANN.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from dataclasses import dataclass

from aznet.names.blocklist import BLOCKLIST_VERSION
from aznet.names.wire import (
    AUTHOR,
    CAP_PER_HANDLE,
    DNS_CCTLD_AZ,
    DNS_FALLTHROUGH,
    FED_SPEC,
    HANDLE_BODY_RE,
    MALFORMED,
    MESH_TLD,
    NOT_MESH,
    POW_BITS_MIN,
    RESERVED_LABELS,
    RESERVED_SLOTS,
    SPEC,
    USER_SLOTS,
    WITNESS_AGE_SECONDS,
    WITNESS_K,
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
    text = str(raw or "").strip().rstrip(".")
    if text.startswith("#"):
        body = text[1:]
        suffix = ""
        lower_body = body.lower()
        if lower_body.endswith("." + MESH_TLD):
            suffix = "." + MESH_TLD
            body = body[: -(len(MESH_TLD) + 1)]
        if any(ch.isspace() for ch in body) or "://" in body or "@" in body:
            return ""
        return "#" + body.upper() + suffix
    text = text.lower()
    if any(ch.isspace() for ch in text) or "://" in text or "@" in text:
        return ""
    return text


def _self_cert(body: str) -> str | None:
    if HANDLE_BODY_RE.match(body):
        return "#" + body.upper()
    return None


def classify(raw: str) -> ClassifiedName:
    """Classify a query. Ledger lookups use ``name`` (the canonical key)."""
    query = _clean(raw)
    if not query or any(part == "" for part in query.split(".")):
        return ClassifiedName(str(raw or ""), None, "malformed", None, False, MALFORMED)

    if query.startswith("#"):
        handle = query[1:]
        if handle.endswith("." + MESH_TLD):
            handle = handle[: -(len(MESH_TLD) + 1)]
        owner = _self_cert(handle.lower())
        if owner is None:
            return ClassifiedName(query, None, "malformed", None, False, MALFORMED)
        return ClassifiedName(query, owner[1:].lower() + "." + MESH_TLD, "self_cert", owner, False, None)

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
        owner = _self_cert(label)
        if owner is not None:
            return ClassifiedName(query, query, "self_cert", owner, False, None)
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
            "status": "matched",
            "note": (
                "Name statements use FED-MESH-1.0 kind=name fields from section 5.1 "
                "(handle, prev, prev_record, owner, target, expires). "
                "docs/designs/FED-MESH-1.0.md is on aziel-runtime branch cursor/fed-mesh-e546, not yet on main."
            ),
        },
        {
            "id": "handle-encoding",
            "status": "matched",
            "note": (
                "Handle is '#' plus 11 uppercase Crockford characters from the first 55 bits "
                "of SHA-256 of the raw Ed25519 public key, matching FED-MESH-1.0."
            ),
        },
        {
            "id": "signature-message",
            "status": "matched",
            "note": (
                "Signed bytes are FED-MESH canonicalize(statement) with sig excluded. "
                "No AZN-NAME prefix. sig is unpadded base64url."
            ),
        },
        {
            "id": "mesh-security-constants",
            "status": "matched",
            "note": (
                "POW_BITS_MIN is 8 and WITNESS_K is 2, matching FED-MESH-1.0 section 11. "
                "pow is {nonce, bits, digest} outside the signature. The digest is SHA-256 of "
                "statement_hash, sig, and nonce separated by newlines. The 72-hour window is this "
                "ledger's anchored_at, because a FED-MESH name statement has no timeslate."
            ),
        },
        {
            "id": "slot-split",
            "status": "open",
            "note": (
                "FED-MESH NAME_CAP is still 7 with no reserved split. This library refuses "
                "ae.aziel, corpus.aziel, godlock.aziel, and hdj.aziel, and allows 3 user claims. "
                "The self-certifying name does not use a slot. MirageGrid factory labels stay a "
                "separate layer and are not renamed. This library does not restore or host the mirrors."
            ),
        },
        {
            "id": "name-blocklist",
            "status": "open",
            "note": (
                f"Friendly claims are checked against {BLOCKLIST_VERSION}. It is a label list, "
                "not a classifier. Paraphrases, misspellings, and other languages are misses. "
                "The runtime spec does not publish this list yet."
            ),
        },
        {
            "id": "isolation-record",
            "status": "open",
            "note": (
                "An isolation record is signed by the subject handle. Evidence is a hash, never "
                "the content. An appeal requests a re-check and does not lift isolation. A peer "
                "cannot isolate a handle that never signs the record. Classifiers and publish "
                "checks belong to qnm-node, not this library."
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
                "They are not a write to suite ChainLock CL-WP-0.4. Handle prev and per-name "
                "name_prev sit inside the signed statement."
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
            "id": "first-valid-final",
            "status": "open",
            "note": (
                "This library anchors competing claims and serves the earliest FINAL one. "
                "A relay that implements section 5.1 still answers FED-MESH-NAME-TAKEN for a second "
                "claim and does not store it. Equal anchored_at values are FORK. The ledger is append-only."
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
        "fed_mesh": FED_SPEC,
        "handle": "# + 11 Crockford of SHA-256(public key)",
        "pow_bits_min": POW_BITS_MIN,
        "witness_k": WITNESS_K,
        "witness_age_seconds": WITNESS_AGE_SECONDS,
        "user_slots": USER_SLOTS,
        "reserved_slots": RESERVED_SLOTS,
        "reserved_names": [f"{label}.{MESH_TLD}" for label in RESERVED_LABELS],
        "self_cert_uses_a_slot": False,
        "factory_cap7_separate_layer": True,
        "blocklist_version": BLOCKLIST_VERSION,
        "blocklist_is_a_classifier": False,
        "isolation_lifts_on_appeal": False,
        "classifiers_in_this_library": False,
        "reserved_slot_restore": False,
        "name_kind": "name",
        "finality": "PENDING until this ledger has held the claim for the age window and K distinct handles have witnessed it",
        "age_basis": "local anchored_at from the caller now; not a signed claim time",
        "first_valid_final_claim_wins": True,
        "expired_frees_cap_slot": True,
        "release_frees_cap_slot": True,
        "pending_counts_toward_cap": True,
        "cap_per_handle": CAP_PER_HANDLE,
        "cap7_is_mesh_duplication": True,
        "standard_internet_reaches_cap7": False,
        "internet_reaches_az_domains_via": "hub_https",
        "resolves_to_hub_on_cap7": False,
        "hosts_payloads": False,
        "keys_leave_nodes": False,
        "relay_socket": False,
        "relay_gossip": False,
        "executes_peer_code": False,
        "vouches_change_finality": False,
        "advisories_affect_non_subscribers": False,
        "zero_knowledge": False,
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
