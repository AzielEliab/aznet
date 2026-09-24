"""AZN-NAME-1.0: self-cert names, Cap-7, forks, signatures, .az allowlist."""

from __future__ import annotations

import json
from pathlib import Path

from aznet.errors import NameRefuse
from aznet.names import honesty, resolve, sign_record
from aznet.names.ed25519 import public_key, sign, verify
from aznet.names.ledger import NameLedger
from aznet.names.namespace import internet_reach
from aznet.names.wire import GENESIS_PREV, SPEC
from aznet.cli import main

VECTORS = Path("tests/vectors/azn-name-1.0.json")
NOW = "2026-09-24T12:00:00Z"


def _seed(n: int) -> bytes:
    return bytes((n + i) % 256 for i in range(32))


def _handle(seed: bytes) -> str:
    return "#" + public_key(seed).hex()


def _claim(
    seed: bytes,
    name: str,
    *,
    prev: str = GENESIS_PREV,
    handle_prev: str = GENESIS_PREV,
    sequence: int = 1,
    timeslate: str = "2026-09-24T00:00:01Z",
    target: str | None = None,
    target_kind: str = "object",
    op: str = "claim",
    successor: str = "",
    renewal: str = "until-release",
    expires_at: str = "",
) -> dict:
    if target is None:
        target = "ab" * 32
    return sign_record(
        seed,
        name=name,
        op=op,
        owner=_handle(seed),
        target=target,
        target_kind=target_kind,
        sequence=sequence,
        prev=prev,
        handle_prev=handle_prev,
        timeslate=timeslate,
        expires_at=expires_at,
        renewal=renewal,
        successor=successor,
    )


