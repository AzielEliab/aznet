"""AZN-NAME-1.0 on the FED-MESH name wire, plus mesh-security rules."""

from __future__ import annotations

import json
from pathlib import Path

from aznet.cli import main
from aznet.errors import NameRefuse
from aznet.names import honesty, resolve, sign_advisory, sign_appeal, sign_isolation, sign_record, sign_vouch, sign_witness
from aznet.names.codec import b64url_decode, canonicalize, handle_from_public, statement_hash
from aznet.names.ed25519 import public_key, sign, verify
from aznet.names.blocklist import BLOCKLIST_VERSION, name_blocked
from aznet.names.ledger import NameLedger
from aznet.names.namespace import internet_reach
from aznet.names.record import prepare_statement
from aznet.names.wire import FED_SPEC, GENESIS_PREV, POW_BITS_MIN, SPEC, WITNESS_K

VECTORS = Path("tests/vectors/azn-name-1.0.json")
OPENED = "2026-09-21T12:00:00Z"
LATER = "2026-09-21T13:00:00Z"
BEFORE = "2026-09-24T11:59:59Z"
FINAL_AT = "2026-09-24T12:00:00Z"
FINAL_LATER = "2026-09-24T13:00:00Z"
OBJECT = "ab" * 32


def _seed(n: int) -> bytes:
    return bytes((n * 7 + i * 3) % 256 for i in range(32))


def _handle(seed: bytes) -> str:
    return handle_from_public(public_key(seed))


def _claim(seed: bytes, name: str, **fields: object) -> dict:
    body = {
        "name": name,
        "op": "claim",
        "target": OBJECT,
        "target_kind": "hash",
        "seq": 1,
        "prev": GENESIS_PREV,
        "prev_record": GENESIS_PREV,
    }
    body.update(fields)
    return sign_record(seed, **body)


def _witness(seed: bytes, claim: dict, *, seq: int = 1, prev: str = GENESIS_PREV) -> dict:
    return sign_witness(
        seed,
        seq=seq,
        prev=prev,
        subject_hash=claim["record_hash"],
    )


def _finalize(ledger: NameLedger, claim: dict, witnesses: list[bytes], *, opened: str = OPENED) -> None:
    assert ledger.accept(claim, now=opened).code in {"OK", "IDEMPOTENT"}
    for seed in witnesses:
        assert ledger.accept(_witness(seed, claim), now=opened).code == "OK"


