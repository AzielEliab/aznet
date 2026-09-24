# AZNet

AZNet keeps a device-local hash record and pairs with AZBrowser before a stamp is written.

**Author:** Aziel Eliab
**Date:** September 2026 · v0.1.0
**License:** [Apache-2.0](LICENSE)

## Start

1. Install: `python -m venv .venv && source .venv/bin/activate && pip install -e .`
2. Open the local page: `aznet ui`
3. The terminal prints `Open http://127.0.0.1:8771/`. Click **Pair AZBrowser**.

`aznet doctor` prints a pass/fail check. `aznet --help` lists commands. Add `--json` for the machine-readable fields (`aznet time --json`).

> Truth Is No Defense — .AZNet — AZ.

Spec: [docs/whitepaper.md](docs/whitepaper.md) ·
[docs/AZNet_v0_spec.md](docs/AZNet_v0_spec.md) ·
[aznet_schema.json](aznet_schema.json).
Contributing: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

## One-click install

```bash
curl -fsSL https://aznet-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `aznet ui`.

Or use the live software homepage (workspace + counted download):
https://aznet-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

- Homepage: [https://aznet-download-tracker.vibelock.workers.dev/](https://aznet-download-tracker.vibelock.workers.dev/)
- Direct tarball: [aznet-0.1.0.tar.gz](https://aznet-download-tracker.vibelock.workers.dev/download?asset=aznet-0.1.0.tar.gz)
- One-click install: [https://aznet-download-tracker.vibelock.workers.dev/install.sh](https://aznet-download-tracker.vibelock.workers.dev/install.sh)
- Skill: [https://aznet-download-tracker.vibelock.workers.dev/v1/skill](https://aznet-download-tracker.vibelock.workers.dev/v1/skill)
- OpenAPI: [https://aznet-download-tracker.vibelock.workers.dev/openapi.json](https://aznet-download-tracker.vibelock.workers.dev/openapi.json)
- GitHub: [https://github.com/AzielEliab/aznet](https://github.com/AzielEliab/aznet)
- Cite: [cite.json](https://aznet-download-tracker.vibelock.workers.dev/cite.json) — Eliab, Aziel. (2026). AZNet 0.1.0 [Software]. Apache-2.0. No Zenodo DOI is invented here; a software deposit is still needed.

Worker name: `aznet-download-tracker`

URL pattern (same as sibling Aziel Eliab products):

`https://aznet-download-tracker.vibelock.workers.dev`

| Path | What |
|------|------|
| `/` | Garden Rolodex + views |
| `/download` | Counted tarball (HTTP 200, live counter, no 302) |
| `/count` | `{views, downloads, total}` |
| `/stats` | views, downloads, `by_repo` / `by_branch` / `by_fork` |
| `/openapi.json` | OpenAPI 3.1 |
| `/mcp` | FragGate pointer (never 404). Not a second MCP. |
| `/v1/fraggate/*` | PROXY list/describe/call/verify to aziel-runtime |
| `/v1/mesh/*` | PROXY to aziel-runtime suite mesh (default OFF; QNM live / locked / isolated; QNS-CD-1.0 cite only) |
| `/v1/{op}` | Human UI backend. Catalog names: `pair_status`, `garden_list`, `stamp`, `verify_hash`, `memorial_list`, `memorial_append`, `receipt_verify`, `health`, `skill` |

Isolated counter: Worker `aznet-download-tracker`, KV `AZNET_DOWNLOADS`. `/v1` does not increment downloads.

Open http://127.0.0.1:8771 (loopback only). No CDN, no telemetry.

---

## Download

**Counted download page (this project only, ticks automatically):**

# → [https://aznet-download-tracker.vibelock.workers.dev/](https://aznet-download-tracker.vibelock.workers.dev/) ←

