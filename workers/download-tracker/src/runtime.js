/**
 * AZNet hosted runtime (port of canon/receipt/chain).
 * Stateless: client sends the ledger JSON in the body. Hashes only.
 * /v1 never touches DOWNLOADS KV.
 * Dual surface: GET/POST /mcp is a FragGate pointer (never 404).
 * Door paths (`/v1/fraggate/*`, `/v1/runtime/*`, `/v1/mesh/*`) PROXY to aziel-runtime.
 * Local ops are single-segment `/v1/{op}` only.
 * Author: Aziel Eliab only.
 */
import { classifyV1Path, doorTargetUrl } from "./door.js";
import { attachQnsCdCrossMap, isMeshLiveNodesPath, meshOpenApiPaths, meshPointer } from "./mesh.js";
const PRODUCT = "aznet";
const VERSION = "0.1.0";
const MOTTO = "Verification without hosting. Presence without authority.";
const ROLE = "silent verification side-net";
const AUTHOR = "Aziel Eliab";
const SPEC = "AZN-WP-0.1";
const ABSENT = "ABSENT";
const ACTOR = "operator";
const MARKER = "Truth Is No Defense — .AZNet — AZ.";
const HOST = "https://aznet-download-tracker.vibelock.workers.dev";
const RUNTIME = "https://aziel-runtime.vibelock.workers.dev";
const FRAGGATE_KERNEL = "https://github.com/AzielEliab/fraggate";
const FRAGGATE_MCP = "https://aziel-runtime.vibelock.workers.dev/mcp";
const FRAGGATE_CALL = "https://aziel-runtime.vibelock.workers.dev/v1/fraggate/call";
const AZBROWSER = "https://github.com/AzielEliab/azbrowser";
const FRAGGATE_LIVE_OPS = Object.freeze([
  "health",
  "pair_status",
  "garden_list",
  "stamp",
  "verify_hash",
  "memorial_list",
  "memorial_append",
  "receipt_verify",
  "skill",
]);
const LEFTOVER_ALIASES = Object.freeze({
  pair: "pair_status",
  garden: "garden_list",
  verify: "verify_hash",
  memorial: "memorial_append",
  receipts: "receipt_verify",
});
const GENESIS_PREV_HASH = "0".repeat(64);
const WITNESS_SECTIONS = ["garden", "memorial", "stamps", "receipts", "pair", "unlock", "staticclock"];
const EVENT_KINDS = ["GARDEN", "STAMP", "MEMORIAL", "PAIR", "UNLOCK", "WITNESS", "WITHDRAW"];
const MEMORIAL_REASONS = ["ui_altered", "integrity_refuse", "node_withdraw", "pair_broken", "witness_fail", "isolation"];
const HASH_FIELDS = [
  "actor", "azbrowser", "aznet_node", "date_stamp", "event_kind", "final_hash", "fraggate",
  "genesis_hash", "hash_hex", "keys", "label", "marker", "note", "pair_flag", "pair_status", "pair_token", "payload",
  "prev_hash", "reason", "spec", "staticclock", "summary", "timestamp", "unlock_status",
  "user_content", "witness_hash", "zone",
];
const DEMO_SEEDS = [
  "AZNet Gold Pages card 0 — verification without hosting",
  "AZNet Gold Pages card 1 — presence without authority",
  "AZNet Gold Pages card 2 — withdrawal over coercion",
  "AZNet Gold Pages card 3 — silence as security",
  "AZNet Gold Pages card 4 — hash continuity",
  "AZNet Gold Pages card 5 — node sovereignty",
  "AZNet Gold Pages card 6 — memorial ledger",
  "AZNet Gold Pages card 7 — cold storage",
];
const FORBIDDEN = ["payload_bytes", "ciphertext", "private_key", "secret", "user_text", "body", "exploit", "poc", "cve", "0day", "key_material", "password", "plaintext"];
const HONEST = "THIS IS: a silent verification SIDE-NET (hash continuity, Custodian Garden, Memorial ledger). THIS IS NOT: an alt internet, a host, a payload store, a VPN, or a key store. The Worker is a control-plane / demo garden. Device-local silent node is the real posture. AZNet + AZBrowser are both required. Author Aziel Eliab.";
const AI_CLIENTS = "Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a GPT Action, custom HTTP tool, or custom OpenAPI tool. MCP clients (Cursor, Glama, Claude, and others): `POST` the catalog MCP endpoint.";

