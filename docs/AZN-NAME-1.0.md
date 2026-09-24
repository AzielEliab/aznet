# AZN-NAME-1.0 — mesh names for AZNet

AZNet naming for Aziel Eliab's local-first edge mesh. A caller resolves a
name from a **local copy** of signed records. This library does not open a
socket, does not host a payload, and does not take a private key into the
ledger.

**Author:** Aziel Eliab only.
**Pair:** AZNet and AZBrowser stay separate software. Pairing is order and
token only. This resolver does not merge them.

`docs/designs/FED-MESH-1.0.md` was not on `AzielEliab/aziel-runtime` main
when this file was written. Wire bytes are isolated in
[`aznet/names/wire.py`](../aznet/names/wire.py). Open alignment points are
listed at the end and on `aznet names`.

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
- AZNet stores hashes and handles. `payload`, `keys`, and `user_content`
  are `ABSENT`. Private seeds never enter the ledger or the CLI.

Lamb Lens order on a lookup: **Service** (return the verified target),
**Clarity** (the code names the failure), **Peace** (a fork is refused
and is not merged).

## Handle

A node handle is `#` plus 64 lowercase hex characters of the raw 32-byte
Ed25519 public key (RFC 8032). The matching `.aziel` name is the same 64
hex characters plus `.aziel`.

```text
#d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a
d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a.aziel
```

The hex label is 64 characters, longer than a DNS label. That is deliberate:
regular DNS cannot carry it. The name is self-certifying. It needs no claim,
and another key cannot sign it. With no anchored update, the target is the handle itself
(`target_kind: node`). The owner may publish `update` or `renew`. Claim,
transfer, and release of that name return `SELF_CERT_FIXED`.

## Friendly names and Cap-7

A friendly name is one label plus `.aziel`. The label is 1–63 characters,
`[a-z0-9-]`, and does not start or end with `-`. A 64-hex label is reserved
for the self-certifying name.

Friendly names, and the four drop-in allowlist keys, are
**first-valid-anchored-claim-wins**:

- Unanchored rivals that share `prev` are ordered by TemporalLock
  `timeslate`. The earliest unique timeslate is anchored. Later rivals
  return `LOST_RACE` and are not served.
- Equal timeslates return `FORK`. No winner is chosen.
- A rival that arrives after a different record with the same `prev` is
  already anchored does not rewrite history. If it is later, `LOST_RACE`.
  If it is earlier or tied, the name freezes as `FORK` (`NO-REWRITE`).
- An extension must use `sequence = parent + 1`, `prev` = the parent
  record hash, and a strictly later `timeslate`.

Each handle may hold **7** active friendly or allowlisted names (Cap-7).
The self-certifying name does not use a slot. Expiry does not free a slot.
Release does. Transfer moves the slot to `successor`. An 8th name returns
`OVER_CAP` and is not anchored.

Operations: `claim`, `update`, `transfer`, `release`, `renew`. Transfer and
release are signed by the current owner. After transfer, the effective
owner is `successor`. After release, resolve returns `REVOKED` until a new
`claim` extends that name's chain.

Renewal is `until-release` (no `expires_at`) or `expiring` (`expires_at`
after `timeslate`). Expiry is evaluated only when the caller passes `now`.
A missing `now` sets `expiry_checked` false and does not invent a clock.

## `.az` allowlist

Queries that end in `.az` and are **not** on this list return
`DNS_FALLTHROUGH` and no mesh target. The caller uses normal DNS.

Factory labels from aziel-runtime `CAP7-SHUFFLE-1.0` (`mesh_name` there is
`{label}.az`, `icann_tld_az: false`). This resolver stores the claim at
`{label}.aziel` and accepts the historical `.az` spelling as an alias:

| Query alias | Ledger name | Cap-7 role |
| --- | --- | --- |
| `azgrid.az` | `azgrid.aziel` | real duplication of azieleliab.com |
| `azcloak.az` | `azcloak.aziel` | real duplication of godlock.uk |
| `azvault.az` | `azvault.aziel` | real duplication of azielcorpuslibrary.net |
| `azshift.az` | `azshift.aziel` | real duplication of hedidntjump.com |
| `azbooth.az` | `azbooth.aziel` | false site (cloak decoy) |
| `azflag.az` | `azflag.aziel` | false site (cloak decoy) |
| `azstandby.az` | `azstandby.aziel` | false site (cloak decoy) |

Drop-in display names are their own ledger keys. They are not rewritten to
`.aziel` and they are not answered from the Azerbaijan ccTLD:

| Display name | Ledger key | Hub the internet actually uses |
| --- | --- | --- |
| `AZ.AzielEliab.AZ` | `az.azieleliab.az` | `https://www.azieleliab.com/` |
| `AZ.AzielCorpusLibrary.AZ` | `az.azielcorpuslibrary.az` | `https://www.azielcorpuslibrary.net/` |
| `AZ.Godlock.AZ` | `az.godlock.az` | `https://godlock.uk/` |
| `AZ.HeDidntJump.AZ` | `az.hedidntjump.az` | `https://www.hedidntjump.com/` |

`internet_reach()` cites that hub layer (`public_icann: true`,
`resolves_to_hub: true`, `icann_registration_by_this_code: false`).
`resolve()` does not return the hub URL as a target. Cap-7 cites keep
`resolves_to_hub: false` and `standard_internet_reaches_cap7: false`.
A false-site flag is a cite. It does not block a signed record.

