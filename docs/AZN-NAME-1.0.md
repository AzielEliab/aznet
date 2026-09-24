# AZN-NAME-1.0 — mesh names for AZNet

AZNet naming for Aziel Eliab's local-first edge mesh. A caller resolves a
name from a **local copy** of signed records. This library does not open a
socket, does not host a payload, and does not take a private key into the
ledger.

**Author:** Aziel Eliab only.
**Pair:** AZNet and AZBrowser stay separate software. Pairing is order and
token only. This resolver does not merge them.

Name statements use the FED-MESH-1.0 `kind: name` fields in
[`aznet/names/wire.py`](../aznet/names/wire.py). That spec is on
`AzielEliab/aziel-runtime` branch `cursor/fed-mesh-e546`
(`docs/designs/FED-MESH-1.0.md`). It is not on main yet, and it has no
Mesh Security section. The proof-of-work, witness, vouch, and advisory
rules below are this repo's copy of the operator brief until that section
lands.

## What this is

A parallel namespace. AZBrowser, qnm-node, and any other caller of
`aznet.names.resolve` can use it.

- The mesh TLD is `.aziel`.
- Regular browsers do not see `.aziel` names.
- This code does not register anything with ICANN.
- `.az` is Azerbaijan's ccTLD. It stays on normal DNS except the allowlist
  below.
- Cap-7 is the mesh duplication layer. Standard internet does not reach
  Cap-7 names. Internet reach of the four AZ.* domains is the hub HTTPS
  link for that domain (`resolves_to_hub` stays false on Cap-7).
- AZNet stores hashes and handles. Private seeds never enter the ledger
  or the CLI.
- A name statement is not code. Fields named `code`, `wasm`, `script`, or
  `bytecode` return `NO_EXEC`. Nothing in this library runs peer bytes.

Lamb Lens order on a lookup: **Service** (return the verified target),
**Clarity** (the code names the failure), **Peace** (a fork is refused
and is not merged).

## Handle

A node handle matches FED-MESH-1.0: `#` plus 11 uppercase Crockford
characters (`0123456789ABCDEFGHJKMNPQRSTVWXYZ`, no I, L, O, or U). The
source is the first 55 bits of SHA-256 of the raw 32-byte Ed25519 public
key, MSB first, 5-bit groups.

```text
#CPV0CWYPXP4
cpv0cwypxp4.aziel
```

Vector seed `0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f20`
produces that handle and public key
`ebVWLo_mVPlAeLES6KmLp5AfhTrmlb7X4OORC60ElmQ`.

The matching `.aziel` name is the handle body in lowercase plus `.aziel`.
It needs no claim. Another key cannot sign it. With no anchored update,
the target is the handle itself (`target.type: handle`). The key is not
proven until a signed record exists (`key_checked: false`). The owner may
publish an update. Claim, transfer, and release of that name return
`SELF_CERT_FIXED` (the relay's name for the same refusal is
`FED-MESH-HANDLE-MISMATCH`).

## Friendly names and finality

A friendly name is one label plus `.aziel`. The label matches
`^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$`. An 11-character Crockford label
is the self-certifying name, not a friendly claim.

Friendly claims are **first-valid-FINAL-claim-wins**:

- A new friendly claim carries a hashcash proof-of-work. The nonce is
  outside the signature. The input is UTF-8 `statement_hash:nonce`.
  SHA-256 of that string must have at least `POW_BITS_MIN` (8) leading
  zero bits. Updates, transfers, releases, and self-cert records do not
  carry a nonce.
- The claim stays `PENDING` until this ledger has held it for 72 hours
  **and** at least `WITNESS_K` (3) other handles have signed a
  `name-witness` for that claim. Resolve returns `PENDING` with the
  target filled in so a caller can show it, and `ok` false.