const SKILL = `---
name: AZNet
description: Use when verifying hashes on the AZNet silent verification side-net (AZN-WP-0.1). Hashes only — never payloads, keys, or user content. AZNet + AZBrowser both required. FragGate unlocks access. StaticClock stamps time. Hosted /v1 via this Worker or aziel-runtime slug aznet. Author Aziel Eliab.
---

# AZNet

Silent verification SIDE-NET. Not an alt internet.

Author: **Aziel Eliab**.

Use when mirroring a cryptographic hash, shifting the Custodian Garden / Gold Pages, stamping a hash, or writing a Memorial. Never host payloads. Never store keys or user content. UI is a mandatory witness — if altered, terminate and memorial.

AZNet, AZBrowser, and FragGate are **separate apps**. Do not embed AZNet chrome in AZBrowser or FragGate. Functional order only: \`pair_token\` then FragGate \`pair_flag\` before garden / stamp / memorial writes. StaticClock stamps time.

Always send \`User-Agent: Mozilla/5.0\`. Cloudflare Workers may 403 an empty agent.

## Agent path is FragGate only

ONE FragGate door. Agents must not treat this Worker as a second MCP brand.

- Discover: \`fraggate_list\` / \`GET ${RUNTIME}/v1/fraggate/list\`
- Describe: \`fraggate_describe\` slug=\`aznet\`
- Call: \`fraggate_call\` / \`POST ${FRAGGATE_CALL}\` with \`{ slug: "aznet", op, payload }\`
- This Worker \`GET|POST /mcp\` is a **pointer** (never 404) to that door
- This Worker \`/v1/fraggate/*\` (list / describe / call / verify) **PROXY** to aziel-runtime via the \`AZIEL_RUNTIME\` service binding
- This Worker \`/v1/mesh/*\` **PROXY** to aziel-runtime suite mesh (default OFF). QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (local qnsd in [qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime); pair custody [AZInterface](https://github.com/AzielEliab/azinterface)). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Catalog MCP \`mesh_*\` + FragGate \`slug=mesh\`
- Leftover flat names such as \`aznet_stamp\` still go through FragGate — they are not a side door

Catalog LIVE_OPS (same names the Worker UI buttons call): \`health\`, \`pair_status\`, \`garden_list\`, \`stamp\`, \`verify_hash\`, \`memorial_list\`, \`memorial_append\`, \`receipt_verify\`, \`skill\`.

\`doctor\` is **not** a FragGate live op. Local CLI \`aznet doctor\` stays a device-local self-check. Worker UI does not expose a Doctor button.

AZNet is **separate software** from AZBrowser. Pairing is functional order only (\`pair_token\` + \`pair_flag\`). Do not merge UIs. Suite mesh is presence + QNM live|locked|isolated (default OFF) — not an anonymity network and not AZMail's product-local ring. QNS-CD-1.0 is a hub cite / Worker mesh cross-map only (photon QNS1 packet transfer). Not a Softwares-tab product. No public qnsd proxy.

## Endpoints (this Worker)

Host: \`https://aznet-download-tracker.vibelock.workers.dev\`

| Method | Path | What |
|--------|------|------|
| GET | \`/\` | Product homepage. Increments **views**. |
| GET | \`/download\` | Counted tarball (HTTP 200, live counter, no 302). Increments **downloads**. |
| GET | \`/count\` | \`{views, downloads, total}\`. Does not increment. |
| GET | \`/stats\` | views, downloads, \`by_repo\` / \`by_branch\` / \`by_fork\`. Does not increment. |
| GET/POST | \`/mcp\` | FragGate pointer (never 404). Not a second MCP. |
| GET | \`/v1/fraggate/list\` | PROXY to aziel-runtime FragGate list. |
| GET | \`/v1/fraggate/describe\` | PROXY to aziel-runtime FragGate describe. |
| POST | \`/v1/fraggate/call\` | PROXY to aziel-runtime FragGate call. |
| POST | \`/v1/fraggate/verify\` | PROXY to aziel-runtime FragGate verify. |
| GET | \`/v1/mesh\` | PROXY suite mesh status. Default OFF. QNM live\\|locked\\|isolated. QNS-CD-1.0 cite on the payload. Never enables. |
| GET | \`/v1/mesh/nodes\` | PROXY Live Nodes roster (5-minute presence). |
| POST | \`/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}\` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |
| GET | \`/v1/health\` | Liveness. Does not increment downloads. |
| GET | \`/v1/skill\` | This markdown. Does not increment downloads. |
| GET | \`/v1/example\` | Sample pair + stamp payload. Does not increment downloads. |
| GET/POST | \`/v1/pair_status\` | Catalog name: pair + report AZBrowser token/flag. Leftover alias: \`/v1/pair\`. |
| GET | \`/v1/garden_list\` | Catalog name: demo Gold Pages. Leftover alias: \`/v1/garden\`. |
| GET | \`/v1/time\` | StaticClock advisory display. Not a scheduler. Human chrome. |
| GET | \`/v1/witness\` | Mandatory UI witness hash. Human chrome. |
| POST | \`/v1/unlock\` | Human chrome: FragGate unlock after pair. Not a catalog live op. |
| POST | \`/v1/stamp\` | TemporalLock-style stamp of a hash. Pair + unlock required. |
| POST | \`/v1/memorial_append\` | Catalog name: terminal memorial. Leftover alias: \`/v1/memorial\`. |
| POST | \`/v1/memorial_list\` | Catalog name: list memorial receipts from the client ledger. |
| POST | \`/v1/withdraw\` | Human chrome: withdrawal over coercion. |
| POST | \`/v1/verify_hash\` | Catalog name: walk hashes and prev links. Leftover alias: \`/v1/verify\`. |
| POST | \`/v1/receipt_verify\` | Catalog name: verify receipt links. Leftover alias: \`/v1/receipts\`. |
| POST | \`/v1/lattice\` | Human chrome: verify receipt links + counts. |
| POST | \`/v1/witness\` | Human chrome: check UI witness. Mismatch terminates + memorial. |

OpenAPI: \`https://aznet-download-tracker.vibelock.workers.dev/openapi.json\`

Catalog OpenAPI: \`https://aziel-runtime.vibelock.workers.dev/openapi.json\`

Catalog MCP: \`POST ${FRAGGATE_MCP}\`

This Worker MCP pointer: \`GET|POST https://aznet-download-tracker.vibelock.workers.dev/mcp\`

Catalog aliases under \`/p/aznet/…\` when listed. FragGate slug: \`aznet\`.

AZBrowser (required pair): \`https://github.com/AzielEliab/azbrowser\`

StaticClock: \`https://staticclock-download-tracker.vibelock.workers.dev/\`

TemporalLock (timeslate lattice): \`https://temporallock-download-tracker.vibelock.workers.dev/\`

FragGate kernel: \`https://github.com/AzielEliab/fraggate\`

Do **not** wire Lumen, AZInterface, AZ-OS Hub, or Interface products.

## How to call (Mozilla/5.0)

\`\`\`bash
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/mcp
curl -s -A 'Mozilla/5.0' -X POST ${FRAGGATE_CALL} \\
  -H 'content-type: application/json' \\
  -d '{"slug":"aznet","op":"pair_status","payload":{"azbrowser":"https://github.com/AzielEliab/azbrowser"}}'
curl -s -A 'Mozilla/5.0' -X POST https://aznet-download-tracker.vibelock.workers.dev/v1/pair_status \\
  -H 'content-type: application/json' \\
  -d '{"azbrowser":"https://github.com/AzielEliab/azbrowser"}'
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/count
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/stats
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/garden_list
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://aznet-download-tracker.vibelock.workers.dev/v1/mesh
\`\`\`

${AI_CLIENTS}

## Local (after one-click install)

\`\`\`bash
curl -fsSL https://aznet-download-tracker.vibelock.workers.dev/install.sh | bash
aznet ui
aznet doctor
\`\`\`

Then open http://127.0.0.1:8771 (this computer only).

## Honest banner

${HONEST}

Cite the GitHub repository and this Worker. No Zenodo DOI is invented here; a software deposit is still needed.

Apache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: hashes only. Not an alt internet.

- Product homepage (workspace + counted download): https://aznet-download-tracker.vibelock.workers.dev/
- Catalog product (when listed): https://aziel-runtime.vibelock.workers.dev/p/aznet/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: \`POST ${FRAGGATE_MCP}\`
- This Worker MCP pointer: \`GET|POST https://aznet-download-tracker.vibelock.workers.dev/mcp\`
- This Worker skill: \`GET https://aznet-download-tracker.vibelock.workers.dev/v1/skill\`
- This Worker OpenAPI: https://aznet-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: \`GET https://aznet-download-tracker.vibelock.workers.dev/v1/example\`

Local UI: Garden Rolodex, Memorial, stamps, receipts, pair-status, FragGate unlock, StaticClock. Device-local \`aznet doctor\` is not a FragGate live op.

${AI_CLIENTS} MCP clients: \`POST https://aziel-runtime.vibelock.workers.dev/mcp\`.

Counted download (gzip HTTP 200, no 302): https://aznet-download-tracker.vibelock.workers.dev/download?asset=aznet-0.1.0.tar.gz
Count JSON: https://aznet-download-tracker.vibelock.workers.dev/count
Stats (\`by_repo\` / \`by_branch\` / \`by_fork\`): https://aznet-download-tracker.vibelock.workers.dev/stats
Isolated counter: Worker \`aznet-download-tracker\`, KV \`AZNET_DOWNLOADS\`. \`/v1\` does not increment.
Hubs list this Worker once live: https://www.azielcorpuslibrary.net/software · https://godlock.uk/software · https://www.azieleliab.com (Software section)
GitHub: https://github.com/AzielEliab/aznet
`;

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version, mcp-session-id, User-Agent, Authorization",
  };
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return HOST;
  }
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