`baku.az` is not on the list. It falls through to normal DNS.

## Record wire

Canonical body: UTF-8 JSON, sorted keys, no extra whitespace, exactly
`SIGNED_FIELDS`. The signature message is the prefix `AZN-NAME-1.0` + NUL
plus that body. `record_hash` is SHA-256 of the body (the prefix is not
inside the hash). `signature` is Ed25519 over the signature message, hex.

Signed fields:

| Field | Value |
| --- | --- |
| `spec` | `AZN-NAME-1.0` |
| `op` | `claim`, `update`, `transfer`, `release`, `renew` |
| `name` | canonical ledger key |
| `owner` | `#` + 64 hex public key |
| `target_kind` | `object`, `ref`, `node`, or `none` (release only) |
| `target` | 64-hex content hash, 64-hex ref, handle, or empty |
| `sequence` | integer ≥ 1 |
| `prev` | per-name ChainLock prev; 64 zero hex at genesis |
| `handle_prev` | per-handle ChainLock prev; 64 zero hex for the owner's first record |
| `timeslate` | `YYYY-MM-DDTHH:MM:SSZ` |
| `expires_at` | empty, or a timeslate when `renewal` is `expiring` |
| `renewal` | `until-release` or `expiring` |
| `successor` | empty, or the new handle on `transfer` |
| `payload`, `keys`, `user_content` | `ABSENT` |

`object` and `ref` targets are hashes. `node` targets are handles. URLs are
refused. The record does not carry the bytes those hashes name.

Local anchor line (`AZN-NAME-ANCHOR-1.0`), append-only, not inside the
signature:

```text
spec, kind (record|fork), prev_hash, record_hash, name, timeslate, anchor_hash
```

`anchor_hash` is SHA-256 of the canonical anchor fields. A `record` line
also stores the signed record. A `fork` line freezes the name. The anchor
chain's first `prev_hash` is 64 zero hex.

Sync envelope (`AZN-NAME-SYNC-1.0`): `records` plus `payload` / `keys` /
`user_content` = `ABSENT`. A private key or a payload field returns `LEAK`
and anchors nothing from that envelope. qnm-node is responsible for moving
the envelope. This library only checks it and caches the records that pass.

## Codes

| Code | Meaning |
| --- | --- |
| `OK` | Anchored record. `owner` and `target` are set. |
| `SELF_CERT` | No record yet. Target is the handle. |
| `IDEMPOTENT` | The same record was already anchored. |
| `UNCLAIMED` | Friendly or allowlisted name has no anchored claim. |
| `DNS_FALLTHROUGH` | `.az` name outside the allowlist. Use normal DNS. |
| `NOT_MESH` | Not `.aziel` and not an allowlisted `.az` name. |
| `BAD_SIGNATURE` | Signature or `record_hash` failed. |
| `FORK` | Equal timeslate, or a late conflict. Not merged. |
| `LOST_RACE` | A strictly earlier claim is already the chain. |
| `OVER_CAP` | This handle already has 7 names. |
| `EXPIRED` | `expires_at` is not after the caller's `now`. |
| `REVOKED` | The tip is a release. |
| `NOT_OWNER` | Signer is not the current owner. |
| `BAD_CHAIN` | `prev` or `handle_prev` does not extend the tip. |
| `BAD_SEQUENCE` | `sequence` does not follow the parent. |
| `SELF_CERT_FIXED` | Claim, transfer, or release of a handle name. |
| `LEAK` | Key or payload material was offered. |
| `MALFORMED` | Shape, clock, or target is not in the wire format. |

## Library

```python
from aznet.names import honesty, resolve, sign_record

record = sign_record(seed, name="garden.aziel", op="claim", ...)
answer = resolve([record], "garden.aziel", now="2026-09-24T12:00:00Z")
answer.owner   # handle
answer.target  # hash or handle
honesty()      # machine surface; only what this code does
```

`aznet names` prints that surface. `aznet resolve NAME --now TIMESLATE`
reads `AZNET_NAMES` or `./aznet_names.jsonl`. The CLI does not accept a seed.

## Open alignment points

1. **FED-MESH-1.0** — spec file was not merged. Adjust `aznet/names/wire.py` when it is.
2. **Handle encoding** — full public key as 64 hex. A spec may require base32 or a hash.
3. **Signature message** — prefix `AZN-NAME-1.0` NUL + canonical JSON. A spec may use CBOR or no prefix.
4. **TemporalLock** — `timeslate` is caller-supplied. This library does not call the TemporalLock worker and does not prove clock sync.
5. **ChainLock** — local `AZN-NAME-ANCHOR-1.0` log. Not a write to suite ChainLock CL-WP-0.4. `prev` and `handle_prev` are inside the signed record.
6. **Cap-7 spelling** — runtime `mesh_name` is `{label}.az`. Claims live at `{label}.aziel`. The `.az` form is an allowlisted alias.
7. **Late earlier claim** — earliest wins before either rival is anchored. After anchor, a contradicting earlier claim freezes `FORK` instead of rewriting.
8. **Relay transport** — sync is an in-process envelope. qnm-node framing is not specified here. No socket is opened.
9. **Self-cert default** — no record yet still returns the handle as the target.
10. **qnm node id** — suite `mesh_join` ids (`[a-z0-9._-]{8,80}`) are not this handle.