- Only a `FINAL` claim is served (`code: OK`, `finality: FINAL`).
- Competing claims are both anchored. The earliest `anchored_at` among
  FINAL claims wins. A later FINAL does not beat an earlier FINAL. An
  earlier PENDING does not beat a later FINAL. Equal anchor times are
  `FORK`. Nothing is rewritten.
- A handle that signs two different statements at the same `seq` is
  marked equivocating. The proof is stored. Names from that handle are
  not served. This library does not gossip. If that second `seq` is
  older than the tip, or its `prev` is not anchored, the code is
  `ROLLBACK` and the handle is still marked. A first statement whose
  `prev` is simply missing returns `BAD_CHAIN` and does not mark the
  handle.
- `anchored_at` is the caller-supplied `now` at ingest
  (`YYYY-MM-DDTHH:MM:SSZ`). FED-MESH name statements have no timeslate.
  Omitting `now` means the claim cannot become FINAL. A peer that syncs
  the statement starts its own window. This is not a TemporalLock proof
  and not a worldwide clock.

A witness is a distinct handle. The signer cannot witness their own
claim. This library does not check that the witness is a registered
relay.

Each handle may hold **7** friendly names (Cap-7). Pending claims count,
so a flood cannot anchor an 8th name while the others are still pending.
The self-certifying name does not use a slot. A released name frees its
slot. An expired name frees its slot. An 8th live name returns `OVER_CAP`.

A relay that follows FED-MESH section 5.1 still keeps one row per name
and answers `FED-MESH-NAME-TAKEN` for a second claim. This library keeps
both claims and lets resolution pick the earliest FINAL one.

## Transfer, release, expiry

The signed fields are the FED-MESH name statement. There is no `op`
field. The act is implied:

| Act | `owner` | `target` | `prev_record` |
| --- | --- | --- | --- |
| Claim | the signer | `{type, value}` | 64 zero hex, or the release this claim follows |
| Update or renew | the signer | `{type, value}` | the current name statement hash |
| Transfer | the new handle | `{type, value}` | the current name statement hash |
| Release | `""` | `null` | the current name statement hash |

`target.type` is `hash` (64 lowercase hex), `ref` (FED-MESH ref name),
or `handle` (a `#` handle). URLs are refused. `expires` is `null` or a
unix time in milliseconds. A record whose `expires` is already past the
caller's `now` is not stored. Resolve returns `EXPIRED` when `now` is at
or after `expires`. Without `now`, expiry is not evaluated.

After transfer, the effective owner is `owner`. After release, resolve
returns `REVOKED`. A later claim may extend that name and must bring its
own proof-of-work and witnesses. Witnesses bind to the establishing
claim, not to each update. Handle `prev` / `seq` is one chain per handle
across name, witness, vouch, and advisory statements.

## Vouch and advisory lists

A `vouch` is an existing handle co-signing another handle and that
handle's public key. Vouches show up in `trust_view`. They do not make a
claim FINAL. There is no score and no ranking on that view.

An `advisory` is a signed list (`list_id`, entries of `name`, `note`,
`subject_handle`). Notes are at most 80 characters. A `score` or
`ranking` field is refused. Advisories affect only a node that has
called `subscribe` for that signer. Subscriptions are local anchor lines.
They are not included in sync. A subscribed note is attached to the
resolve result and does not change `FINAL`.

## `.az` allowlist

Queries that end in `.az` and are **not** on this list return
`DNS_FALLTHROUGH` and no mesh target. The caller uses normal DNS.

Factory labels from aziel-runtime `CAP7-SHUFFLE-1.0`. This resolver
stores the claim at `{label}.aziel` and accepts the historical `.az`
spelling as an alias:

| Query alias | Ledger name | Cap-7 role |
| --- | --- | --- |
| `azgrid.az` | `azgrid.aziel` | real duplication of azieleliab.com |
| `azcloak.az` | `azcloak.aziel` | real duplication of godlock.uk |
| `azvault.az` | `azvault.aziel` | real duplication of azielcorpuslibrary.net |
| `azshift.az` | `azshift.aziel` | real duplication of hedidntjump.com |
| `azbooth.az` | `azbooth.aziel` | false site (cloak decoy) |
| `azflag.az` | `azflag.aziel` | false site (cloak decoy) |
| `azstandby.az` | `azstandby.aziel` | false site (cloak decoy) |

These four display names are cites. They are not FED-MESH name records.
`resolve` does not return a mesh target for them. `internet_reach()`
cites the hub (`public_icann: true`, `resolves_to_hub: true`,
`icann_registration_by_this_code: false`):

| Display name | Hub the internet actually uses |
| --- | --- |
| `AZ.AzielEliab.AZ` | `https://www.azieleliab.com/` |
| `AZ.AzielCorpusLibrary.AZ` | `https://www.azielcorpuslibrary.net/` |
| `AZ.Godlock.AZ` | `https://godlock.uk/` |
| `AZ.HeDidntJump.AZ` | `https://www.hedidntjump.com/` |

`baku.az` is not on the list. It falls through to normal DNS.

## Record wire

Canonical bytes match FED-MESH `canonicalize`: UTF-8 JSON, sorted keys,
no extra whitespace. The signature is Ed25519 over those bytes. `sig` is
unpadded base64url and is not inside the hash. `record_hash` is SHA-256
of the canonical statement.

Name statement (`kind: name`):

| Field | Value |
| --- | --- |
| `v` | `FED-MESH-1.0` |
| `kind` | `name` |
| `handle` | signer |
| `public_key` | raw Ed25519, unpadded base64url |
| `name` | canonical `.aziel` name |
| `owner` | `#` handle, or `""` on release |
| `target` | `{type, value}` or `null` on release |
| `expires` | `null` or unix milliseconds |
| `seq` | integer ≥ 1 |
| `prev` | handle-chain tip, or 64 zero hex |
| `prev_record` | previous name statement, or 64 zero hex |

`pow_nonce` sits beside `sig` on a friendly claim. It is not signed.
Witness (`kind: name-witness`), vouch (`kind: vouch`), and advisory
(`kind: advisory`) use the same handle chain and the same signature
rule. Their fields are in `aznet/names/record.py`.

Published FED-MESH vectors (name claim hash
`6d38408d305afb2ae562d3c022c3421fc8819c81d61108d3a8b91e2b8dc7ca7c`, ref
hash `06805b89889f62b379ae1dee9a7108f9ad37e23124c3ea111145d27438ceb708`)
verify here. That name claim has no `pow_nonce`, so this ledger will not
anchor it until a nonce is attached. Pinned bytes are in
`tests/vectors/azn-name-1.0.json`.

Local anchor line (`AZN-NAME-ANCHOR-1.0`), append-only, not inside the
signature: `spec`, `kind` (`record`, `equivocation`, or `subscribe`),
`prev_hash`, `record_hash`, `prior_hash`, `name`, `timeslate`,
`anchored_at`, `anchor_hash`. A `record` line also stores the signed
statement. Equivocation lines store the conflicting statement. Subscribe
lines stay on this node.

Sync envelope (`AZN-NAME-SYNC-1.0`): `records` plus `payload` / `keys` /
`user_content` = `ABSENT`. A private key or a payload field returns
`LEAK`. `anchored_at` is not exported. qnm-node is responsible for moving
the envelope. This library does not open a socket.

## Codes