def test_rfc8032_vectors() -> None:
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    public = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    signature = (
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    assert public_key(seed).hex() == public
    assert sign(seed, b"").hex() == signature
    assert verify(bytes.fromhex(public), b"", bytes.fromhex(signature))
    seed2 = bytes.fromhex("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb")
    assert public_key(seed2).hex() == "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c"


def test_pinned_name_vector() -> None:
    pinned = json.loads(VECTORS.read_text(encoding="utf-8"))
    seed = bytes.fromhex(pinned["seed_hex"])
    record = sign_record(seed, **{key: pinned["fields"][key] for key in pinned["fields"]})
    assert record["record_hash"] == pinned["record_hash"]
    assert record["signature"] == pinned["signature_hex"]
    assert record["owner"] == pinned["owner"]
    assert record["payload"] == "ABSENT"
    assert record["keys"] == "ABSENT"
    assert "seed" not in record
    again = resolve([record], pinned["fields"]["name"], now=NOW)
    assert again.ok
    assert again.owner == pinned["owner"]
    assert again.target == pinned["fields"]["target"]


def test_self_certifying_name_needs_no_claim() -> None:
    seed = _seed(1)
    handle = _handle(seed)
    bare = resolve(None, handle)
    dotted = resolve(None, f"{handle}.{ 'aziel' }")
    naked = resolve(None, handle[1:] + ".aziel")
    for result in (bare, dotted, naked):
        assert result.ok
        assert result.code == "SELF_CERT"
        assert result.owner == handle
        assert result.target == handle
        assert result.target_kind == "node"
        assert result.resolves_to_hub is False
    other = _handle(_seed(2))
    try:
        sign_record(
            _seed(2),
            name=handle[1:] + ".aziel",
            op="update",
            owner=_handle(_seed(2)),
            target=other,
            target_kind="node",
            sequence=1,
            prev=GENESIS_PREV,
            handle_prev=GENESIS_PREV,
            timeslate="2026-09-24T00:00:01Z",
            renewal="until-release",
            expires_at="",
            successor="",
        )
        raise AssertionError("another key must not sign this self-cert name")
    except NameRefuse as exc:
        assert exc.code == "NOT_OWNER"


def test_self_cert_update_and_fixed_ownership() -> None:
    seed = _seed(3)
    handle = _handle(seed)
    name = handle[1:] + ".aziel"
    target = "cd" * 32
    update = _claim(
        seed,
        name,
        op="update",
        target=target,
        timeslate="2026-09-24T00:00:02Z",
    )
    ledger = NameLedger()
    assert ledger.accept(update).code == "OK"
    result = resolve(ledger, name, now=NOW)
    assert result.ok
    assert result.code == "OK"
    assert result.target == target
    assert result.owner == handle
    release = _claim(
        seed,
        name,
        op="release",
        target="",
        target_kind="none",
        sequence=2,
        prev=update["record_hash"],
        handle_prev=update["record_hash"],
        timeslate="2026-09-24T00:00:03Z",
    )
    assert ledger.accept(release).code == "SELF_CERT_FIXED"
    assert resolve(ledger, name, now=NOW).target == target


def test_first_claim_wins_by_timeslate() -> None:
    first = _claim(_seed(4), "garden.aziel", timeslate="2026-09-24T00:00:01Z", target="11" * 32)
    second = _claim(_seed(5), "garden.aziel", timeslate="2026-09-24T00:00:09Z", target="22" * 32)
    ledger = NameLedger()
    report = ledger.ingest(
        {
            "spec": "AZN-NAME-SYNC-1.0",
            "payload": "ABSENT",
            "keys": "ABSENT",
            "user_content": "ABSENT",
            "records": [second, first],
        }
    )
    codes = [row["code"] for row in report["results"]]
    assert codes == ["LOST_RACE", "OK"]
    result = resolve(ledger, "Garden.AZIEL", now=NOW)
    assert result.ok
    assert result.owner == first["owner"]
    assert result.target == "11" * 32
    assert result.resolves_to_hub is False


def test_equal_timeslate_is_a_fork() -> None:
    left = _claim(_seed(6), "forked.aziel", timeslate="2026-09-24T00:00:04Z", target="33" * 32)
    right = _claim(_seed(7), "forked.aziel", timeslate="2026-09-24T00:00:04Z", target="44" * 32)
    ledger = NameLedger()
    report = ledger.ingest(
        {
            "spec": "AZN-NAME-SYNC-1.0",
            "payload": "ABSENT",
            "keys": "ABSENT",
            "user_content": "ABSENT",
            "records": [left, right],
        }
    )
    assert {row["code"] for row in report["results"]} == {"FORK"}
    result = resolve(ledger, "forked.aziel", now=NOW)
    assert result.ok is False
    assert result.code == "FORK"
    assert result.target is None


def test_late_earlier_claim_freezes_without_rewrite() -> None:
    later = _claim(_seed(8), "late.aziel", timeslate="2026-09-24T00:00:08Z", target="55" * 32)
    earlier = _claim(_seed(9), "late.aziel", timeslate="2026-09-24T00:00:01Z", target="66" * 32)
    ledger = NameLedger()
    assert ledger.accept(later).code == "OK"
    assert ledger.accept(earlier).code == "FORK"
    result = resolve(ledger, "late.aziel", now=NOW)
    assert result.code == "FORK"
    assert result.target is None
    assert later["record_hash"] in {rec["record_hash"] for rec in ledger.records}


def test_cap_seven_per_handle() -> None:
    seed = _seed(10)
    ledger = NameLedger()
    handle_prev = GENESIS_PREV
    anchored = []
    for index in range(7):
        rec = _claim(
            seed,
            f"name{index}.aziel",
            handle_prev=handle_prev,
            timeslate=f"2026-09-24T00:00:0{index + 1}Z",
            target=f"{index:064x}",
        )
        assert ledger.accept(rec).code == "OK"
        anchored.append(rec)
        handle_prev = rec["record_hash"]
    eighth = _claim(
        seed,
        "name7.aziel",
        handle_prev=handle_prev,
        timeslate="2026-09-24T00:00:08Z",
        target="77" * 32,
    )
    assert ledger.accept(eighth).code == "OVER_CAP"
    assert resolve(ledger, "name7.aziel", now=NOW).code == "UNCLAIMED"
    for index in range(7):
        result = resolve(ledger, f"name{index}.aziel", now=NOW)
        assert result.ok
        assert result.owner == _handle(seed)
    self_name = _handle(seed)[1:] + ".aziel"
    update = _claim(
        seed,
        self_name,
        op="update",
        handle_prev=handle_prev,
        sequence=1,
        prev=GENESIS_PREV,
        timeslate="2026-09-24T00:00:09Z",
        target_kind="node",
        target=_handle(seed),
    )
    assert ledger.accept(update).code == "OK"
    assert resolve(ledger, self_name, now=NOW).code == "OK"


def test_transfer_and_release() -> None:
    owner_seed = _seed(11)
    next_seed = _seed(12)
    third_seed = _seed(13)
    ledger = NameLedger()
    claim = _claim(owner_seed, "booth.aziel", timeslate="2026-09-24T00:01:00Z", target="aa" * 32)
    assert ledger.accept(claim).code == "OK"
    transfer = _claim(
        owner_seed,
        "booth.aziel",
        op="transfer",
        sequence=2,
        prev=claim["record_hash"],
        handle_prev=claim["record_hash"],
        timeslate="2026-09-24T00:02:00Z",
        target="aa" * 32,
        successor=_handle(next_seed),
    )
    assert ledger.accept(transfer).code == "OK"
    moved = resolve(ledger, "booth.aziel", now=NOW)
    assert moved.ok
    assert moved.owner == _handle(next_seed)
    assert moved.target == "aa" * 32
    stale = _claim(
        owner_seed,
        "booth.aziel",
        op="update",
        sequence=3,
        prev=transfer["record_hash"],
        handle_prev=transfer["record_hash"],
        timeslate="2026-09-24T00:03:00Z",
        target="bb" * 32,
    )
    assert ledger.accept(stale).code == "NOT_OWNER"
    release = _claim(
        next_seed,
        "booth.aziel",
        op="release",
        target="",
        target_kind="none",
        sequence=3,
        prev=transfer["record_hash"],
        handle_prev=GENESIS_PREV,
        timeslate="2026-09-24T00:04:00Z",
    )
    assert ledger.accept(release).code == "OK"
    assert resolve(ledger, "booth.aziel", now=NOW).code == "REVOKED"
    reclaimed = _claim(
        third_seed,
        "booth.aziel",
        sequence=4,
        prev=release["record_hash"],
        timeslate="2026-09-24T00:05:00Z",
        target="cc" * 32,
    )
    assert ledger.accept(reclaimed).code == "OK"
    final = resolve(ledger, "booth.aziel", now=NOW)
    assert final.owner == _handle(third_seed)
    assert final.target == "cc" * 32


def test_bad_signature_is_refused() -> None:
    record = _claim(_seed(14), "signed.aziel", target="de" * 32)
    broken = dict(record)
    broken["signature"] = ("0" if broken["signature"][0] != "0" else "1") + broken["signature"][1:]
    ledger = NameLedger()
    refused = ledger.accept(broken)
    assert refused.ok is False
    assert refused.code == "BAD_SIGNATURE"
    assert resolve(ledger, "signed.aziel", now=NOW).code == "UNCLAIMED"
    assert ledger.accept(record).code == "OK"
    tampered = dict(record)
    tampered["target"] = "ff" * 32
    assert ledger.accept(tampered).code == "BAD_SIGNATURE"


def test_expiry_and_renewal() -> None:
    seed = _seed(15)
    ledger = NameLedger()
    claim = _claim(
        seed,
        "short.aziel",
        renewal="expiring",
        expires_at="2026-09-24T00:10:00Z",
        timeslate="2026-09-24T00:00:01Z",
    )
    assert ledger.accept(claim).code == "OK"
    assert resolve(ledger, "short.aziel", now="2026-09-24T00:09:59Z").ok
    expired = resolve(ledger, "short.aziel", now="2026-09-24T00:10:00Z")
    assert expired.code == "EXPIRED"
    assert expired.owner == _handle(seed)
    unchecked = resolve(ledger, "short.aziel")
    assert unchecked.ok
    assert unchecked.expiry_checked is False
    renewed = _claim(
        seed,
        "short.aziel",
        op="renew",
        renewal="expiring",
        expires_at="2026-10-01T00:00:00Z",
        sequence=2,
        prev=claim["record_hash"],
        handle_prev=claim["record_hash"],
        timeslate="2026-09-24T00:11:00Z",
        target=claim["target"],
    )
    assert ledger.accept(renewed).code == "OK"
    assert resolve(ledger, "short.aziel", now="2026-09-24T00:12:00Z").ok


def test_az_allowlist_and_dns_fallthrough() -> None:
    seed = _seed(16)
    ledger = NameLedger()
    fall = resolve(ledger, "baku.az", now=NOW)
    assert fall.code == "DNS_FALLTHROUGH"
    assert fall.target is None
    assert fall.dns == "fallthrough"
    assert resolve(ledger, "example.com").code == "NOT_MESH"
    missing = resolve(ledger, "azgrid.az", now=NOW)
    assert missing.code == "UNCLAIMED"
    assert missing.name == "azgrid.aziel"
    assert missing.resolves_to_hub is False
    claim = _claim(seed, "azgrid.aziel", target_kind="node", target=_handle(seed), timeslate="2026-09-24T00:00:03Z")
    assert ledger.accept(claim).code == "OK"
    via_az = resolve(ledger, "AZGRID.AZ", now=NOW)
    via_aziel = resolve(ledger, "azgrid.aziel", now=NOW)
    assert via_az.ok and via_aziel.ok
    assert via_az.target == via_aziel.target == _handle(seed)
    assert via_az.owner == _handle(seed)
    assert via_az.resolves_to_hub is False
    decoy = resolve(ledger, "azbooth.az")
    assert decoy.code == "UNCLAIMED"
    assert decoy.false_site is True
    drop = resolve(ledger, "AZ.AzielEliab.AZ")
    assert drop.code == "UNCLAIMED"
    assert drop.name == "az.azieleliab.az"


def test_non_allowlisted_az_cannot_be_claimed() -> None:
    try:
        _claim(_seed(17), "baku.az")
        raise AssertionError("baku.az must not become a mesh claim")
    except NameRefuse as exc:
        assert exc.code == "DNS_FALLTHROUGH"


def test_drop_in_claim_and_hub_cite_stay_separate() -> None:
    seed = _seed(18)
    ledger = NameLedger()
    claim = _claim(
        seed,
        "az.godlock.az",
        target_kind="ref",
        target="99" * 32,
        timeslate="2026-09-24T00:08:00Z",
    )
    assert ledger.accept(claim).code == "OK"
    result = resolve(ledger, "AZ.Godlock.AZ", now=NOW)
    assert result.ok
    assert result.target == "99" * 32
    assert result.target != "https://godlock.uk/"
    cite = internet_reach("AZ.Godlock.AZ")
    assert cite is not None
    assert cite["hub"] == "https://godlock.uk/"
    assert cite["resolves_to_hub"] is True
    assert cite["mesh_answer"] is False
    assert cite["icann_registration_by_this_code"] is False
    cap7 = internet_reach("azgrid.az")
    assert cap7 is not None
    assert cap7["layer"] == "cap7"
    assert cap7["resolves_to_hub"] is False
    assert cap7["standard_internet_reaches_cap7"] is False
    assert cap7["mesh_name"] == "azgrid.aziel"


def test_sync_refuses_keys_and_roundtrips(tmp_path: Path) -> None:
    path = tmp_path / "names.jsonl"
    ledger = NameLedger(path=path)
    record = _claim(_seed(19), "cache.aziel", target_kind="node", target=_handle(_seed(19)))
    assert ledger.accept(record).code == "OK"
    envelope = ledger.export_sync()
    assert envelope["payload"] == "ABSENT"
    assert envelope["keys"] == "ABSENT"
    blob = json.dumps(envelope)
    assert "private_key" not in blob
    assert record["signature"] in blob
    other = NameLedger()
    report = other.ingest(envelope)
    assert report["ok"]
    assert resolve(other, "cache.aziel", now=NOW).owner == record["owner"]
    leaked = dict(envelope)
    leaked["private_key"] = "nope"
    try:
        other.ingest(leaked)
        raise AssertionError("private keys must not enter sync")
    except NameRefuse as exc:
        assert exc.code == "LEAK"
    assert ledger.verify()["ok"]
    lines = path.read_text(encoding="utf-8").splitlines()
    row = json.loads(lines[0])
    row["record"]["note"] = "tamper"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    assert ledger.verify()["ok"] is False
    try:
        NameLedger.load(path)
        raise AssertionError("tampered anchor must not load")
    except NameRefuse as exc:
        assert exc.code in {"MALFORMED", "BAD_SIGNATURE", "BAD_CHAIN"}


def test_honesty_machine_surface() -> None:
    surface = honesty()
    assert surface["spec"] == SPEC
    assert surface["author"] == "Aziel Eliab"
    assert surface["mesh_tld"] == "aziel"
    assert surface["regular_browsers_see_aziel"] is False
    assert surface["icann_registration"] is False
    assert surface["icann_tld_az"] is False
    assert surface["hosts_payloads"] is False
    assert surface["keys_leave_nodes"] is False
    assert surface["cap_per_handle"] == 7
    assert surface["standard_internet_reaches_cap7"] is False
    assert surface["products_merged"] is False
    assert "azgrid" in surface["factory_labels"]
    assert len(surface["alignment"]) >= 8


def test_cli_resolve_fallthrough_and_names(tmp_path: Path, capsys) -> None:
    assert main(["names"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["icann_registration"] is False
    assert main(["resolve", "baku.az"]) == 1
    refused = json.loads(capsys.readouterr().out)
    assert refused["code"] == "DNS_FALLTHROUGH"
    handle = _handle(_seed(20))
    assert main(["resolve", handle[1:] + ".aziel"]) == 0
    owned = json.loads(capsys.readouterr().out)
    assert owned["code"] == "SELF_CERT"
    assert owned["owner"] == handle