class ReceiptError extends Error { constructor(msg) { super(msg); this.name = "ReceiptError"; } }
class PairError extends Error { constructor(msg) { super(msg); this.name = "PairError"; } }
class WitnessError extends Error { constructor(msg) { super(msg); this.name = "WitnessError"; } }
class InvariantError extends Error { constructor(msg) { super(msg); this.name = "InvariantError"; } }

function utcNow() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function witnessDigest() {
  return sha256Hex(MARKER + "|" + WITNESS_SECTIONS.join("|") + "|" + SPEC);
}

async function advise(now) {
  const stampAt = now || utcNow();
  const zone = "UTC";
  return {
    zone,
    local: stampAt,
    window: "advisory stamp window",
    stamp: await sha256Hex(`${stampAt}|${zone}|${MARKER}`),
    note: "StaticClock stamps time. Not a scheduler.",
    product: "staticclock",
    github: "https://github.com/AzielEliab/staticclock",
    worker: "https://staticclock-download-tracker.vibelock.workers.dev/",
  };
}

function assertNoLeakage(data) {
  for (const key of FORBIDDEN) {
    if (Object.prototype.hasOwnProperty.call(data || {}, key)) {
      throw new InvariantError(`I1: forbidden key ${key} — hashes only`);
    }
  }
  for (const key of ["payload", "keys", "user_content"]) {
    const val = data && data[key];
    if (val != null && val !== "" && val !== ABSENT) {
      throw new InvariantError(`I1: ${key} must be ABSENT`);
    }
  }
}

function validateNote(note) {
  const text = note == null ? "" : String(note);
  if (text.length > 80) throw new InvariantError("note must be ≤80 characters");
  const lowered = text.toLowerCase();
  if (["poc", "payload bytes", "private key", "shellcode"].some((t) => lowered.includes(t))) {
    throw new InvariantError("note must not carry payloads, keys, or attack details");
  }
  return text;
}

function requireHash(name, value) {
  const text = String(value || "").toLowerCase();
  if (!/^[0-9a-f]{64}$/.test(text)) throw new ReceiptError(`${name} must be a 64-char lowercase hex SHA-256`);
  return text;
}

function canonicalObject(record) {
  const payload = {};
  for (const key of HASH_FIELDS) payload[key] = record[key] == null ? null : record[key];
  payload.spec = SPEC;
  payload.marker = MARKER;
  payload.actor = ACTOR;
  payload.payload = ABSENT;
  payload.keys = ABSENT;
  payload.user_content = ABSENT;
  return payload;
}

function sortedJson(payload) {
  const keys = Object.keys(payload).sort();
  return "{" + keys.map((k) => JSON.stringify(k) + ":" + JSON.stringify(payload[k])).join(",") + "}";
}

async function digest(record) {
  return sha256Hex(sortedJson(canonicalObject(record)));
}

async function createReceipt(fields) {
  assertNoLeakage(fields);
  if (!EVENT_KINDS.includes(fields.event_kind)) throw new ReceiptError("event_kind closed set");
  const ts = fields.timestamp || utcNow();
  const payload = {
    actor: ACTOR,
    azbrowser: fields.azbrowser || null,
    aznet_node: fields.aznet_node || null,
    date_stamp: fields.date_stamp || ts.slice(0, 10),
    event_kind: fields.event_kind,
    final_hash: fields.final_hash || null,
    fraggate: fields.fraggate || null,
    genesis_hash: fields.genesis_hash || null,
    hash_hex: fields.hash_hex || null,
    keys: ABSENT,
    label: fields.label || null,
    marker: MARKER,
    note: validateNote(fields.note),
    pair_flag: fields.pair_flag == null ? null : fields.pair_flag,
    pair_status: fields.pair_status || null,
    pair_token: fields.pair_token || null,
    payload: ABSENT,
    prev_hash: fields.prev_hash || GENESIS_PREV_HASH,
    reason: fields.reason || null,
    spec: SPEC,
    staticclock: fields.staticclock || null,
    summary: fields.summary || null,
    timestamp: ts,
    unlock_status: fields.unlock_status || null,
    user_content: ABSENT,
    witness_hash: fields.witness_hash || null,
    zone: fields.zone || "UTC",
  };
  if (payload.event_kind === "MEMORIAL") {
    if (!MEMORIAL_REASONS.includes(payload.reason)) throw new ReceiptError("memorial reason closed set");
    payload.genesis_hash = requireHash("genesis_hash", payload.genesis_hash);
    payload.final_hash = requireHash("final_hash", payload.final_hash);
    payload.summary = payload.reason;
  }
  if (payload.hash_hex) payload.hash_hex = requireHash("hash_hex", payload.hash_hex);
  payload.receipt_hash = await digest(payload);
  return payload;
}