| Code | Meaning |
| --- | --- |
| `OK` | The earliest FINAL record. `owner` and `target` are set. |
| `PENDING` | Anchored, not yet aged and witnessed. Target is present, `ok` is false. |
| `FINAL` | Used as `finality` on a served record. The resolve code stays `OK`. |
| `SELF_CERT` | No record yet. Target is the handle. The key is not proven. |
| `IDEMPOTENT` | The same statement was already anchored. |
| `UNCLAIMED` | No anchored claim. Also the AZ.* cite, which has no mesh target. |
| `DNS_FALLTHROUGH` | `.az` name outside the allowlist. Use normal DNS. |
| `NOT_MESH` | Not `.aziel` and not an allowlisted `.az` name. |
| `BAD_SIGNATURE` | Signature, public key, or `record_hash` failed. |
| `FORK` | Two claims share an anchor time. Not merged. |
| `POW_FAIL` | Friendly claim nonce misses 8 leading zero bits. |
| `POW_WEAK` | `pow_bits` is below 8. |
| `EQUIVOCATION` | This handle signed two statements at one `seq`. Not served. |
| `ROLLBACK` | `seq` or `prev` does not extend the handle tip. |
| `OVER_CAP` | This handle already has 7 friendly names. |
| `EXPIRED` | `expires` is at or before the caller's `now`. |
| `REVOKED` | The tip is a release. |
| `NOT_OWNER` | Signer is not the current owner, or the key does not match the handle. |
| `BAD_CHAIN` | `prev` or `prev_record` does not connect. |
| `BAD_SEQUENCE` | `seq` does not follow the handle tip. |
| `SELF_CERT_FIXED` | Claim, transfer, or release of a handle name. |
| `LEAK` | Key or payload material was offered. |
| `NO_EXEC` | The statement tried to carry code. |
| `MALFORMED` | Shape or clock is not in the wire format. |
| `WAIT` | Internal: the parent is later in the same ingest batch. |

`LOST_RACE` remains defined and is not returned. A second claim is
anchored, then resolution picks the earliest FINAL one.

## Library

```python
from aznet.names import honesty, resolve, sign_record

record = sign_record(seed, name="garden.aziel", op="claim", target="ab" * 32, target_kind="hash", seq=1)
answer = resolve([record], "garden.aziel", now="2026-09-24T12:00:00Z")
answer.owner      # handle
answer.target     # hash, ref name, or handle
answer.finality   # PENDING until aged and witnessed
honesty()         # machine surface; only what this code does
```

`aznet names` prints that surface. `aznet resolve NAME --now TIMESLATE`
reads `AZNET_NAMES` or `./aznet_names.jsonl`. The CLI does not accept a
seed.

## What this repo does not do

These belong to other repos. This library does not claim them.

- No Mesh Security section is published in FED-MESH-1.0.md yet. Constants
  here are local: 8-bit proof-of-work, 3 witnesses, 72 hours.
- Witnesses are distinct handles. They are not checked to be relays.
- No relay gossip, no socket, no end-to-end transport, no Tor bearer, no
  two-hop routing.
- No airlock, scanner, island mode, or per-peer quarantine.
- No object-byte check. A hash target is not compared to bytes.
- No zero-knowledge claim. No blockchain and no staking.
- Vouches and advisories do not change FINAL. Subscriptions are local.
- `now` is caller-supplied. This process does not call TemporalLock.

## Open alignment points

`aznet names` prints the same list.

1. **FED-MESH-1.0** — name fields match section 5.1 on the runtime branch. The file is not on main.
2. **Mesh security constants** — 8 bits, K=3, 72h. Not in the runtime spec yet. Age is local `anchored_at`.
3. **First FINAL versus first anchored** — a relay may refuse the second claim. This library keeps both.
4. **TemporalLock** — `now` is caller-supplied. No clock proof.
5. **ChainLock** — local `AZN-NAME-ANCHOR-1.0` log. Not suite ChainLock CL-WP-0.4.
6. **Cap-7 spelling** — runtime `mesh_name` is `{label}.az`. Claims live at `{label}.aziel`.
7. **AZ.* cites** — display names are not name records here. The relay does not resolve them either.
8. **Relay transport** — sync is an in-process envelope. No socket.
9. **Self-cert default** — no record yet still returns the handle, with `key_checked` false.
10. **qnm node id** — suite `mesh_join` ids are not this handle.