Direct tarball (also counted): [aznet-0.1.0.tar.gz](https://aznet-download-tracker.vibelock.workers.dev/download?asset=aznet-0.1.0.tar.gz)

- Live count JSON (`views`, `downloads`, `total`): [https://aznet-download-tracker.vibelock.workers.dev/count](https://aznet-download-tracker.vibelock.workers.dev/count)
- Stats (`by_repo` / `by_branch` / `by_fork`): [https://aznet-download-tracker.vibelock.workers.dev/stats](https://aznet-download-tracker.vibelock.workers.dev/stats)
- GitHub releases: [https://github.com/AzielEliab/aznet/releases](https://github.com/AzielEliab/aznet/releases)

## Software tabs (parent listing)

Once this Worker is live, AZNet is listed on:

- https://www.azielcorpuslibrary.net/software
- https://godlock.uk/software
- https://www.azieleliab.com (Software section)

Parent lists after deploy. Expected URL:
`https://aznet-download-tracker.vibelock.workers.dev/`

---

## Local page

`aznet ui` prints `Open http://127.0.0.1:8771/` and serves that page on this machine only.

The first screen is **Pair AZBrowser**, a short status line, and the time in words.
Stamps, Gold Pages, memorials, and receipts are under **Advanced**.
Light and dark follow the system. **Theme** on the page can switch them.
Keyboard focus uses a gold ring. The layout fits a phone width.

The `/local/…` routes stay JSON. `--json` on the CLI prints those same fields.

## CLI smoke

```bash
export AZNET_LEDGER=./aznet_ledger.jsonl
aznet pair --azbrowser https://github.com/AzielEliab/azbrowser
aznet unlock
aznet garden
aznet stamp --hash aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
aznet memorial --reason isolation
aznet receipts
aznet verify
aznet time
aznet time --json
aznet witness
aznet doctor
```

Default ledger is `./aznet_ledger.jsonl`. Override with
`AZNET_LEDGER` or `--ledger`.

Pairing is mandatory. Stamp refuses until AZNet + AZBrowser are paired
and FragGate has unlocked access.

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.aznet`. Offline. No analytics. Black / white / gold.

```bash
cd mobile
flutter create --org com.azieeliab --project-name aznet .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you run `flutter create .` (this machine has no Flutter SDK on PATH). Then open `android/` in Android Studio or `ios/Runner.xcworkspace` in Xcode. Not a store listing.

## What it does

AZNet is a silent verification side-net. It keeps hash continuity on this machine.

Principles:

- verification without hosting
- presence without authority
- withdrawal over coercion
- silence as security

The Custodian Garden / Gold Pages is a shifting, non-ranked hash
directory. A card shows its hash. Select it with a tap or the keyboard
to place that hash in the stamp field. No favorites, analytics, or
personalization.

Each action writes a hash-chained lattice receipt. StaticClock stamps
time. TemporalLock-style stamps carry a hash only. The Memorial ledger
records a terminal compromise: genesis hash, final hash, timestamps,
and a non-actionable summary. No exploit details.

UI is a mandatory witness. If the UI is altered, AZNet terminates and
writes a Memorial.

The Worker is a **control-plane / demo garden**. Device-local silent
node posture is the real product.

Runtime is stdlib only (`hashlib`, `json`). No extra crypto packages.

## Mesh names (AZN-NAME-1.0)

AZNet resolves mesh names from a local signed ledger. The mesh TLD is
`.aziel`. A node handle is `#` plus 11 Crockford characters of the
Ed25519 public key (FED-MESH-1.0), and that handle already owns
`<handle>.aziel`. Friendly names are first-valid-FINAL-claim-wins: an
8-bit proof-of-work, then 72 hours and 2 witness handles. Each handle
has 4 reserved hub-mirror names (`ae`, `corpus`, `godlock`, `hdj`) and
3 user names, plus the automatic `<handle>.aziel`. Factory Cap-7 labels
stay a separate cite layer and are not claimable `.aziel` names. `.az` stays on normal DNS except the Cap-7 allowlist (`azgrid`,
`azbooth`, `azcloak`, `azvault`, `azshift`, `azflag`, `azstandby`). The
four AZ.* display names are hub cites, not name records.

Regular browsers do not see `.aziel`. This repo does not register
anything with ICANN. Internet reach of those AZ.* domains is the hub
site. Cap-7 is the mesh duplication layer and does not resolve to the
hub. AZNet and AZBrowser stay separate software. Name records are hashes
and handles only. This library does not gossip, does not open a socket,
and does not run peer code.

```bash
aznet names
aznet resolve baku.az                 # DNS_FALLTHROUGH — not on the allowlist
aznet resolve cpv0cwypxp4.aziel       # SELF_CERT — the handle itself
```

Spec and open alignment points: [docs/AZN-NAME-1.0.md](docs/AZN-NAME-1.0.md).

## Invariants (enforced)

- **I1** Hashes only — `payload`, `keys`, `user_content` are always `ABSENT`
- **I2** Presence without authority — garden is non-ranked; no favorites
- **I3** Withdrawal over coercion — node may withdraw; no force
- **I4** Silence as security — no analytics, personalization, or engagement
- **I5** Hash continuity — append-only SHA-256 lattice
- **I6** UI is a mandatory witness — altered UI terminates + memorial
- **I7** Pairing required — AZNet + AZBrowser both required (except health/skill/pair/time)
- **I8** Memorial on terminal compromise — non-actionable; no exploit details
- **I9** Worker is a demo garden — honest about control-plane posture
- **I10** No persuasion / engagement optimization

## Pairing (mandatory)

AZNet, [AZBrowser](https://github.com/AzielEliab/azbrowser), and
[FragGate](https://github.com/AzielEliab/fraggate) are **separate software**
with separate Worker UIs. Do not embed AZNet chrome inside AZBrowser or
FragGate. ONE FragGate door. Agents use FragGate only (`slug=aznet`).

The required relationship is **functional order / pairing only**:
`pair_token` then FragGate `pair_flag` before garden / stamp / memorial
writes. AZBrowser may view side-net status from its own UI by calling
this runtime. Products stay separate.

Do **not** wire Lumen, AZInterface, AZ-OS Hub, or Interface products.

## Cross-links

- [AZBrowser](https://github.com/AzielEliab/azbrowser) — required pair; views the side-net
- [StaticClock](https://github.com/AzielEliab/staticclock) — stamps time
- [TemporalLock](https://github.com/AzielEliab/temporallock) — timeslate lattice
- [FragGate](https://github.com/AzielEliab/fraggate) — one door: discover, route, refuse
- [aziel-runtime](https://github.com/AzielEliab/aziel-runtime) — catalog + MCP + OpenAPI; QNS-CD-1.0 cites + catalog field
- [qnm-node](https://github.com/AzielEliab/qnm-node) — local Quantum Node Mesh process; local `qnsd` (QNS-CD-1.0 / photon QNS1)
- [AZInterface](https://github.com/AzielEliab/azinterface) — QNS-CD-1.0 pair-custody cite only (do not wire Interface ops into this Worker)
- [Aziel Digital Library](https://www.azielcorpuslibrary.net/)
- [godlock.uk](https://godlock.uk/)
- [www.azieleliab.com](https://www.azieleliab.com/)

## Use with AI assistants

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): `POST https://aziel-runtime.vibelock.workers.dev/mcp`. Public identity: Aziel Eliab only.

- Worker OpenAPI: https://aznet-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- FragGate slug: `aznet`
- This Worker MCP pointer: `GET|POST https://aznet-download-tracker.vibelock.workers.dev/mcp`
- FragGate proxy: `GET|POST https://aznet-download-tracker.vibelock.workers.dev/v1/fraggate/{list,describe,call,verify}`
- Suite mesh proxy: `GET|POST https://aznet-download-tracker.vibelock.workers.dev/v1/mesh` (and `/status`, `/nodes`, `/enable`, `/disable`, `/join`, `/heartbeat`, `/leave`, `/broadcast`)

Agents use FragGate only via aziel-runtime (`fraggate_call` / `POST /v1/fraggate/call` with `{slug:"aznet",op,payload}`). This Worker `/mcp` is a pointer, not a second MCP brand. Humans use the complete Worker UI (Garden Rolodex, Memorial, stamps, receipts, pair-status, FragGate unlock, StaticClock, Live Nodes strip). Dual surface: do not gut the human UI. Catalog UI ops: `pair_status`, `garden_list`, `stamp`, `verify_hash`, `memorial_list`, `memorial_append`, `receipt_verify`. `doctor` is local CLI only — not a FragGate live op. Suite mesh `/v1/mesh/*` PROXY to aziel-runtime (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. **QNS-CD-1.0** (photon QNS1 packet transfer) is a hub cite / Worker mesh cross-map only — local `qnsd` is coded in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites + catalog field live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); pair custody is [AZInterface](https://github.com/AzielEliab/azinterface). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Catalog MCP `mesh_*` + FragGate `slug=mesh`. Anon-broadcast is not a publish path.

Always send `User-Agent: Mozilla/5.0`.

## Notes

THIS IS: a silent verification SIDE-NET (hash continuity, Custodian Garden, Memorial ledger).
THIS IS NOT: an alt internet, a host, a payload store, a VPN, or a key store.
The Worker is a control-plane / demo garden. Device-local silent node is the real posture.
AZNet + AZBrowser are both required. Author Aziel Eliab only.

Cite the GitHub repository and this Worker. No Zenodo DOI is invented here (placeholder until a software deposit exists).

Apache-2.0. Forks are welcome and always allowed.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: hashes only.

- Product homepage (workspace + counted download): https://aznet-download-tracker.vibelock.workers.dev/
- Catalog product (when listed): https://aziel-runtime.vibelock.workers.dev/p/aznet/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://aznet-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://aznet-download-tracker.vibelock.workers.dev/openapi.json

Local page: Pair, time in words, and Advanced for Gold Pages, memorials, stamps, receipts, and FragGate unlock. Worker homepage adds the suite Live Nodes strip (`GET /v1/mesh`). Then `aznet doctor`.

Counted download (gzip HTTP 200, no 302): https://aznet-download-tracker.vibelock.workers.dev/download?asset=aznet-0.1.0.tar.gz
Count JSON: https://aznet-download-tracker.vibelock.workers.dev/count
Stats (`by_repo` / `by_branch` / `by_fork`): https://aznet-download-tracker.vibelock.workers.dev/stats
Isolated counter: Worker `aznet-download-tracker`, KV `AZNET_DOWNLOADS`. `/v1` does not increment.
Hubs list this Worker once live: https://www.azielcorpuslibrary.net/software · https://godlock.uk/software · https://www.azieleliab.com (Software section)
GitHub: https://github.com/AzielEliab/aznet