function parseLedger(body) {
  if (body == null) return [];
  let raw = body;
  if (typeof body === "string") {
    const text = body.trim();
    if (!text) return [];
    if (text.startsWith("[")) raw = JSON.parse(text);
    else {
      return text.split("\n").map((l) => l.trim()).filter(Boolean).map((l) => JSON.parse(l));
    }
  }
  if (Array.isArray(raw)) return raw;
  if (raw && typeof raw === "object") {
    if (Array.isArray(raw.ledger)) return raw.ledger;
    if (Array.isArray(raw.chain)) return raw.chain;
    if (Array.isArray(raw.receipts)) return raw.receipts;
  }
  return [];
}

function tipHash(ledger) {
  return ledger.length ? ledger[ledger.length - 1].receipt_hash : GENESIS_PREV_HASH;
}

function genesisHash(ledger) {
  return ledger.length ? ledger[0].receipt_hash : GENESIS_PREV_HASH;
}

function pairStatus(ledger) {
  for (let i = ledger.length - 1; i >= 0; i--) {
    if (ledger[i].event_kind === "PAIR") return ledger[i].pair_status || "UNPAIRED";
  }
  return "UNPAIRED";
}

function unlockStatus(ledger) {
  if (pairStatus(ledger) !== "PAIRED") return "LOCKED";
  for (let i = ledger.length - 1; i >= 0; i--) {
    if (ledger[i].event_kind === "UNLOCK") return ledger[i].unlock_status || "LOCKED";
  }
  return "LOCKED";
}

function pairToken(ledger) {
  for (let i = ledger.length - 1; i >= 0; i--) {
    if (ledger[i].event_kind === "PAIR") return ledger[i].pair_token || null;
  }
  return null;
}

function pairFlag(ledger) {
  return unlockStatus(ledger) === "UNLOCKED" && Boolean(pairToken(ledger));
}

function requireReady(ledger) {
  if (!pairToken(ledger) || pairStatus(ledger) !== "PAIRED") {
    throw new PairError("AZNet + AZBrowser pairing is functional only (pair_token). Products stay separate apps.");
  }
  if (!pairFlag(ledger)) {
    throw new PairError("FragGate pair_flag required. Pairing alone does not open garden/stamp/memorial writes.");
  }
}

function wrap(action, rec, ledger, extra = {}) {
  return {
    product: PRODUCT,
    version: VERSION,
    motto: MOTTO,
    role: ROLE,
    author: AUTHOR,
    spec: SPEC,
    marker: MARKER,
    action,
    receipt: rec,
    ledger,
    chain: ledger,
    pair_status: pairStatus(ledger),
    unlock_status: unlockStatus(ledger),
    ...extra,
  };
}

async function gardenView(now) {
  const clock = await advise(now);
  const cards = [];
  for (let i = 0; i < DEMO_SEEDS.length; i++) {
    cards.push({
      slot: String(i),
      label: `card-${i}`,
      hash_hex: await sha256Hex(DEMO_SEEDS[i]),
      seed_kind: "public-demo-label",
      rank: "none",
      favorite: "forbidden",
    });
  }
  const offset = parseInt(clock.stamp.slice(0, 8), 16) % cards.length;
  const rotated = cards.slice(offset).concat(cards.slice(0, offset)).map((c, i) => ({ ...c, order: String(i) }));
  return {
    name: "Custodian Garden / Gold Pages",
    kind: "shifting non-ranked hash directory",
    hover_reveal: true,
    manual_intent: true,
    favorites: false,
    analytics: false,
    personalization: false,
    payloads: false,
    staticclock: clock,
    cards: rotated,
    note: "Hashes only. Worker is a demo garden. Device-local silent node is the real posture.",
  };
}

async function verify(ledger) {
  const errors = [];
  const n = ledger.length;
  const first = n ? ledger[0].receipt_hash : null;
  const last = n ? ledger[n - 1].receipt_hash : null;
  for (let i = 0; i < n; i++) {
    const rec = ledger[i];
    const copy = { ...rec };
    delete copy.receipt_hash;
    const expected = await digest(copy);
    if (rec.receipt_hash !== expected) errors.push(`index ${i}: stored receipt_hash != recomputed`);
    if (rec.payload !== ABSENT || rec.keys !== ABSENT || rec.user_content !== ABSENT) errors.push(`index ${i}: I1 leakage`);
    if (i === 0) {
      if (rec.prev_hash !== GENESIS_PREV_HASH) errors.push("index 0: prev_hash != GENESIS");
      continue;
    }
    if (rec.prev_hash !== ledger[i - 1].receipt_hash) errors.push(`index ${i}: prev_hash != previous.receipt_hash`);
  }
  return { ok: errors.length === 0, length: n, first_hash: first, last_hash: last, errors };
}

async function doPair(body) {
  assertNoLeakage(body);
  const ledger = parseLedger(body);
  const clock = await advise(body.timestamp);
  const azbrowser = body.azbrowser || "https://github.com/AzielEliab/azbrowser";
  const aznetNode = body.aznet_node || "demo-garden";
  const token = await sha256Hex(`${aznetNode}|${azbrowser}|${MARKER}|${clock.local}`);
  const rec = await createReceipt({
    event_kind: "PAIR",
    prev_hash: tipHash(ledger),
    timestamp: clock.local,
    pair_status: "PAIRED",
    pair_token: token,
    pair_flag: false,
    unlock_status: "LOCKED",
    azbrowser,
    aznet_node: aznetNode,
    fraggate: "required",
    staticclock: clock.stamp,
    zone: clock.zone,
    note: body.note || "pair_token issued. Separate apps. FragGate pair_flag still required.",
  });
  return wrap("paired", rec, [...ledger, rec]);
}

async function doUnlock(body) {
  const ledger = parseLedger(body);
  const token = pairToken(ledger);
  if (pairStatus(ledger) !== "PAIRED" || !token) throw new PairError("FragGate pair_flag requires an AZNet pair_token first. Apps stay separate.");
  const clock = await advise(body.timestamp);
  const rec = await createReceipt({
    event_kind: "UNLOCK",
    prev_hash: tipHash(ledger),
    timestamp: clock.local,
    pair_status: "PAIRED",
    pair_token: token,
    pair_flag: true,
    unlock_status: "UNLOCKED",
    azbrowser: "https://github.com/AzielEliab/azbrowser",
    fraggate: "unlocked",
    staticclock: clock.stamp,
    zone: clock.zone,
    note: body.note || "pair_flag set. FragGate order only. Side-net remains hash-only.",
  });
  return wrap("unlocked", rec, [...ledger, rec]);
}