def test_rfc8032_and_fed_mesh_vectors() -> None:
    seed = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
    public = "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
    signature = (
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    assert public_key(seed).hex() == public
    assert sign(seed, b"").hex() == signature
    assert verify(bytes.fromhex(public), b"", bytes.fromhex(signature))

    pinned = json.loads(VECTORS.read_text(encoding="utf-8"))
    fed_seed = bytes.fromhex(pinned["fed_mesh"]["seed_hex"])
    assert handle_from_public(public_key(fed_seed)) == pinned["fed_mesh"]["handle"]
    name = pinned["fed_mesh"]["name_claim"]
    body = {key: name[key] for key in name if key != "sig"}
    assert statement_hash(body) == pinned["fed_mesh"]["name_claim_statement_hash"]
    assert verify(
        b64url_decode(name["public_key"]),
        canonicalize(body).encode("utf-8"),
        b64url_decode(name["sig"]),
    )
    prepared = prepare_statement(name)
    assert prepared["record_hash"] == pinned["fed_mesh"]["name_claim_statement_hash"]
    assert prepared["v"] == FED_SPEC
    ref = pinned["fed_mesh"]["ref_update"]
    ref_body = {key: ref[key] for key in ref if key != "sig"}
    assert statement_hash(ref_body) == pinned["fed_mesh"]["ref_statement_hash"]

    local = pinned["friendly_claim"]
    record = sign_record(bytes.fromhex(local["seed_hex"]), **local["fields"])
    assert record["record_hash"] == local["record_hash"]
    assert record["sig"] == local["sig"]
    assert record["pow"] == local["pow"]
    assert record["handle"] == local["handle"]
    assert "seed" not in record
    assert record["pow"]["bits"] >= 8
    again = prepare_statement(record)
    assert again["record_hash"] == local["record_hash"]
    stamped = dict(name)
    stamped["pow"] = pinned["fed_mesh"]["name_claim_pow"]
    anchored = prepare_statement(stamped)
    assert anchored["record_hash"] == pinned["fed_mesh"]["name_claim_statement_hash"]
    assert anchored["pow"]["digest"] == pinned["fed_mesh"]["name_claim_pow"]["digest"]


def test_self_certifying_name_needs_no_claim() -> None:
    handle = _handle(_seed(1))
    bare = resolve(None, handle)
    dotted = resolve(None, handle + ".aziel")
    naked = resolve(None, handle[1:].lower() + ".aziel")
    for result in (bare, dotted, naked):
        assert result.ok
        assert result.code == "SELF_CERT"
        assert result.owner == handle
        assert result.target == handle
        assert result.target_kind == "handle"
        assert result.key_checked is False
        assert result.finality == "FINAL"
        assert result.resolves_to_hub is False
    try:
        sign_record(
            _seed(2),
            name=handle[1:].lower() + ".aziel",
            op="update",
            target=handle,
            target_kind="handle",
            seq=1,
        )
        raise AssertionError("another key must not sign this self-cert name")
    except NameRefuse as exc:
        assert exc.code == "NOT_OWNER"


def test_self_cert_update_and_fixed_ownership() -> None:
    seed = _seed(3)
    handle = _handle(seed)
    name = handle[1:].lower() + ".aziel"
    target = "cd" * 32
    update = sign_record(
        seed,
        name=name,
        op="update",
        target=target,
        target_kind="hash",
        seq=1,
        timeslate="unused",
    )
    ledger = NameLedger()
    assert ledger.accept(update, now=OPENED).code == "OK"
    result = resolve(ledger, name, now=FINAL_AT)
    assert result.ok
    assert result.code == "OK"
    assert result.finality == "FINAL"
    assert result.witnesses == 0
    assert result.target == target
    assert result.key_checked is True
    try:
        sign_record(seed, name=name, op="release", seq=2, prev=update["record_hash"], prev_record=update["record_hash"])
        raise AssertionError("self-cert release is fixed")
    except NameRefuse as exc:
        assert exc.code == "SELF_CERT_FIXED"
    assert resolve(ledger, name, now=FINAL_AT).target == target


def test_pending_does_not_beat_final_and_earlier_final_wins() -> None:
    early = _claim(_seed(4), "garden.aziel", target="11" * 32)
    late = _claim(_seed(5), "garden.aziel", target="22" * 32)
    ledger = NameLedger()
    assert ledger.accept(early, now=OPENED).code == "OK"
    assert ledger.accept(late, now=LATER).code == "OK"
    for seed in (_seed(6), _seed(7)):
        assert ledger.accept(_witness(seed, late), now=LATER).code == "OK"
    pending = resolve(ledger, "Garden.AZIEL", now=FINAL_AT)
    assert pending.ok is False
    assert pending.code == "PENDING"
    assert pending.target == "11" * 32
    assert pending.owner == early["handle"]
    served = resolve(ledger, "garden.aziel", now=FINAL_LATER)
    assert served.ok
    assert served.code == "OK"
    assert served.finality == "FINAL"
    assert served.witnesses == 2
    assert served.target == "22" * 32
    assert served.owner == late["handle"]
    for seed in (_seed(9), _seed(10)):
        assert ledger.accept(_witness(seed, early), now=FINAL_LATER).code == "OK"
    winner = resolve(ledger, "garden.aziel", now=FINAL_LATER)
    assert winner.ok
    assert winner.target == "11" * 32
    assert winner.owner == early["handle"]
    assert winner.resolves_to_hub is False


def test_equal_anchor_time_is_a_fork() -> None:
    left = _claim(_seed(12), "forked.aziel", target="33" * 32)
    right = _claim(_seed(13), "forked.aziel", target="44" * 32)
    ledger = NameLedger()
    report = ledger.ingest(
        {
            "spec": "AZN-NAME-SYNC-1.0",
            "payload": "ABSENT",
            "keys": "ABSENT",
            "user_content": "ABSENT",
            "records": [left, right],
        },
        now=OPENED,
    )
    assert [row["code"] for row in report["results"]] == ["OK", "OK"]
    witnesses = [_seed(14), _seed(15)]
    progress = {id(seed): GENESIS_PREV for seed in witnesses}
    seq = {id(seed): 1 for seed in witnesses}
    for claim in (left, right):
        for seed in witnesses:
            witnessed = _witness(seed, claim, seq=seq[id(seed)], prev=progress[id(seed)])
            assert ledger.accept(witnessed, now=OPENED).code == "OK"
            progress[id(seed)] = witnessed["record_hash"]
            seq[id(seed)] += 1
    result = resolve(ledger, "forked.aziel", now=FINAL_AT)
    assert result.ok is False
    assert result.code == "FORK"
    assert result.target is None


def test_one_witness_and_short_age_stay_pending() -> None:
    claim = _claim(_seed(17), "wait.aziel")
    ledger = NameLedger()
    assert ledger.accept(claim, now=OPENED).code == "OK"
    assert ledger.accept(_witness(_seed(18), claim), now=OPENED).code == "OK"
    one = resolve(ledger, "wait.aziel", now=FINAL_AT)
    assert one.code == "PENDING"
    assert one.witnesses == 1
    assert ledger.accept(_witness(_seed(19), claim), now=OPENED).code == "OK"
    early = resolve(ledger, "wait.aziel", now=BEFORE)
    assert early.code == "PENDING"
    assert early.witnesses == 2
    assert early.target == OBJECT
    ready = resolve(ledger, "wait.aziel", now=FINAL_AT)
    assert ready.ok
    assert ready.witnesses == WITNESS_K


def test_self_witness_and_weak_proof_of_work_refused() -> None:
    seed = _seed(21)
    claim = _claim(seed, "sybil.aziel")
    ledger = NameLedger()
    assert ledger.accept(claim, now=OPENED).code == "OK"
    witnessed = sign_witness(seed, seq=2, prev=claim["record_hash"], subject_hash=claim["record_hash"])
    refused_self = ledger.accept(witnessed, now=OPENED)
    assert refused_self.code == "EQUIVOCATION"
    assert ledger.is_equivocating(claim["handle"]) is False
    try:
        _claim(seed, "sybil-weak.aziel", pow_bits=3)
        raise AssertionError("pow below the minimum must fail")
    except NameRefuse as exc:
        assert exc.code == "POW_WEAK"
    broken = dict(claim)
    broken["pow"] = {"nonce": "0", "bits": 8, "digest": "0" * 64}
    refused = NameLedger().accept(broken, now=OPENED)
    assert refused.ok is False
    assert refused.code == "POW_FAIL"
    assert resolve(ledger, "sybil.aziel", now=FINAL_AT).code == "PENDING"


def test_sybil_flood_cannot_pass_cap_or_skip_finality() -> None:
    owner = _seed(22)
    ledger = NameLedger()
    previous = GENESIS_PREV
    for index in range(1, 4):
        claim = _claim(owner, f"slot{index}.aziel", seq=index, prev=previous)
        assert ledger.accept(claim, now=OPENED).code == "OK"
        previous = claim["record_hash"]
    fourth = _claim(owner, "slot4.aziel", seq=4, prev=previous)
    assert ledger.accept(fourth, now=OPENED).code == "OVER_CAP"
    flood = _claim(_seed(23), "slot1.aziel")
    assert ledger.accept(flood, now=LATER).code == "OK"
    assert resolve(ledger, "slot1.aziel", now=FINAL_LATER).code == "PENDING"
    _finalize(ledger, flood, [_seed(24), _seed(25)], opened=LATER)
    # The earlier pending claim still has no witnesses, so the later FINAL is served.
    served = resolve(ledger, "slot1.aziel", now=FINAL_LATER)
    assert served.ok
    assert served.owner == flood["handle"]


def test_equivocation_refuses_the_handle_only() -> None:
    seed = _seed(30)
    first = _claim(seed, "left.aziel", target="aa" * 32)
    second = _claim(seed, "right.aziel", target="bb" * 32)
    other = _claim(_seed(31), "right.aziel", target="cc" * 32)
    ledger = NameLedger()
    assert ledger.accept(first, now=OPENED).code == "OK"
    conflict = ledger.accept(second, now=OPENED)
    assert conflict.code == "EQUIVOCATION"
    assert ledger.is_equivocating(first["handle"])
    hidden = resolve(ledger, "left.aziel", now=FINAL_AT)
    assert hidden.code == "EQUIVOCATION"
    assert hidden.target is None
    _finalize(ledger, other, [_seed(32), _seed(33)], opened=LATER)
    shown = resolve(ledger, "right.aziel", now=FINAL_LATER)
    assert shown.ok
    assert shown.owner == other["handle"]
    assert shown.target == "cc" * 32


def test_rollback_and_bad_signature_refused() -> None:
    seed = _seed(35)
    ledger = NameLedger()
    claim = _claim(seed, "chain.aziel")
    assert ledger.accept(claim, now=OPENED).code == "OK"
    update = sign_record(
        seed,
        name="chain.aziel",
        op="update",
        target="dd" * 32,
        target_kind="hash",
        seq=2,
        prev=claim["record_hash"],
        prev_record=claim["record_hash"],
    )
    assert ledger.accept(update, now=LATER).code == "OK"
    third = sign_record(
        seed,
        name="chain.aziel",
        op="update",
        target="ee" * 32,
        target_kind="hash",
        seq=3,
        prev=update["record_hash"],
        prev_record=update["record_hash"],
    )
    assert ledger.accept(third, now="2026-09-21T14:00:00Z").code == "OK"
    stale = sign_record(
        seed,
        name="chain.aziel",
        op="update",
        target="ff" * 32,
        target_kind="hash",
        seq=2,
        prev=claim["record_hash"],
        prev_record=claim["record_hash"],
    )
    assert ledger.accept(stale, now="2026-09-21T15:00:00Z").code == "ROLLBACK"
    assert ledger.is_equivocating(_handle(seed))
    older = sign_record(
        _seed(36),
        name="rolled.aziel",
        op="claim",
        target=OBJECT,
        target_kind="hash",
        seq=2,
        prev=GENESIS_PREV,
    )
    assert ledger.accept(older, now=OPENED).code == "BAD_SEQUENCE"
    rolled = _claim(_seed(36), "rolled.aziel")
    assert ledger.accept(rolled, now=OPENED).code == "OK"
    replay = sign_record(
        _seed(36),
        name="rolled.aziel",
        op="update",
        target="ab" * 32,
        target_kind="hash",
        seq=1,
        prev="22" * 32,
        prev_record=rolled["record_hash"],
    )
    assert ledger.accept(replay, now=LATER).code == "ROLLBACK"
    poisoned = dict(claim)
    poisoned["sig"] = ("A" if poisoned["sig"][0] != "A" else "B") + poisoned["sig"][1:]
    assert ledger.accept(poisoned, now=OPENED).code == "BAD_SIGNATURE"
    tampered = dict(third)
    tampered["target"] = {"type": "hash", "value": "ff" * 32}
    assert ledger.accept(tampered, now=OPENED).code == "BAD_SIGNATURE"
    assert resolve(ledger, "missing-poison.aziel", now=FINAL_AT).code == "UNCLAIMED"


def test_transfer_release_expiry_and_cap_slot() -> None:
    owner = _seed(40)
    nxt = _seed(41)
    ledger = NameLedger()
    claim = _claim(owner, "booth.aziel", target="99" * 32, expires_at="2026-09-24T00:00:00Z")
    _finalize(ledger, claim, [_seed(42), _seed(43)])
    moved = sign_record(
        owner,
        name="booth.aziel",
        op="transfer",
        successor=_handle(nxt),
        target="99" * 32,
        target_kind="hash",
        seq=2,
        prev=claim["record_hash"],
        prev_record=claim["record_hash"],
    )
    assert ledger.accept(moved, now=LATER).code == "OK"
    result = resolve(ledger, "booth.aziel", now=FINAL_LATER)
    assert result.ok
    assert result.owner == _handle(nxt)
    assert result.target == "99" * 32
    released = sign_record(
        nxt,
        name="booth.aziel",
        op="release",
        seq=1,
        prev_record=moved["record_hash"],
    )
    assert ledger.accept(released, now="2026-09-21T16:00:00Z").code == "OK"
    assert resolve(ledger, "booth.aziel", now=FINAL_LATER).code == "REVOKED"

    expiring = _claim(_seed(45), "short.aziel", expires_at="2026-09-25T12:00:00Z")
    _finalize(ledger, expiring, [_seed(46), _seed(47)])
    assert resolve(ledger, "short.aziel", now=FINAL_AT).ok
    expired = resolve(ledger, "short.aziel", now="2026-09-25T12:00:00Z")
    assert expired.code == "EXPIRED"
    assert expired.expiry_checked is True
    unchecked = resolve(ledger, "short.aziel")
    assert unchecked.code == "PENDING"
    assert unchecked.expiry_checked is False


def test_release_and_expiry_free_a_cap_slot() -> None:
    owner = _seed(50)
    ledger = NameLedger()
    previous = GENESIS_PREV
    first = None
    for index in range(1, 4):
        kwargs = {"seq": index, "prev": previous}
        if index == 1:
            kwargs["expires_at"] = "2026-09-22T00:00:00Z"
        claim = _claim(owner, f"cap{index}.aziel", **kwargs)
        assert ledger.accept(claim, now=OPENED).code == "OK"
        if first is None:
            first = claim
        previous = claim["record_hash"]
    blocked = _claim(owner, "cap4.aziel", seq=4, prev=previous)
    assert ledger.accept(blocked, now=OPENED).code == "OVER_CAP"
    assert ledger.accept(blocked, now="2026-09-22T00:00:01Z").code == "OK"
    fresh = NameLedger()
    previous = GENESIS_PREV
    for index in range(1, 4):
        claim = _claim(_seed(51), f"rel{index}.aziel", seq=index, prev=previous)
        assert fresh.accept(claim, now=OPENED).code == "OK"
        previous = claim["record_hash"]
    opening = _claim(_seed(51), "rel4.aziel", seq=4, prev=previous)
    assert fresh.accept(opening, now=OPENED).code == "OVER_CAP"
    rel1 = next(rec for rec in fresh.records if rec.get("name") == "rel1.aziel")
    release = sign_record(
        _seed(51),
        name="rel1.aziel",
        op="release",
        seq=4,
        prev=previous,
        prev_record=rel1["record_hash"],
    )
    assert fresh.accept(release, now=LATER).code == "OK"
    opening = _claim(_seed(51), "rel4.aziel", seq=5, prev=release["record_hash"])
    assert fresh.accept(opening, now=LATER).code == "OK"


def test_vouch_does_not_change_finality_and_advisory_is_local() -> None:
    claim = _claim(_seed(60), "trust.aziel")
    friend = _seed(61)
    ledger = NameLedger()
    assert ledger.accept(claim, now=OPENED).code == "OK"
    vouch = sign_vouch(
        friend,
        seq=1,
        subject=claim["handle"],
        subject_public_key=claim["public_key"],
    )
    assert ledger.accept(vouch, now=OPENED).code == "OK"
    view = ledger.trust_view(claim["handle"])
    assert view["vouches_change_finality"] is False
    assert view["vouches"][0]["by"] == _handle(friend)
    assert "score" not in view
    assert resolve(ledger, "trust.aziel", now=FINAL_AT).code == "PENDING"
    try:
        sign_advisory(
            friend,
            seq=2,
            prev=vouch["record_hash"],
            subject=claim["handle"],
            note="look twice",
            score=9,
        )
        raise AssertionError("advisory notes have no score")
    except NameRefuse as exc:
        assert exc.code == "MALFORMED"
    advisory = sign_advisory(
        friend,
        seq=2,
        prev=vouch["record_hash"],
        subject=claim["handle"],
        note="look twice",
    )
    assert ledger.accept(advisory, now=OPENED).code == "OK"
    quiet = resolve(ledger, "trust.aziel", now=FINAL_AT)
    assert quiet.advisories == ()
    assert quiet.code == "PENDING"
    ledger.subscribe(_handle(friend))
    noted = resolve(ledger, "trust.aziel", now=FINAL_AT)
    assert noted.code == "PENDING"
    assert noted.advisories[0]["note"] == "look twice"
    assert "score" not in noted.advisories[0]


def test_az_allowlist_and_dns_fallthrough() -> None:
    ledger = NameLedger()
    fall = resolve(ledger, "baku.az", now=FINAL_AT)
    assert fall.code == "DNS_FALLTHROUGH"
    assert fall.target is None
    assert fall.dns == "fallthrough"
    assert resolve(ledger, "example.com").code == "NOT_MESH"
    missing = resolve(ledger, "azgrid.az", now=FINAL_AT)
    assert missing.code == "UNCLAIMED"
    assert missing.name == "azgrid.aziel"
    assert missing.resolves_to_hub is False
    try:
        _claim(_seed(70), "azgrid.aziel", target=_handle(_seed(70)), target_kind="handle")
        raise AssertionError("azgrid.aziel is a factory label")
    except NameRefuse as exc:
        assert exc.code == "RESERVED"
    try:
        _claim(_seed(70), "azgrid.az")
        raise AssertionError("the .az alias is the same reserved name")
    except NameRefuse as exc:
        assert exc.code == "RESERVED"
    assert resolve(ledger, "AZGRID.AZ", now=FINAL_AT).code == "UNCLAIMED"
    assert resolve(ledger, "azgrid.aziel", now=FINAL_AT).code == "UNCLAIMED"
    decoy = resolve(ledger, "azbooth.az")
    assert decoy.code == "UNCLAIMED"
    assert decoy.false_site is True
    drop = resolve(ledger, "AZ.AzielEliab.AZ")
    assert drop.code == "UNCLAIMED"
    assert drop.name == "az.azieleliab.az"
    assert drop.target is None
    try:
        _claim(_seed(74), "baku.az")
        raise AssertionError("baku.az must not become a mesh claim")
    except NameRefuse as exc:
        assert exc.code == "DNS_FALLTHROUGH"
    try:
        _claim(_seed(74), "az.godlock.az")
        raise AssertionError("AZ.* cites are not name records")
    except NameRefuse as exc:
        assert exc.code == "NOT_MESH"
    cite = internet_reach("AZ.Godlock.AZ")
    assert cite is not None
    assert cite["hub"] == "https://godlock.uk/"
    assert cite["resolves_to_hub"] is True
    assert cite["mesh_answer"] is False
    cap7 = internet_reach("azgrid.az")
    assert cap7 is not None
    assert cap7["resolves_to_hub"] is False
    assert cap7["standard_internet_reaches_cap7"] is False
    assert cap7["mesh_name"] == "azgrid.aziel"


def test_sync_refuses_keys_and_keeps_subscriptions_local(tmp_path: Path) -> None:
    path = tmp_path / "names.jsonl"
    ledger = NameLedger(path=path)
    record = _claim(_seed(80), "cache.aziel", target=_handle(_seed(80)), target_kind="handle")
    assert ledger.accept(record, now=OPENED).code == "OK"
    ledger.subscribe(_handle(_seed(81)))
    envelope = ledger.export_sync()
    assert envelope["payload"] == "ABSENT"
    assert envelope["keys"] == "ABSENT"
    blob = json.dumps(envelope)
    assert "private_key" not in blob
    assert record["sig"] in blob
    assert _handle(_seed(81)) not in blob
    other = NameLedger()
    report = other.ingest(envelope, now=OPENED)
    assert report["ok"]
    synced = resolve(other, "cache.aziel", now=OPENED)
    assert synced.code == "PENDING"
    assert synced.owner == record["handle"]
    assert other.subscriptions() == ()
    leaked = dict(envelope)
    leaked["private_key"] = "nope"
    try:
        other.ingest(leaked)
        raise AssertionError("private keys must not enter sync")
    except NameRefuse as exc:
        assert exc.code == "LEAK"
    smuggled = dict(record)
    smuggled["code"] = "print(1)"
    assert ledger.accept(smuggled, now=OPENED).code == "NO_EXEC"
    assert ledger.verify()["ok"]
    lines = path.read_text(encoding="utf-8").splitlines()
    row = json.loads(lines[0])
    row["record"]["name"] = "tampered.aziel"
    path.write_text("\n".join([json.dumps(row), *lines[1:]]) + "\n", encoding="utf-8")
    assert ledger.verify()["ok"] is False


def test_honesty_machine_surface() -> None:
    surface = honesty()
    assert surface["spec"] == SPEC
    assert surface["author"] == "Aziel Eliab"
    assert surface["mesh_tld"] == "aziel"
    assert surface["regular_browsers_see_aziel"] is False
    assert surface["icann_registration"] is False
    assert surface["hosts_payloads"] is False
    assert surface["keys_leave_nodes"] is False
    assert surface["cap_per_handle"] == 7
    assert surface["user_slots"] == 3
    assert surface["reserved_slots"] == 4
    assert surface["reserved_names"] == ["ae.aziel", "corpus.aziel", "godlock.aziel", "hdj.aziel"]
    assert surface["self_cert_uses_a_slot"] is False
    assert surface["factory_cap7_separate_layer"] is True
    assert surface["pow_bits_min"] == POW_BITS_MIN == 8
    assert surface["witness_k"] == WITNESS_K == 2
    assert surface["blocklist_version"] == "FED-MESH-BLOCKLIST-1"
    assert surface["blocklist_is_a_classifier"] is False
    assert surface["isolation_lifts_on_appeal"] is False
    assert surface["classifiers_in_this_library"] is False
    assert surface["reserved_slot_restore"] is False
    assert surface["first_valid_final_claim_wins"] is True
    assert surface["zero_knowledge"] is False
    assert surface["executes_peer_code"] is False
    assert surface["vouches_change_finality"] is False
    assert surface["relay_gossip"] is False
    assert surface["products_merged"] is False
    assert "azgrid" in surface["factory_labels"]


def test_blocklist_fold_matches_runtime() -> None:
    """Shared with aziel-runtime nameBlockHit: separators and digit lookalikes."""
    for label in ("child.porn", "child-porn", "ch1ldp0rn", "child.porn.aziel", "child-porn.aziel", "ch1ldp0rn.aziel"):
        assert name_blocked(label) == BLOCKLIST_VERSION
    for label in ("sussex", "analysis", "essex", "sussex.aziel", "analysis.aziel", "child", "childcare"):
        assert name_blocked(label) is None
    owner = _seed(89)
    for label in ("child-porn.aziel", "ch1ldp0rn.aziel"):
        try:
            _claim(owner, label)
            raise AssertionError(f"{label} must be refused")
        except NameRefuse as exc:
            assert exc.code == "POLICY"
            assert "porn" not in str(exc)
            assert "child" not in str(exc)


def test_reserved_slots_blocklist_and_self_cert_outside_the_cap() -> None:
    owner = _seed(90)
    ledger = NameLedger()
    for label in ("ae", "corpus", "godlock", "hdj", "azgrid", "azbooth", "azcloak", "azvault", "azshift", "azflag", "azstandby"):
        try:
            _claim(owner, f"{label}.aziel")
            raise AssertionError(f"{label}.aziel is reserved")
        except NameRefuse as exc:
            assert exc.code == "RESERVED"
    for blocked in ("porn.aziel", "my-porn-site.aziel", "csam.aziel", "xxx.aziel", "nazism.aziel", "whitepower.aziel", "kkk.aziel", "childsex.aziel"):
        try:
            _claim(owner, blocked)
            raise AssertionError(f"{blocked} matches the blocklist")
        except NameRefuse as exc:
            assert exc.code == "POLICY"
            assert "porn" not in str(exc)
            assert "csam" not in str(exc)
    assert _claim(owner, "analysis.aziel")["name"] == "analysis.aziel"
    assert _claim(owner, "sussex.aziel")["name"] == "sussex.aziel"
    assert _claim(owner, "garden.aziel")["name"] == "garden.aziel"
    previous = GENESIS_PREV
    for index, label in enumerate(("one", "two", "three"), start=1):
        claim = _claim(owner, f"{label}.aziel", seq=index, prev=previous)
        assert ledger.accept(claim, now=OPENED).code == "OK"
        previous = claim["record_hash"]
    extra = _claim(owner, "four.aziel", seq=4, prev=previous)
    assert ledger.accept(extra, now=OPENED).code == "OVER_CAP"
    handle = _handle(owner)
    update = sign_record(
        owner,
        name=handle[1:].lower() + ".aziel",
        op="update",
        target=OBJECT,
        target_kind="hash",
        seq=4,
        prev=previous,
    )
    assert ledger.accept(update, now=OPENED).code == "OK"
    served = resolve(ledger, handle[1:].lower() + ".aziel", now=OPENED)
    assert served.ok
    assert served.finality == "FINAL"
    assert served.witnesses == 0


def test_isolation_hides_names_and_appeal_does_not_lift_it(tmp_path: Path) -> None:
    owner = _seed(91)
    claim = _claim(owner, "kept.aziel")
    ledger = NameLedger(path=tmp_path / "names.jsonl")
    assert ledger.accept(claim, now=OPENED).code == "OK"
    witness = _witness(_seed(92), claim)
    assert ledger.accept(witness, now=OPENED).code == "OK"
    evidence = "cd" * 32
    try:
        sign_isolation(
            _seed(93),
            seq=1,
            subject=claim["handle"],
            reason="CSAM",
            evidence_hash=evidence,
            check="label-blocklist",
        )
        raise AssertionError("another handle cannot isolate this one")
    except NameRefuse as exc:
        assert exc.code == "NOT_OWNER"
    try:
        sign_isolation(owner, seq=2, prev=claim["record_hash"], reason="CSAM", evidence_hash="zz", check="label")
        raise AssertionError("evidence must be a hash")
    except NameRefuse as exc:
        assert exc.code == "MALFORMED"
    try:
        sign_isolation(
            owner,
            seq=2,
            prev=claim["record_hash"],
            reason="name-policy",
            evidence_hash=evidence,
            check="label",
        )
        raise AssertionError("old reason codes are not isolation reasons")
    except NameRefuse as exc:
        assert exc.code == "MALFORMED"
    try:
        sign_isolation(
            owner,
            seq=2,
            prev=claim["record_hash"],
            reason="CSAM",
            evidence_hash=evidence,
            check="label",
            image=b"not-stored",
        )
        raise AssertionError("isolation must not carry image bytes")
    except NameRefuse as exc:
        assert exc.code == "LEAK"
    isolation = sign_isolation(
        owner,
        seq=2,
        prev=claim["record_hash"],
        reason="CSAM",
        evidence_hash=evidence,
        check="image-nudity",
        model="absent",
    )
    assert "image" not in isolation
    assert isolation["reason"] == "CSAM"
    assert isolation["model"] == "absent"
    assert isolation["evidence_hash"] == evidence
    assert ledger.accept(isolation, now=LATER).code == "OK"
    assert ledger.is_isolated(claim["handle"])
    hidden = resolve(ledger, "kept.aziel", now=FINAL_AT)
    assert hidden.ok is False
    assert hidden.code == "ISOLATED"
    assert hidden.target is None
    bare = resolve(ledger, claim["handle"], now=FINAL_AT)
    assert bare.code == "ISOLATED"
    assert bare.target is None
    later_witness = sign_witness(_seed(94), seq=1, subject_hash=claim["record_hash"])
    assert ledger.accept(later_witness, now=LATER).code == "ISOLATED"
    appeal = sign_appeal(
        owner,
        seq=3,
        prev=isolation["record_hash"],
        isolation_hash=isolation["record_hash"],
        note="operator re-check requested",
    )
    assert appeal["note"] == "operator re-check requested"
    assert "check" not in appeal
    assert ledger.accept(appeal, now=FINAL_AT).code == "OK"
    view = ledger.trust_view(claim["handle"])
    assert view["isolated"] is True
    assert view["appeal_requested"] is True
    assert view["appeal_lifts_isolation"] is False
    still = resolve(ledger, "kept.aziel", now=FINAL_AT)
    assert still.code == "ISOLATED"
    assert still.target is None
    again = _claim(owner, "after.aziel", seq=4, prev=appeal["record_hash"])
    assert ledger.accept(again, now=FINAL_AT).code == "ISOLATED"
    reloaded = NameLedger.load(ledger.path)
    assert reloaded.is_isolated(claim["handle"])
    assert resolve(reloaded, "kept.aziel", now=FINAL_AT).code == "ISOLATED"


def test_cli_resolve_fallthrough_and_names(capsys) -> None:
    assert main(["names"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["icann_registration"] is False
    assert payload["pow_bits_min"] == 8
    assert main(["resolve", "baku.az"]) == 1
    refused = json.loads(capsys.readouterr().out)
    assert refused["code"] == "DNS_FALLTHROUGH"
    handle = _handle(_seed(90))
    assert main(["resolve", handle[1:].lower() + ".aziel"]) == 0
    owned = json.loads(capsys.readouterr().out)
    assert owned["code"] == "SELF_CERT"
    assert owned["owner"] == handle
