---
name: AZNet
description: Use when verifying hashes on the AZNet silent verification side-net (AZN-WP-0.1). Hashes only — never payloads, keys, or user content. AZNet + AZBrowser both required. FragGate unlocks access. StaticClock stamps time. Hosted /v1 via this Worker or aziel-runtime slug aznet. Author Aziel Eliab.
---

# AZNet

Silent verification SIDE-NET. Not an alt internet.

Author: **Aziel Eliab**.

Use when mirroring a cryptographic hash, shifting the Custodian Garden / Gold Pages, stamping a hash, or writing a Memorial. Never host payloads. Never store keys or user content. UI is a mandatory witness — if altered, terminate and memorial.

AZNet, AZBrowser, and FragGate are **separate apps**. Do not embed AZNet chrome in AZBrowser or FragGate. Functional order only: `pair_token` then FragGate `pair_flag` before garden / stamp / memorial writes. StaticClock stamps time.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Endpoints (this Worker)

Host: `https://aznet-download-tracker.vibelock.workers.dev`

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/example` | Sample pair + stamp payload. Does not increment downloads. |
| GET | `/v1/doctor` | Hosted self-check (no writes). Does not increment downloads. |
| GET | `/v1/garden` | Demo Gold Pages (shifting, non-ranked hashes). |
| GET | `/v1/time` | StaticClock advisory display. Not a scheduler. |
| GET | `/v1/witness` | Mandatory UI witness hash. |
| POST | `/v1/pair` | Pair AZNet + AZBrowser. Client may send ledger. |
| POST | `/v1/unlock` | FragGate unlock after pair. |
| POST | `/v1/stamp` | TemporalLock-style stamp of a hash. Pair + unlock required. |
| POST | `/v1/memorial` | Terminal compromise memorial. No exploit details. |
| POST | `/v1/withdraw` | Withdrawal over coercion. |
| POST | `/v1/verify` | Walk hashes and prev links. Not stored. |
| POST | `/v1/lattice` | Verify receipt links + counts. |
| POST | `/v1/receipts` | Return the client-held ledger. |
| POST | `/v1/witness` | Check UI witness. Mismatch terminates + memorial. |

OpenAPI: `https://aznet-download-tracker.vibelock.workers.dev/openapi.json`

Catalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`

MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`

Catalog aliases under `/p/aznet/…` when listed. FragGate slug: `aznet`.

AZBrowser (required pair): `https://github.com/AzielEliab/azbrowser`

StaticClock: `https://staticclock-download-tracker.vibelock.workers.dev/`

TemporalLock (timeslate lattice): `https://temporallock-download-tracker.vibelock.workers.dev/`

FragGate kernel: `https://github.com/AzielEliab/fraggate`

Do **not** wire Lumen, AZInterface, AZ-OS Hub, or Interface products.

## How to call (Mozilla/5.0)

```bash
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' -X POST https://aznet-download-tracker.vibelock.workers.dev/v1/pair \
  -H 'content-type: application/json' \
  -d '{"azbrowser":"https://github.com/AzielEliab/azbrowser"}'
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/garden
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/skill
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
- This Worker skill: `GET https://aznet-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://aznet-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://aznet-download-tracker.vibelock.workers.dev/v1/example`

Local UI: Garden Rolodex, Memorial, stamps, receipts, pair-status, FragGate unlock, StaticClock. Then `aznet doctor`.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients: `POST https://aziel-runtime.vibelock.workers.dev/mcp`.

Counted download (gzip HTTP 200, no 302): https://aznet-download-tracker.vibelock.workers.dev/download?asset=aznet-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/aznet