async function doStamp(body) {
  const ledger = parseLedger(body);
  requireReady(ledger);
  const clock = await advise(body.timestamp);
  const rec = await createReceipt({
    event_kind: "STAMP",
    prev_hash: tipHash(ledger),
    timestamp: clock.local,
    hash_hex: body.hash_hex || body.hash,
    pair_status: "PAIRED",
    pair_token: pairToken(ledger),
    pair_flag: true,
    unlock_status: "UNLOCKED",
    staticclock: clock.stamp,
    zone: clock.zone,
    note: body.note || "TemporalLock-style stamp. Hash only.",
  });
  return wrap("stamped", rec, [...ledger, rec]);
}

async function doMemorial(body) {
  const ledger = parseLedger(body);
  const clock = await advise(body.timestamp);
  const rec = await createReceipt({
    event_kind: "MEMORIAL",
    prev_hash: tipHash(ledger),
    timestamp: clock.local,
    genesis_hash: body.genesis_hash || genesisHash(ledger),
    final_hash: body.final_hash || tipHash(ledger),
    reason: body.reason || "isolation",
    pair_status: pairStatus(ledger),
    pair_token: pairToken(ledger),
    pair_flag: pairFlag(ledger),
    unlock_status: unlockStatus(ledger),
    staticclock: clock.stamp,
    zone: clock.zone,
    note: body.note || "Terminal compromise memorial. Non-actionable summary only.",
  });
  return wrap("memorial", rec, [...ledger, rec]);
}

async function doWithdraw(body) {
  const ledger = parseLedger(body);
  const clock = await advise(body.timestamp);
  const rec = await createReceipt({
    event_kind: "WITHDRAW",
    prev_hash: tipHash(ledger),
    timestamp: clock.local,
    pair_status: pairStatus(ledger),
    unlock_status: "LOCKED",
    staticclock: clock.stamp,
    zone: clock.zone,
    note: body.note || "Withdrawal over coercion. Node silent.",
  });
  return wrap("withdrawn", rec, [...ledger, rec]);
}

async function doWitness(body) {
  const ledger = parseLedger(body);
  const expected = await witnessDigest();
  const clock = await advise(body.timestamp);
  if (!body.witness_hash || body.witness_hash !== expected) {
    const mem = await createReceipt({
      event_kind: "MEMORIAL",
      prev_hash: tipHash(ledger),
      timestamp: clock.local,
      genesis_hash: genesisHash(ledger),
      final_hash: tipHash(ledger),
      reason: "ui_altered",
      pair_status: pairStatus(ledger),
      unlock_status: unlockStatus(ledger),
      staticclock: clock.stamp,
      zone: clock.zone,
      note: "UI witness failed. Terminated. Memorial written.",
    });
    throw Object.assign(new WitnessError("UI witness failed. Terminated. Memorial written. " + MARKER), {
      memorial: mem,
      ledger: [...ledger, mem],
    });
  }
  const rec = await createReceipt({
    event_kind: "WITNESS",
    prev_hash: tipHash(ledger),
    timestamp: clock.local,
    witness_hash: expected,
    pair_status: pairStatus(ledger),
    unlock_status: unlockStatus(ledger),
    staticclock: clock.stamp,
    zone: clock.zone,
    note: "UI witness intact.",
  });
  return wrap("witness", rec, [...ledger, rec], { witness_hash: expected });
}

function mcpDocs(origin) {
  return {
    ok: false,
    error: "not a product MCP",
    product: PRODUCT,
    door: "fraggate",
    slug: "aznet",
    identity: AUTHOR,
    agent_path: FRAGGATE_CALL,
    catalog_mcp: FRAGGATE_MCP,
    body: { slug: "aznet", op: "pair_status", payload: { azbrowser: AZBROWSER } },
    openapi: origin + "/openapi.json",
    mesh: meshPointer(),
    mesh_body: { slug: "mesh", op: "status", payload: {} },
    note: "AI / MCP path is FragGate only. This host GET|POST /mcp is a pointer (never 404), not a second agent brand. /v1/fraggate/*, /v1/runtime/*, and /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Local ops are /v1/{op} only. Catalog LIVE_OPS: " + FRAGGATE_LIVE_OPS.join(", ") + ". Catalog MCP mesh_* + FragGate slug=mesh. Suite mesh default OFF. QNM rollup live|locked|isolated. QNS-CD-1.0 photon QNS1 cite only — no public qnsd proxy. No Node Gate. No auto-heal. Not anonymity. AZBrowser is sibling software (functional-order pair), not this product. doctor is not a FragGate live op.",
    ops: [...FRAGGATE_LIVE_OPS],
    live_ops: [...FRAGGATE_LIVE_OPS],
    fraggate_live_ops: [...FRAGGATE_LIVE_OPS],
    leftover_aliases: { ...LEFTOVER_ALIASES },
    limitation: HONEST,
    kernel: FRAGGATE_KERNEL,
    separate_from: "azbrowser",
  };
}

function runtimeFetcher(env) {
  if (env && env.AZIEL_RUNTIME && typeof env.AZIEL_RUNTIME.fetch === "function") return env.AZIEL_RUNTIME;
  return null;
}

async function proxyDoor(request, url, env) {
  const dest = doorTargetUrl(url.pathname, request.url, env);
  if (!dest) {
    return json({ ok: false, error: "not a door path", path: url.pathname, limitation: HONEST }, 404);
  }
  const headers = new Headers();
  const pass = ["content-type", "accept", "authorization", "user-agent", "mcp-protocol-version", "mcp-session-id", "x-aziel-runtime-token"];
  for (const name of pass) {
    const v = request.headers.get(name);
    if (v) headers.set(name, v);
  }
  if (!headers.has("User-Agent")) headers.set("User-Agent", "Mozilla/5.0 AZNet/0.1.0");
  const init = { method: request.method, headers, redirect: "follow" };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
    init.duplex = "half";
  }
  try {
    const fetcher = runtimeFetcher(env);
    const res = fetcher ? await fetcher.fetch(dest, init) : await fetch(dest, init);
    const outHeaders = new Headers(res.headers);
    for (const [k, v] of Object.entries(corsHeaders())) outHeaders.set(k, v);
    outHeaders.set("X-Aziel-Door", "proxy");
    outHeaders.set("X-Aziel-Door-Origin", dest);
    if (request.method === "GET" && isMeshLiveNodesPath(url.pathname)) {
      try {
        const parsed = await res.clone().json();
        const attached = attachQnsCdCrossMap(parsed);
        outHeaders.set("Content-Type", "application/json; charset=utf-8");
        outHeaders.delete("Content-Length");
        return new Response(JSON.stringify(attached, null, 2), {
          status: res.status,
          statusText: res.statusText,
          headers: outHeaders,
        });
      } catch {
        /* keep the proxied body if it is not JSON */
      }
    }
    return new Response(res.body, { status: res.status, statusText: res.statusText, headers: outHeaders });
  } catch (exc) {
    return json({
      ok: false,
      error: "fraggate_proxy_failed",
      detail: String(exc).slice(0, 240),
      origin: dest,
      agent_path: FRAGGATE_CALL,
      limitation: HONEST,
    }, 502);
  }
}

