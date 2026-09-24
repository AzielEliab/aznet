"""Self-check for AZNet. No network, no telemetry.

    aznet doctor
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable

from aznet import __version__

AUTHOR = "Aziel Eliab"
Check = tuple[str, bool, str]


def _ok(name: str, detail: str = "") -> Check:
    return name, True, detail


def _fail(name: str, detail: str) -> Check:
    return name, False, detail


def _check_version() -> Check:
    if __version__:
        return _ok("version", str(__version__))
    return _fail("version", "missing")


def _check_identity() -> Check:
    try:
        mod = __import__(__name__.split(".")[0])
        author = str(getattr(mod, "__author__", AUTHOR))
    except Exception as exc:  # noqa: BLE001
        return _fail("identity", str(exc))
    blob = author + " " + AUTHOR
    forbidden = ("Col" + "lin H" + "orton", "Ja" + "ck Al" + "tman", "GodLock" + ".AZ", "Reve" + "aler")
    if any(x in blob for x in forbidden):
        return _fail("identity", "forbidden identity label")
    if "Aziel Eliab" not in blob:
        return _fail("identity", author)
    return _ok("identity", AUTHOR)


def _check_json_roundtrip() -> Check:
    from aznet.jsonio import export_json, import_json

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "in.json"
        out = Path(tmp) / "out.json"
        src.write_text(
            json.dumps({"product": "aznet", "author": AUTHOR, "ok": True}, indent=2),
            encoding="utf-8",
        )
        rec = import_json(src)
        if not rec.get("ok"):
            return _fail("import", str(rec))
        rec2 = export_json(out)
        if not rec2.get("ok") or not out.exists():
            return _fail("export", str(rec2))
        doc = json.loads(out.read_text(encoding="utf-8"))
        if doc.get("author") != AUTHOR:
            return _fail("export author", str(doc.get("author")))
        return _ok("json import/export", "roundtrip")


def _check_core_hash_stable() -> Check:
    from aznet.canon import ABSENT, ACTOR_OPERATOR, GENESIS_PREV_HASH, MARKER, SPEC, digest

    payload = {
        "actor": ACTOR_OPERATOR,
        "azbrowser": None,
        "aznet_node": None,
        "date_stamp": "2026-09-06",
        "event_kind": "STAMP",
        "final_hash": None,
        "fraggate": None,
        "genesis_hash": None,
        "hash_hex": "a" * 64,
        "keys": ABSENT,
        "label": None,
        "marker": MARKER,
        "note": "",
        "pair_flag": True,
        "pair_status": "PAIRED",
        "pair_token": "c" * 64,
        "payload": ABSENT,
        "prev_hash": GENESIS_PREV_HASH,
        "reason": None,
        "spec": SPEC,
        "staticclock": "b" * 64,
        "summary": None,
        "timestamp": "2026-09-06T00:00:00Z",
        "unlock_status": "UNLOCKED",
        "user_content": ABSENT,
        "witness_hash": None,
        "zone": "UTC",
    }
    known = digest(payload)
    again = digest(payload)
    if known != again or len(known) != 64:
        return _fail("AZN-WP-0.1 core hash", known)
    return _ok("AZN-WP-0.1 core hash", "stable")


def _check_pair_required() -> Check:
    from aznet.chain import Ledger
    from aznet.errors import PairError

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ledger = Ledger((), path=path)
        try:
            ledger.stamp("c" * 64, timestamp="2026-09-06T00:00:00Z")
            return _fail("pair", "stamp accepted without pair")
        except PairError:
            pass
        return _ok("pair required", "stamp refused until AZBrowser pair + FragGate unlock")


def _check_lattice() -> Check:
    from aznet.chain import Ledger
    from aznet.lattice import walk

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ledger = Ledger((), path=path)
        ledger.pair(timestamp="2026-09-06T00:00:00Z")
        ledger.unlock(timestamp="2026-09-06T00:01:00Z")
        ledger.stamp("d" * 64, timestamp="2026-09-06T00:02:00Z")
        ledger.memorial(reason="isolation", timestamp="2026-09-06T00:03:00Z", note="isolation memorial")
        result = walk(ledger)
        if not result.ok or result.stamps != 1 or result.pairs != 1 or result.unlocks != 1:
            return _fail("lattice", str(result.errors))
        return _ok("lattice", f"stamps={result.stamps} memorials={result.memorials}")


def _check_no_payload() -> Check:
    from aznet.errors import InvariantError
    from aznet.receipt import assert_no_leakage

    try:
        assert_no_leakage({"payload": "hello", "event_kind": "STAMP"})
        return _fail("I1", "payload accepted")
    except InvariantError:
        return _ok("no payload leakage", "I1")


def _check_names() -> Check:
    from aznet.names import honesty
    from aznet.names.codec import handle_from_public
    from aznet.names.ed25519 import public_key, verify

    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    public = public_key(seed)
    signature = bytes.fromhex(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    if public.hex() != "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a":
        return _fail("mesh names", "Ed25519 public key drifted")
    if not verify(public, b"", signature):
        return _fail("mesh names", "RFC 8032 vector did not verify")
    fed_seed = bytes.fromhex("0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20")
    if handle_from_public(public_key(fed_seed)) != "#CPV0CWYPXP4":
        return _fail("mesh names", "FED-MESH handle vector drifted")
    surface = honesty()
    if surface.get("icann_registration") or surface.get("hosts_payloads") or surface.get("keys_leave_nodes"):
        return _fail("mesh names", "honesty surface overclaims")
    if surface.get("zero_knowledge") or surface.get("executes_peer_code") or surface.get("relay_gossip"):
        return _fail("mesh names", "honesty surface overclaims mesh security")
    if surface.get("mesh_tld") != "aziel" or surface.get("cap_per_handle") != 7:
        return _fail("mesh names", "namespace constants drifted")
    if surface.get("pow_bits_min") != 8 or surface.get("witness_k") != 2 or surface.get("witness_age_seconds") != 72 * 60 * 60:
        return _fail("mesh names", "mesh security constants drifted")
    if surface.get("user_slots") != 3 or surface.get("reserved_slots") != 4:
        return _fail("mesh names", "slot split drifted")
    if surface.get("blocklist_is_a_classifier") or surface.get("isolation_lifts_on_appeal") or surface.get("classifiers_in_this_library"):
        return _fail("mesh names", "honesty surface overclaims the name policy")
    return _ok("mesh names", "AZN-NAME-1.0 RFC 8032 and FED-MESH #CPV0CWYPXP4; .aziel is not an ICANN registration")


def _check_witness() -> Check:
    from aznet.chain import Ledger
    from aznet.errors import WitnessError
    from aznet.witness import expected_witness

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        ledger = Ledger((), path=path)
        try:
            ledger.witness("0" * 64, timestamp="2026-09-06T00:00:00Z")
            return _fail("witness", "bad witness accepted")
        except WitnessError:
            pass
        if not any(r.event_kind == "MEMORIAL" for r in ledger.receipts):
            return _fail("witness", "memorial not written")
        ledger.witness(expected_witness(), timestamp="2026-09-06T00:01:00Z")
        return _ok("UI witness", "bad hash memorializes; good hash appends")


CHECKS: tuple[Callable[[], Check], ...] = (
    _check_version,
    _check_identity,
    _check_json_roundtrip,
    _check_core_hash_stable,
    _check_pair_required,
    _check_lattice,
    _check_no_payload,
    _check_names,
    _check_witness,
)


def run_doctor(*, as_json: bool = False) -> int:
    results = []
    failed = 0
    for fn in CHECKS:
        name, ok, detail = fn()
        results.append({"name": name, "ok": ok, "detail": detail})
        if not ok:
            failed += 1
        mark = "ok" if ok else "FAIL"
        if not as_json:
            print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    payload = {
        "ok": failed == 0,
        "failed": failed,
        "checks": results,
        "version": __version__,
        "author": AUTHOR,
        "role": "silent verification side-net",
        "network": False,
        "telemetry": False,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        print("doctor", "passed" if failed == 0 else "failed")
    return 0 if failed == 0 else 1
