# AZN-SIDENET-1.0 — AZnet is the sidenet

Operator naming lock: the sidenet is AZnet. The client surface is AZ Browser.
There is no second sidenet and no new Softwares slug. The pair slug stays
`azbrowser`. There is no public ICANN registration.

**Author:** Aziel Eliab only.

## Layers

L0 is the public FragGate path already in this repo:

- catalog ops `health`, `pair_status`, `garden_list`, `stamp`,
  `verify_hash`, `memorial_list`, `memorial_append`, `receipt_verify`,
  `skill`
- Worker `/mcp` pointer
- Worker `/v1/fraggate/*` proxy to aziel-runtime

That path stays the door. `sidenet` is not one of those ops. This
layer does not replace L0, does not probe the remote Worker, and does
not add a door.

The additive layer is the mesh sidenet: local Cap-7 mesh DNS pairs,
a qnm peer-bearer cite, and a survival inventory.

## Cap-7 mesh DNS pairing

Seven factory labels, same set as MirageGrid `CAP7-SHUFFLE-1.0`. This
repo does not own that factory and does not call shuffle land.

| Label | Mesh name | Alias | Role |
| --- | --- | --- | --- |
| `azgrid` | `azgrid.aziel` | `azgrid.az` | real duplication of azieleliab.com |
| `azbooth` | `azbooth.aziel` | `azbooth.az` | false site |
| `azcloak` | `azcloak.aziel` | `azcloak.az` | real duplication of godlock.uk |
| `azvault` | `azvault.aziel` | `azvault.az` | real duplication of azielcorpuslibrary.net |
| `azshift` | `azshift.aziel` | `azshift.az` | real duplication of hedidntjump.com |
| `azflag` | `azflag.aziel` | `azflag.az` | false site |
| `azstandby` | `azstandby.aziel` | `azstandby.az` | false site |

Local mesh DNS for those names is LIVE (the resolver in
AZN-NAME-1.0). Public DNS is SLOT. `resolves_to_hub` stays false.
Standard internet does not reach Cap-7. No label is a hardcoded
update host.

AZ Browser pairing stays order and token. Products stay separate.
AZ Browser reads this map; it does not merge with AZNet.

## Peer bearers

The appropriate peer bearer is qnm-node, for moving an
`AZN-NAME-SYNC-1.0` envelope. Status is SLOT. This process does not
open a socket. A cite of qnm-node is not a live session.

Any other bearer name is refused (`AZN-BEARER-REFUSED`).

## Survival

| Plane | Status | Why |
| --- | --- | --- |
| `l0-fraggate` | LIVE | Path contract in this repo. Remote not probed. |
| `local-hash-ledger` | LIVE | AZN-WP-0.1 lattice runs here. |
| `local-mesh-dns` | LIVE | `.aziel` resolver runs here. Public DNS is SLOT. |
| `cap7-mesh-dns-pair` | LIVE | This map is produced here. |
| `qnm-peer-bearer` | SLOT | No socket is opened here. |
| `shuffle-land` | SLOT | MirageGrid owns land. Not called here. |
| `cold-shelf` | SLOT | No Codeberg, archive.org, or USB tip-pack from this repo. |
| `hub-https` | SLOT | Hubs are cites, not AZNet survival copies. Not probed. |
| `public-icann` | REFUSED | This code does not register a TLD. |

`independent_live_shelves` is 0. `multi_survival_complete` is false.
`copies_one_tunnel` is true: GitHub and this Worker are one product
tunnel. A finished multi-survival set would need an independent shelf
this repository does not publish. SLOT is not painted LIVE to close
that gap.

## What this layer does not do

- No public ICANN registration. `.az` outside the allowlist stays
  normal DNS.
- No payload hosting. No peer code execution. No gossip socket.
- No second FragGate door. No Softwares catalog change.
- No rewrite key. Survival does not authorize a false status.

`aznet sidenet` prints the machine map. `GET /v1/sidenet` on the
Worker returns the same map and is not a catalog live op.