async function doPairStatus(body, method) {
  if (method === "GET") {
    const ledger = parseLedger(body || {});
    return {
      ok: true,
      product: PRODUCT,
      version: VERSION,
      author: AUTHOR,
      action: "pair_status",
      pair_status: pairStatus(ledger),
      unlock_status: unlockStatus(ledger),
      pair_token: pairToken(ledger) ? "present" : "absent",
      pair_flag: pairFlag(ledger),
      peer: "azbrowser",
      separate_software: true,
      fraggate_live_ops: [...FRAGGATE_LIVE_OPS],
    };
  }
  return doPair(body || {});
}

async function doMemorialList(body) {
  const ledger = parseLedger(body || {});
  const memorials = ledger.filter((row) => row && row.event_kind === "MEMORIAL");
  return {
    ok: true,
    product: PRODUCT,
    version: VERSION,
    author: AUTHOR,
    action: "memorial_list",
    memorials,
    length: memorials.length,
    pair_status: pairStatus(ledger),
    unlock_status: unlockStatus(ledger),
    note: "Append-only memorial list from the client-held ledger. No rewrite.",
  };
}

async function doReceiptVerify(body) {
  const ledger = parseLedger(body || {});
  const rec = await verify(ledger);
  return {
    product: PRODUCT,
    version: VERSION,
    author: AUTHOR,
    action: "receipt_verify",
    pair_status: pairStatus(ledger),
    unlock_status: unlockStatus(ledger),
    length: ledger.length,
    ...rec,
  };
}

