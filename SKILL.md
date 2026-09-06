---
name: AZNet
description: Use when verifying hashes on the AZNet silent verification side-net (AZN-WP-0.1). Hashes only — never payloads, keys, or user content. AZNet + AZBrowser both required. FragGate unlocks access. StaticClock stamps time. Hosted /v1 via this Worker or aziel-runtime slug aznet. Author Aziel Eliab.
---

# AZNet

Silent verification SIDE-NET. Not an alt internet.

Author: **Aziel Eliab**.

Use when mirroring a cryptographic hash, shifting the Custodian Garden / Gold Pages, stamping a hash, or writing a Memorial. Never host payloads. Never store keys or user content. UI is a mandatory witness — if altered, terminate and memorial.

AZNet, AZBrowser, and FragGate are **separate software**. Do not embed AZNet chrome in AZBrowser or FragGate. Functional order only: `pair_token` then FragGate `pair_flag` before garden / stamp / memorial writes. StaticClock stamps time. Suite mesh is presence + QNM live|locked|isolated (default OFF) — not an anonymity network and not AZMail's product-local ring.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Agent path is FragGate only

ONE FragGate door. Agents must not treat this Worker as a second MCP brand.

- Discover: `fraggate_list` / `GET https://aziel-runtime.vibelock.workers.dev/v1/fraggate/list`
- Call: `fraggate_call` / `POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call` with `{ slug: "aznet", op, payload }`
- This Worker `GET|POST /mcp` is a **pointer** (never 404) to that door
- This Worker `/v1/fraggate/*` (list / describe / call / verify) **PROXY** to aziel-runtime via the `AZIEL_RUNTIME` service binding
- This Worker `/v1/mesh/*` **PROXY** to aziel-runtime suite mesh (default OFF). QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Catalog MCP `mesh_*` + FragGate `slug=mesh`

Catalog LIVE_OPS (same names the Worker UI buttons call): `health`, `pair_status`, `garden_list`, `stamp`, `verify_hash`, `memorial_list`, `memorial_append`, `receipt_verify`, `skill`.

`doctor` is **not** a FragGate live op. Local CLI `aznet doctor` stays a device-local self-check.

## Endpoints (this Worker)

Host: `https://aznet-download-tracker.vibelock.workers.dev`

| Method | Path | What |
|--------|------|------|
| GET | `/` | Product homepage. Increments **views**. |
| GET | `/download` | Counted tarball (HTTP 200, live counter, no 302). Increments **downloads**. |
| GET | `/count` | `{views, downloads, total}`. Does not increment. |
| GET | `/stats` | views, downloads, `by_repo` / `by_branch` / `by_fork`. Does not increment. |
| GET/POST | `/mcp` | FragGate pointer (never 404). Not a second MCP. |
| GET | `/v1/fraggate/list` | PROXY to aziel-runtime FragGate list. |
| GET | `/v1/fraggate/describe` | PROXY to aziel-runtime FragGate describe. |
| POST | `/v1/fraggate/call` | PROXY to aziel-runtime FragGate call. |
| POST | `/v1/fraggate/verify` | PROXY to aziel-runtime FragGate verify. |
| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live\|locked\|isolated. Never enables. |
| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). |
| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/example` | Sample pair + stamp payload. Does not increment downloads. |
| GET/POST | `/v1/pair_status` | Catalog name: pair + report AZBrowser token/flag. Leftover alias: `/v1/pair`. |
| GET | `/v1/garden_list` | Catalog name: demo Gold Pages. Leftover alias: `/v1/garden`. |
| GET | `/v1/time` | StaticClock advisory display. Not a scheduler. Human chrome. |
| GET | `/v1/witness` | Mandatory UI witness hash. Human chrome. |
| POST | `/v1/unlock` | Human chrome: FragGate unlock after pair. Not a catalog live op. |
| POST | `/v1/stamp` | TemporalLock-style stamp of a hash. Pair + unlock required. |
| POST | `/v1/memorial_append` | Catalog name: terminal memorial. Leftover alias: `/v1/memorial`. |
| POST | `/v1/memorial_list` | Catalog name: list memorial receipts from the client ledger. |
| POST | `/v1/withdraw` | Human chrome: withdrawal over coercion. |
| POST | `/v1/verify_hash` | Catalog name: walk hashes and prev links. Leftover alias: `/v1/verify`. |
| POST | `/v1/receipt_verify` | Catalog name: verify receipt links. Leftover alias: `/v1/receipts`. |
| POST | `/v1/lattice` | Human chrome: verify receipt links + counts. |
| POST | `/v1/witness` | Human chrome: check UI witness. Mismatch terminates + memorial. |

OpenAPI: `https://aznet-download-tracker.vibelock.workers.dev/openapi.json`

Catalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`

Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`

This Worker MCP pointer: `GET|POST https://aznet-download-tracker.vibelock.workers.dev/mcp`

Catalog aliases under `/p/aznet/…` when listed. FragGate slug: `aznet`.

AZBrowser (required pair): `https://github.com/AzielEliab/azbrowser`

StaticClock: `https://staticclock-download-tracker.vibelock.workers.dev/`

TemporalLock (timeslate lattice): `https://temporallock-download-tracker.vibelock.workers.dev/`

FragGate kernel: `https://github.com/AzielEliab/fraggate`

Do **not** wire Lumen, AZInterface, AZ-OS Hub, or Interface products.

## How to call (Mozilla/5.0)

```bash
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/mcp
curl -s -A 'Mozilla/5.0' -X POST https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call \
  -H 'content-type: application/json' \
  -d '{"slug":"aznet","op":"pair_status","payload":{"azbrowser":"https://github.com/AzielEliab/azbrowser"}}'
curl -s -A 'Mozilla/5.0' -X POST https://aznet-download-tracker.vibelock.workers.dev/v1/pair_status \
  -H 'content-type: application/json' \
  -d '{"azbrowser":"https://github.com/AzielEliab/azbrowser"}'
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/count
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/stats
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/garden_list
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/mesh
```

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): `POST` the catalog MCP endpoint.

## Local (after one-click install)

```bash
curl -fsSL https://aznet-download-tracker.vibelock.workers.dev/install.sh | bash
aznet ui
aznet doctor
```

Then open http://127.0.0.1:8771 (this computer only).

## Honest banner

THIS IS: a silent verification SIDE-NET (hash continuity, Custodian Garden, Memorial ledger). THIS IS NOT: an alt internet, a host, a payload store, a VPN, or a key store. The Worker is a control-plane / demo garden. Device-local silent node is the real posture. AZNet + AZBrowser are both required. Author Aziel Eliab.

Cite the GitHub repository and this Worker. No Zenodo DOI is invented here; a software deposit is still needed.

Apache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: hashes only. Not an alt internet.

- Product homepage (workspace + counted download): https://aznet-download-tracker.vibelock.workers.dev/
- Catalog product (when listed): https://aziel-runtime.vibelock.workers.dev/p/aznet/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker MCP pointer: `GET|POST https://aznet-download-tracker.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://aznet-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://aznet-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://aznet-download-tracker.vibelock.workers.dev/v1/example`

Local UI: Garden Rolodex, Memorial, stamps, receipts, pair-status, FragGate unlock, StaticClock. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). Device-local `aznet doctor` is not a FragGate live op.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients: `POST https://aziel-runtime.vibelock.workers.dev/mcp`.

Counted download (gzip HTTP 200, no 302): https://aznet-download-tracker.vibelock.workers.dev/download?asset=aznet-0.1.0.tar.gz
Count JSON: https://aznet-download-tracker.vibelock.workers.dev/count
Stats (`by_repo` / `by_branch` / `by_fork`): https://aznet-download-tracker.vibelock.workers.dev/stats
Isolated counter: Worker `aznet-download-tracker`, KV `AZNET_DOWNLOADS`. `/v1` does not increment.
Hubs list this Worker once live: https://www.azielcorpuslibrary.net/software · https://godlock.uk/software · https://www.azieleliab.com (Software section)
GitHub: https://github.com/AzielEliab/aznet