function openapiSpec(origin) {
  const ledgerSchema = { oneOf: [{ type: "array", items: { type: "object" } }, { type: "string" }] };
  return {
    openapi: "3.1.0",
    info: {
      title: "AZNet runtime",
      version: VERSION,
      summary: "Dual surface. Human UI is this Worker /v1. AI / MCP path is FragGate only (slug=aznet).",
      description: HONEST + " Agent door is FragGate only: POST " + FRAGGATE_CALL + " {slug:aznet,op,payload}. Catalog MCP: POST " + FRAGGATE_MCP + ". This host /mcp is a pointer, not a second agent brand. Catalog LIVE_OPS: " + FRAGGATE_LIVE_OPS.join(", ") + ". AZBrowser is sibling software. Suite mesh /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 cite only. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Aziel Eliab only.",
      license: { name: "Apache-2.0", identifier: "Apache-2.0" },
      contact: { name: AUTHOR, url: "https://github.com/AzielEliab/aznet" },
    },
    servers: [{ url: origin || HOST }, { url: RUNTIME, description: "aziel-runtime FragGate catalog" }],
    paths: {
      "/count": { get: { operationId: "count", summary: "Live {views, downloads, total}. Does not increment.", responses: { "200": { description: "count" } } } },
      "/stats": { get: { operationId: "stats", summary: "views, downloads, by_repo / by_branch / by_fork. Does not increment.", responses: { "200": { description: "stats" } } } },
      "/download": { get: { operationId: "download", summary: "Counted tarball. HTTP 200, live counter, no 302.", responses: { "200": { description: "gzip" } } } },
      "/mcp": {
        get: { operationId: "aznet_mcp_docs", summary: "MCP docs + FragGate pointer. Never 404.", responses: { "200": { description: "docs" } } },
        post: { operationId: "aznet_mcp", summary: "JSON-RPC MCP-over-HTTP pointer. Same catalog ops as UI.", responses: { "200": { description: "rpc" } } },
      },
      "/v1/skill": { get: { operationId: "aznet_skill", summary: "Return skill markdown. Does not increment download KV.", responses: { "200": { description: "markdown" } } } },
      "/v1/health": { get: { operationId: "health", summary: "Liveness", responses: { "200": { description: "ok" } } } },
      "/v1/pair_status": { get: { operationId: "pair_status_get", summary: "Report AZBrowser pair token + flag.", responses: { "200": { description: "status" } } }, post: { operationId: "pair_status", summary: "FragGate catalog name. Pair AZNet + AZBrowser, then report status. Leftover alias: /v1/pair.", requestBody: { content: { "application/json": { schema: { type: "object", properties: { azbrowser: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "paired" } } } },
      "/v1/garden_list": { get: { operationId: "garden_list", summary: "FragGate catalog name. Demo Gold Pages. Leftover alias: /v1/garden.", responses: { "200": { description: "garden" } } } },
      "/v1/time": { get: { operationId: "time", summary: "StaticClock advisory display. Human chrome.", responses: { "200": { description: "time" } } } },
      "/v1/witness": { get: { operationId: "witness_get", summary: "Mandatory UI witness hash.", responses: { "200": { description: "witness" } } } },
      "/v1/pair": { post: { operationId: "pair", summary: "Leftover alias of pair_status.", requestBody: { content: { "application/json": { schema: { type: "object", properties: { azbrowser: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "paired" } } } },
      "/v1/unlock": { post: { operationId: "unlock", summary: "Human chrome: FragGate unlock after pair. Not a catalog live op.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "unlocked" } } } },
      "/v1/stamp": { post: { operationId: "stamp", summary: "Stamp a hash. Pair + unlock required.", requestBody: { required: true, content: { "application/json": { schema: { type: "object", required: ["hash_hex"], properties: { hash_hex: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "stamped" } } } },
      "/v1/memorial_append": { post: { operationId: "memorial_append", summary: "FragGate catalog name. Terminal memorial. Leftover alias: /v1/memorial.", requestBody: { content: { "application/json": { schema: { type: "object", properties: { reason: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "memorial" } } } },
      "/v1/memorial_list": { post: { operationId: "memorial_list", summary: "List memorial receipts from the client-held ledger.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "memorials" } } } },
      "/v1/memorial": { post: { operationId: "memorial", summary: "Leftover alias of memorial_append.", requestBody: { content: { "application/json": { schema: { type: "object", properties: { reason: { type: "string" }, ledger: ledgerSchema } } } } }, responses: { "200": { description: "memorial" } } } },
      "/v1/withdraw": { post: { operationId: "withdraw", summary: "Human chrome: withdrawal over coercion.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "withdrawn" } } } },
      "/v1/verify_hash": { post: { operationId: "verify_hash", summary: "FragGate catalog name. Walk hashes and links. Leftover alias: /v1/verify.", requestBody: { content: { "application/json": { schema: { type: "object", properties: { ledger: ledgerSchema } } } } }, responses: { "200": { description: "verify" } } } },
      "/v1/verify": { post: { operationId: "verify", summary: "Leftover alias of verify_hash.", requestBody: { content: { "application/json": { schema: { type: "object", properties: { ledger: ledgerSchema } } } } }, responses: { "200": { description: "verify" } } } },
      "/v1/receipt_verify": { post: { operationId: "receipt_verify", summary: "FragGate catalog name. Verify receipt links. Leftover alias: /v1/receipts.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "verify" } } } },
      "/v1/lattice": { post: { operationId: "lattice", summary: "Human chrome: verify receipt links + counts.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "lattice" } } } },
      "/v1/receipts": { post: { operationId: "receipts", summary: "Leftover alias of receipt_verify / return the client-held ledger.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "receipts" } } } },
      "/v1/example": { get: { operationId: "example", summary: "Sample pair payload.", responses: { "200": { description: "example" } } } },
      "/v1/fraggate/call": { post: { operationId: "aznet_fraggate_call_proxy", summary: "PROXY to aziel-runtime POST /v1/fraggate/call. Not a local op.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "FragGate ResultEnvelope" } } } },
      "/v1/fraggate/list": { get: { operationId: "aznet_fraggate_list_proxy", summary: "PROXY to aziel-runtime GET /v1/fraggate/list. Not a local op.", responses: { "200": { description: "hashed registry" } } } },
      "/v1/fraggate/describe": { get: { operationId: "aznet_fraggate_describe_proxy", summary: "PROXY to aziel-runtime GET /v1/fraggate/describe. Not a local op.", responses: { "200": { description: "catalog entry" } } } },
      "/v1/fraggate/verify": { post: { operationId: "aznet_fraggate_verify_proxy", summary: "PROXY to aziel-runtime POST /v1/fraggate/verify. Not a local op.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "verify" } } } },
      "/v1/runtime/call": { post: { operationId: "aznet_runtime_call_proxy", summary: "Alias PROXY → origin /v1/fraggate/call. Not a local op.", requestBody: { content: { "application/json": { schema: { type: "object" } } } }, responses: { "200": { description: "FragGate ResultEnvelope" } } } },
      "/v1/runtime/list": { get: { operationId: "aznet_runtime_list_proxy", summary: "Alias PROXY → origin /v1/fraggate/list. Not a local op.", responses: { "200": { description: "hashed registry" } } } },
      ...meshOpenApiPaths(),
    },
  };
}

function aiHtml(origin) {
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZNet — Aziel Eliab · AI runtime</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.25rem 3rem; background: #000; color: #fff; }
  code { background: #151922; padding: .15rem .4rem; border-radius: 4px; }
  a { color: #c9a227; }
  .motto { color: #c9a227; font-style: italic; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; }
  pre { background: #141414; padding: .85rem 1rem; overflow: auto; border-radius: 8px; }
  .brandrow{display:flex;align-items:center;gap:12px;margin:0 0 10px}
  .brandmark{width:40px;height:40px;border-radius:10px;object-fit:cover;flex:0 0 auto;box-shadow:0 0 0 1px #d4af3733}
  .stamp{margin:0;color:#c9a227;font-size:.88rem}
</style>
<body>
  <div class="brandrow">
    <img class="brandmark" src="/sigil.png" width="40" height="40" alt="" decoding="async">
    <p class="stamp">Aziel Eliab</p>
  </div>
  <h1>AZNet dual surface</h1>
  <p class="motto">${MOTTO}</p>
  <p class="banner">${HONEST}</p>
  <h2>Use with AI assistants</h2>
  <p>${AI_CLIENTS} Author ${AUTHOR} only.</p>
  <p>Agent path is FragGate only (one door). This Worker <code>/mcp</code> is a pointer, not a second MCP. AZBrowser is sibling software — functional-order pair only.</p>
  <pre>POST ${FRAGGATE_CALL}
{"slug":"aznet","op":"pair_status","payload":{"azbrowser":"${AZBROWSER}"}}</pre>
  <h2>OpenAPI import</h2>
  <p>Paste this OpenAPI URL into GPT Actions, custom HTTP tools, Grok custom tools, or any other OpenAPI-capable assistant:</p>
  <p><code>${origin}/openapi.json</code></p>
  <p>Human chrome catalog names: <code>POST ${origin}/v1/pair_status</code>, <code>/v1/garden_list</code>, <code>/v1/stamp</code>, <code>/v1/verify_hash</code>, <code>/v1/memorial_append</code>, <code>/v1/receipt_verify</code>.</p>
  <h2>MCP catalog</h2>
  <p>Catalog MCP: <code>POST ${FRAGGATE_MCP}</code> (includes <code>mesh_*</code> + FragGate <code>slug=mesh</code>). This Worker <code>/mcp</code> is a pointer. FragGate slug: <code>aznet</code>.</p>
  <p>Suite mesh: <code>GET ${origin}/v1/mesh</code> PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 cite only (qnm-node + aziel-runtime). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Author: ${AUTHOR} only.</p>
  <p><a href="/openapi.json">openapi.json</a> · <a href="/mcp">/mcp pointer</a> · <a href="/v1/health">health</a> · <a href="/v1/fraggate/list">FragGate list</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/">AZNet software</a> · <a href="/cite.json">cite.json</a></p>
</body>
</html>`;
}

export async function handleRuntimeApi(request, url, env) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  const isApi = path === "/v1" || path.startsWith("/v1/") || path === "/openapi.json" || path === "/ai" || path === "/mcp";
  if (!isApi) return null;
  try {
    if (path === "/mcp" && (request.method === "GET" || request.method === "POST")) {
      return json(mcpDocs(originOf(request)));
    }
    if (path === "/v1/health" && request.method === "GET") {
      return json({
        ok: true,
        product: PRODUCT,
        version: VERSION,
        author: AUTHOR,
        role: ROLE,
        motto: MOTTO,
        spec: SPEC,
        marker: MARKER,
        door: "fraggate",
        slug: "aznet",
        agent_path: FRAGGATE_CALL,
        fraggate_live_ops: [...FRAGGATE_LIVE_OPS],
        pair: "AZNet + AZBrowser both required",
        separate_software: true,
        worker_posture: "control-plane / demo garden",
        mesh: meshPointer(),
        note: "Hosted /v1 does not store ledgers. Hashes only. Device-local silent node is the real posture. Agent path is FragGate only. Suite mesh /v1/mesh/* PROXY to aziel-runtime. Default OFF. QNS-CD-1.0 is a hub cite / Worker mesh cross-map only.",
      });
    }
    if (path === "/v1/skill" && request.method === "GET") {
      return new Response(SKILL, { status: 200, headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...corsHeaders() } });
    }
    if (path === "/openapi.json" && request.method === "GET") return json(openapiSpec(originOf(request)));
    if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
      return new Response(aiHtml(originOf(request)), { headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() } });
    }

    const classified = classifyV1Path(url.pathname);
    if (classified.kind === "door") {
      return proxyDoor(request, url, env);
    }
    if (classified.kind === "multi") {
      return json({
        ok: false,
        error: "not a local op",
        code: "NOT_LOCAL_OP",
        path: classified.path,
        hint: "Local ops are POST|GET /v1/{op} only (single segment). FragGate door is /v1/fraggate/* (proxied to aziel-runtime). /v1/runtime/list and /v1/runtime/call alias that door. Suite mesh is /v1/mesh/* (proxied to aziel-runtime; default OFF).",
        agent_path: FRAGGATE_CALL,
        ops: [...FRAGGATE_LIVE_OPS],
        limitation: HONEST,
      }, 404);
    }

    if (path === "/v1/example" && request.method === "GET") {
      return json({ azbrowser: AZBROWSER, hash_hex: "a".repeat(64), author: AUTHOR, spec: SPEC, marker: MARKER, op: "pair_status" });
    }
    if ((path === "/v1/garden" || path === "/v1/garden_list") && request.method === "GET") return json(await gardenView());
    if (path === "/v1/time" && request.method === "GET") return json(await advise());
    if (path === "/v1/witness" && request.method === "GET") {
      return json({ marker: MARKER, spec: SPEC, sections: WITNESS_SECTIONS, witness_hash: await witnessDigest() });
    }
    if (path === "/v1/pair_status" && request.method === "GET") return json(await doPairStatus({}, "GET"));
    async function readBody() {
      try { return await request.json(); } catch { return {}; }
    }
    if ((path === "/v1/pair_status" || path === "/v1/pair") && request.method === "POST") {
      return json(await doPairStatus(await readBody(), "POST"));
    }
    if (path === "/v1/unlock" && request.method === "POST") return json(await doUnlock(await readBody()));
    if (path === "/v1/stamp" && request.method === "POST") return json(await doStamp(await readBody()));
    if ((path === "/v1/memorial_append" || path === "/v1/memorial") && request.method === "POST") return json(await doMemorial(await readBody()));
    if (path === "/v1/memorial_list" && (request.method === "POST" || request.method === "GET")) return json(await doMemorialList(request.method === "GET" ? {} : await readBody()));
    if (path === "/v1/withdraw" && request.method === "POST") return json(await doWithdraw(await readBody()));
    if (path === "/v1/witness" && request.method === "POST") return json(await doWitness(await readBody()));
    if (path === "/v1/receipt_verify" && request.method === "POST") return json(await doReceiptVerify(await readBody()));
    if (path === "/v1/receipts" && request.method === "POST") {
      const body = await readBody();
      const ledger = parseLedger(body);
      return json({ product: PRODUCT, version: VERSION, author: AUTHOR, action: "receipts", ledger, length: ledger.length, pair_status: pairStatus(ledger), unlock_status: unlockStatus(ledger) });
    }
    if ((path === "/v1/verify_hash" || path === "/v1/verify") && request.method === "POST") {
      const ledger = parseLedger(await readBody());
      return json({ product: PRODUCT, version: VERSION, motto: MOTTO, role: ROLE, author: AUTHOR, action: "verify_hash", ...(await verify(ledger)) });
    }
    if (path === "/v1/lattice" && request.method === "POST") {
      const ledger = parseLedger(await readBody());
      const rec = await verify(ledger);
      const counts = { GARDEN: 0, STAMP: 0, MEMORIAL: 0, PAIR: 0, UNLOCK: 0 };
      for (const item of ledger) {
        if (counts[item.event_kind] != null) counts[item.event_kind] += 1;
      }
      return json({ product: PRODUCT, version: VERSION, author: AUTHOR, ...rec, garden: counts.GARDEN, stamps: counts.STAMP, memorials: counts.MEMORIAL, pairs: counts.PAIR, unlocks: counts.UNLOCK, note: HONEST });
    }
    if (path === "/v1/garden_list" && request.method === "POST") return json(await gardenView());
    return json({
      error: "not found",
      hint: "GET /v1/health GET /v1/skill POST /v1/{catalog_op} GET /v1/fraggate/list POST /v1/fraggate/call GET /v1/mesh GET /openapi.json GET|POST /mcp",
      ops: [...FRAGGATE_LIVE_OPS],
      leftover_aliases: { ...LEFTOVER_ALIASES },
      limitation: HONEST,
    }, 404);
  } catch (err) {
    const status = err instanceof PairError || err instanceof WitnessError ? 409 : 400;
    const extra = err.memorial ? { memorial: err.memorial, ledger: err.ledger } : {};
    return json({ error: String(err.message || err), motto: MOTTO, marker: MARKER, ok: false, ...extra }, status);
  }
}

export { SKILL, MARKER, WITNESS_SECTIONS, HONEST, MOTTO, FRAGGATE_LIVE_OPS, FRAGGATE_CALL, FRAGGATE_MCP };
