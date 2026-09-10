/**
 * AZNet product homepage — software UI, not a downloads shell.
 * Black background, white text, gold trim. UI is a mandatory witness.
 * Author: Aziel Eliab only. Apache-2.0. Forks welcome.
 * No Zenodo DOI is invented here.
 */

const HOST = "https://aznet-download-tracker.vibelock.workers.dev";
const GITHUB_REPO = "https://github.com/AzielEliab/aznet";
const GITHUB_LATEST = "https://github.com/AzielEliab/aznet/releases/latest";
const AZBROWSER = "https://github.com/AzielEliab/azbrowser";
const CATALOG = "https://aziel-runtime.vibelock.workers.dev/";
const CATALOG_PRODUCT = "https://aziel-runtime.vibelock.workers.dev/p/aznet/";
const LIBRARY = "https://www.azielcorpuslibrary.net/";
const STATICCLOCK_HOST = "https://staticclock-download-tracker.vibelock.workers.dev";
const TEMPORALLOCK_HOST = "https://temporallock-download-tracker.vibelock.workers.dev";
const FRAGGATE = "https://github.com/AzielEliab/fraggate";
const LICENSE = "https://www.apache.org/licenses/LICENSE-2.0";
const VERSION = "0.1.0";
const AUTHOR = "Aziel Eliab";
const AUTHOR_AKA = "Aziel Elroi Eliab";
const AI_CLIENTS =
  "ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants";

/**
 * Aziel Eliab AI Allow policy. Hardcoded crawler names only.
 * Never interpolate fs/readdir, ASSETS listings, or workspace directory names.
 */
export const AI_CRAWLER_AGENTS = Object.freeze([
  "GPTBot",
  "ChatGPT-User",
  "OAI-SearchBot",
  "Google-Extended",
  "Googlebot",
  "GoogleOther",
  "Google-CloudVertexBot",
  "ClaudeBot",
  "Claude-SearchBot",
  "Claude-User",
  "anthropic-ai",
  "PerplexityBot",
  "Perplexity-User",
  "bingbot",
  "Meta-ExternalAgent",
  "Meta-ExternalFetcher",
  "Meta-WebIndexer",
  "FacebookBot",
  "facebookexternalhit",
  "Meta-ExternalAds",
  "Applebot",
  "Applebot-Extended",
  "Amazonbot",
  "DuckDuckBot",
  "DuckAssistBot",
  "MistralAI-User",
  "YouBot",
  "CCBot",
  "cohere-ai",
  "cohere-training-data-crawler",
  "Diffbot",
  "AI2Bot",
  "AI2Bot-Dolma",
  "Timpibot",
  "Petalbot",
  "Bytespider",
  "Omgili",
  "Omgilibot",
  "FirecrawlAgent",
  "ImagesiftBot",
  "Cloudflare-AI-Search",
  "TikTokSpider",
  "Baiduspider",
  "Baiduspider-render",
  "Baiduspider-ai",
  "YandexBot",
  "PanguBot",
  "Kangaroo Bot",
  "Cotoyogi",
  "aiHitBot",
  "webzio-extended",
  "ICC-Crawler",
  "DataForSeoBot",
  "AwarioBot",
  "AwarioSmartBot",
  "AwarioRssBot",
  "Sentibot",
  "peer39_crawler",
  "Seekr",
  "Meltwater",
  "TurnitinBot",
  "Factset_spyderbot",
  "NeevaBot",
]);

export function uniqueUserAgents(agents) {
  const seen = new Set();
  const out = [];
  for (const agent of agents) {
    const key = String(agent).toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(agent);
  }
  return out;
}

const TITLE = "AZNet — Aziel Eliab";
const DEFAULT_ASSET = "aznet-0.1.0.tar.gz";
const INSTALL_LINE = "curl -fsSL https://aznet-download-tracker.vibelock.workers.dev/install.sh | bash";
const MARKER = "Truth Is No Defense — .AZNet — AZ.";
const DESCRIPTION =
  "AZNet is Aziel Eliab software: a silent verification SIDE-NET (AZN-WP-0.1). Hashes only. AZNet + AZBrowser required. FragGate unlocks access. StaticClock stamps time. Apache-2.0.";
const HONEST =
  "THIS IS: a silent verification SIDE-NET (hash continuity, Custodian Garden, Memorial ledger). THIS IS NOT: an alt internet, a host, a payload store, a VPN, or a key store. The Worker is a control-plane / demo garden. Device-local silent node is the real posture. AZNet + AZBrowser are both required. Author Aziel Eliab.";
const HOW_TO_CITE =
  "Eliab, Aziel. (2026). AZNet 0.1.0 [Software]. Apache-2.0. https://github.com/AzielEliab/aznet · https://aznet-download-tracker.vibelock.workers.dev/";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function citePayload() {
  return {
    author: AUTHOR,
    title: "AZNet",
    version: VERSION,
    homepage: HOST + "/",
    github: GITHUB_REPO,
    download: HOST + "/download",
    install: HOST + "/install.sh",
    openapi: HOST + "/openapi.json",
    skill: HOST + "/v1/skill",
    catalog: CATALOG,
    catalog_product: CATALOG_PRODUCT,
    library: LIBRARY,
    aka: AUTHOR_AKA,
    azbrowser: AZBROWSER,
    license: "Apache-2.0",
    license_url: LICENSE,
    one_line: DESCRIPTION,
    how_to_cite: HOW_TO_CITE,
    apa: "Eliab, A. (2026). AZNet (Version 0.1.0) [Computer software]. https://aznet-download-tracker.vibelock.workers.dev/",
    bibtex:
      "@software{eliab_aznet_2026, author = {Eliab, Aziel}, title = {AZNet}, version = {0.1.0}, year = {2026}, license = {Apache-2.0}, url = {https://aznet-download-tracker.vibelock.workers.dev/}, publisher = {GitHub}, howpublished = {\\url{https://github.com/AzielEliab/aznet}}}",
    zenodo_status: "placeholder_no_doi_invented",
    software_deposit_needed: true,
    note: "No DOI is invented here. Cite GitHub and this Worker. Identity is Aziel Eliab only. Forks welcome.",
    identity: "Aziel Eliab only",
    forks: "welcome and always allowed",
    marker: MARKER,
  };
}

export function jsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "AZNet",
    alternateName: TITLE,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Linux, macOS, Windows, Cloudflare Workers",
    softwareVersion: VERSION,
    author: { "@type": "Person", name: AUTHOR, alternateName: AUTHOR_AKA, url: "https://github.com/AzielEliab" },
    creator: { "@type": "Person", name: AUTHOR, alternateName: AUTHOR_AKA, url: "https://github.com/AzielEliab" },
    codeRepository: GITHUB_REPO,
    downloadUrl: HOST + "/download",
    installUrl: HOST + "/install.sh",
    license: LICENSE,
    url: HOST + "/",
    description: DESCRIPTION,
    keywords: "AZNet, silent verification, side-net, Custodian Garden, Gold Pages, Memorial ledger, Aziel Eliab, AZN-WP-0.1",
    isAccessibleForFree: true,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    sameAs: [GITHUB_REPO, CATALOG_PRODUCT, AZBROWSER],
  };
}

export function sitemapXml() {
  const paths = ["/", "/download", "/count", "/stats", "/install.sh", "/mcp", "/v1/skill", "/v1/example", "/v1/health", "/v1/garden_list", "/v1/fraggate/list", "/v1/mesh", "/openapi.json", "/cite.json", "/llms.txt", "/ai.txt", "/ai"];
  const urls = paths.map((p) => `  <url><loc>${HOST}${p === "/" ? "/" : p}</loc></url>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
  <url><loc>${GITHUB_REPO}</loc></url>
</urlset>
`;
}

export function robotsTxt() {
  const lines = ["User-agent: *", "Allow: /", "Content-Signal: search=yes, ai-input=yes, ai-train=yes", ""];
  for (const agent of uniqueUserAgents(AI_CRAWLER_AGENTS)) {
    lines.push("User-agent: " + agent);
    lines.push("Allow: /");
  }
  lines.push("");
  lines.push("Sitemap: " + HOST + "/sitemap.xml");
  lines.push("");
  return lines.join("\n");
}

export function llmsTxt() {
  return `# AZNet

Author: Aziel Eliab
Also known as: ${AUTHOR_AKA} (alternateName only)
One-line: ${DESCRIPTION}
GitHub: ${GITHUB_REPO}
Homepage: ${HOST}/
Download: ${HOST}/download
Count: ${HOST}/count
Stats: ${HOST}/stats
Install: ${HOST}/install.sh
OpenAPI: ${HOST}/openapi.json
Skill: ${HOST}/v1/skill
Cite: ${HOST}/cite.json
Library: ${LIBRARY}
Catalog: ${CATALOG}
Agent path: FragGate only — POST ${CATALOG}v1/fraggate/call {slug:aznet,op,payload}
This Worker /mcp is a pointer, not a second MCP.
Catalog LIVE_OPS: health, pair_status, garden_list, stamp, verify_hash, memorial_list, memorial_append, receipt_verify, skill
Suite mesh: GET ${HOST}/v1/mesh PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 cite only (qnm-node + aziel-runtime; pair custody cite). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Catalog MCP mesh_* + FragGate slug=mesh.
Human chrome leftovers: unlock, time, witness, lattice, withdraw
doctor is not a FragGate live op (local CLI only).
AZNet is separate software from AZBrowser.
Pair: AZNet + AZBrowser both required
Marker: ${MARKER}
Identity: Aziel Eliab only
License: Apache-2.0
Forks: welcome and always allowed
DOI: none invented; software deposit still needed.
AI clients: ${AI_CLIENTS}.
robots.txt: User-agent * Allow / plus GPTBot, ChatGPT-User, Google-Extended, Claude, Perplexity, and the rest of the Aziel Eliab AI Allow set. No GPTBot Disallow.

Indexing, metadata scrape, and AI grounding of public pages are allowed.
`;
}

function seoPath(pathname) {
  if (pathname.length > 1 && pathname.endsWith("/")) return pathname.slice(0, -1);
  return pathname;
}

export function handleSeoRoutes(request, url) {
  if (request.method !== "GET" && request.method !== "HEAD") return null;
  const headers = { ...corsHeaders(), "Cache-Control": "private, no-store" };
  const path = seoPath(url.pathname);
  if (path === "/cite.json" || path === "/cite") {
    return new Response(JSON.stringify(citePayload(), null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8", ...headers },
    });
  }
  if (path === "/sitemap.xml") {
    return new Response(sitemapXml(), { status: 200, headers: { "Content-Type": "application/xml; charset=utf-8", ...headers } });
  }
  if (path === "/robots.txt") {
    return new Response(robotsTxt(), { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
  }
  if (path === "/llms.txt" || path === "/ai.txt") {
    return new Response(llmsTxt(), { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
  }
  return null;
}

function breakdownList(stats) {
  const rows = stats.breakdown || [];
  if (!rows.length) return "<li>none yet</li>";
  return rows
    .map((b) => `<li><code>${escapeHtml(b.owner)}/${escapeHtml(b.repo)}</code> branch <code>${escapeHtml(b.branch)}</code> fork=${escapeHtml(b.fork)} → ${escapeHtml(b.count)}</li>`)
    .join("");
}

export function renderHome(stats) {
  const views = Number(stats.views) || 0;
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const gh = stats.github || {};
  const ld = JSON.stringify(jsonLd());
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${TITLE}</title>
<meta name="description" content="${escapeHtml(DESCRIPTION)}">
<meta name="author" content="${AUTHOR}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="${HOST}/">
<link rel="sitemap" type="application/xml" href="${HOST}/sitemap.xml">
<link rel="icon" type="image/png" href="/sigil.png">
<meta property="og:type" content="website">
<meta property="og:title" content="${TITLE}">
<meta property="og:description" content="${escapeHtml(DESCRIPTION)}">
<meta property="og:url" content="${HOST}/">
<meta property="og:site_name" content="Aziel Eliab">
<meta property="og:image" content="${HOST}/sigil.png">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="${TITLE}">
<meta name="twitter:description" content="${escapeHtml(DESCRIPTION)}">
<meta name="twitter:image" content="${HOST}/sigil.png">
<script type="application/ld+json">${ld}</script>
<style>
  :root {
    color-scheme: dark;
    --bg: #000000; --panel: #0d0d0d; --ink: #ffffff; --muted: #c4c4c4;
    --line: #3a2f12; --gold: #c9a227; --gold-dim: #c9a227; --pass: #3dba7a; --bad: #d4534b; --focus: #e6d19a;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink); }
  body { font: 16px/1.5 system-ui, "Segoe UI", sans-serif; }
  a { color: #e6d19a; }
  code, pre, .mono { font-family: ui-monospace, Menlo, Consolas, monospace; }
  .wrap { max-width: 60rem; margin: 0 auto; padding: 1.4rem 1.2rem 4.5rem; }
  .brandrow { display: flex; align-items: center; gap: 12px; margin: 0 0 12px; }
  .brandmark { width: 40px; height: 40px; border-radius: 10px; object-fit: cover; flex: 0 0 auto; box-shadow: 0 0 0 1px #d4af3733; }
  .stamp { margin: 0; color: var(--gold); font-size: .88rem; letter-spacing: .02em; }
  h1 { font-size: 2rem; letter-spacing: .02em; margin: 0 0 .2rem; color: #fff; }
  .motto { color: var(--gold); font-style: italic; margin: 0 0 .4rem; }
  .marker { color: var(--gold); letter-spacing: .04em; margin: 0 0 .7rem; }
  .lede { color: var(--muted); margin: 0 0 1rem; max-width: 48rem; }
  .pill { font: 650 .78rem/1 ui-monospace, Menlo, Consolas, monospace; letter-spacing: .06em; text-transform: uppercase; border: 1px solid var(--gold); border-radius: 999px; padding: .4rem .7rem; color: var(--gold); background: #000; }
  .pill.ok { color: var(--pass); border-color: #2f6b48; }
  .pill.bad { color: var(--bad); border-color: #7a2f2c; }
  nav.toc { display: flex; flex-wrap: wrap; gap: .55rem; margin: 0 0 1.1rem; }
  nav.toc a { text-decoration: none; color: #fff; border: 1px solid var(--gold); background: var(--panel); border-radius: 999px; padding: .35rem .75rem; font-size: .88rem; }
  .banner { border: 1px solid var(--gold); background: #14100a; color: #f0d78c; padding: .9rem 1rem; border-radius: 10px; margin: 0 0 1.15rem; font-size: .94rem; }
  .card, .workspace, .cite { border: 1px solid var(--gold); border-radius: 14px; padding: 1.15rem 1.2rem 1.25rem; background: var(--panel); margin: 0 0 1.1rem; }
  h2 { font-size: 1.12rem; margin: 0 0 .45rem; letter-spacing: .04em; color: #fff; }
  .kicker { display: block; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: var(--gold); margin-bottom: .15rem; font-family: ui-monospace, Menlo, Consolas, monospace; }
  .actions { display: flex; flex-wrap: wrap; gap: .5rem; margin: .95rem 0 .2rem; }
  button, a.btn { font: 700 .88rem/1.1 ui-monospace, Menlo, Consolas, monospace; letter-spacing: .03em; padding: .72rem .9rem; border-radius: 9px; border: 1px solid transparent; cursor: pointer; text-decoration: none; display: inline-block; }
  button.gold, a.btn.gold { background: var(--gold); color: #000; }
  button.ghost, a.btn.ghost { background: transparent; color: #fff; border-color: var(--gold); }
  button.copied { background: var(--pass); color: #000; }
  .status { margin: 0 0 .8rem; padding: .75rem .85rem; border-radius: 10px; border: 1px solid var(--line); background: #000; color: var(--muted); }
  .status.ok { color: var(--pass); border-color: #2f6b48; }
  .status.bad { color: var(--bad); border-color: #7a2f2c; }
  .metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .55rem; margin: 0 0 .85rem; }
  @media (max-width: 720px) { .metrics { grid-template-columns: 1fr 1fr; } }
  .metric { border: 1px solid var(--gold); border-radius: 10px; padding: .55rem .65rem; background: #000; }
  .metric b { display: block; font-size: .72rem; color: var(--gold); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
  .metric span { display: block; font-size: .78rem; word-break: break-all; color: #fff; }
  .rolodex { display: grid; grid-template-columns: repeat(auto-fill, minmax(9.5rem, 1fr)); gap: .65rem; }
  .goldcard { border: 1px solid var(--gold); min-height: 7rem; padding: .75rem; border-radius: 10px; background: #000; color: #fff; cursor: pointer; }
  .goldcard .full { display: none; font: 11px/1.3 ui-monospace, Menlo, Consolas, monospace; word-break: break-all; color: var(--gold); }
  .goldcard:hover .full { display: block; }
  .goldcard:hover .hint { display: none; }
  input, select { width: 100%; padding: .58rem .7rem; border: 1px solid var(--gold); border-radius: 8px; background: #000; color: #fff; font: inherit; }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 1rem; }
  .count { font-size: 2.1rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; color: #fff; }
  .count span { display: block; font-size: .92rem; font-weight: 500; color: var(--muted); }
  .btns { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin: 0 0 .85rem; }
  @media (max-width: 520px) { .btns { grid-template-columns: 1fr; } }
  a.btn.block, button.btn.block { display: block; width: 100%; text-align: center; font-size: 1.15rem; padding: 1rem 1.1rem; }
  a.btn.primary { background: #fff; color: #000; }
  button.btn.install { background: var(--gold); color: #000; }
  pre { background: #000; padding: .75rem .9rem; overflow: auto; border-radius: 8px; font-size: .82rem; border: 1px solid var(--line); color: #fff; }
  .meta { margin-top: 1rem; color: var(--muted); font-size: .92rem; }
  footer { color: var(--muted); font-size: .9rem; }
  #meshStrip { border: 1px solid var(--gold); border-radius: 14px; padding: .85rem 1rem; background: var(--panel); margin: 0 0 1.1rem; display: flex; flex-wrap: wrap; align-items: center; gap: .7rem 1rem; font-size: .88rem; color: var(--muted); }
  #meshStrip .live { color: #fff; }
  #meshStrip .live b { color: var(--gold); font-size: 1.35rem; margin-right: .35rem; }
  #meshStrip .rollup b { color: var(--gold); }
  #meshStrip button { font: 700 .78rem/1 ui-monospace, Menlo, Consolas, monospace; height: 2rem; padding: 0 .75rem; border-radius: 8px; background: #000; color: #fff; border: 1px solid var(--gold); cursor: pointer; }
  #meshStrip button:hover { background: #241c0d; color: var(--gold); }
  #meshStrip input { width: 10rem; padding: .4rem .55rem; border: 1px solid var(--gold); border-radius: 8px; background: #000; color: #fff; font: inherit; }
  #meshProducts { flex-basis: 100%; margin: 0; }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brandrow">
        <img class="brandmark" src="/sigil.png" width="40" height="40" alt="Everblooming sigil — Aziel Eliab" decoding="async">
        <p class="stamp">Everblooming sigil · Aziel Eliab</p>
      </div>
      <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap">
        <div>
          <h1>AZNet</h1>
          <p class="motto">Verification without hosting. Presence without authority.</p>
          <p class="marker">${escapeHtml(MARKER)}</p>
        </div>
        <p class="pill" id="api-pill">API · checking</p>
      </div>
      <p class="lede">v${VERSION} software by <strong>${AUTHOR}</strong> only. Silent verification SIDE-NET. Hashes only. AZNet + <a href="${AZBROWSER}">AZBrowser</a> are both required. FragGate unlocks access. StaticClock stamps time. Forks are welcome and always allowed.</p>
      <nav class="toc" aria-label="Product sections">
        <a href="#garden">Garden</a>
        <a href="#memorial">Memorial</a>
        <a href="#stamps">Stamps</a>
        <a href="#receipts">Receipts</a>
        <a href="#pair">Pair</a>
        <a href="#meshStrip">Live Nodes</a>
        <a href="#install">Download / install</a>
        <a href="/v1/skill">Skill</a>
        <a href="/openapi.json">OpenAPI</a>
        <a href="/mcp">/mcp pointer</a>
        <a href="${GITHUB_REPO}">GitHub</a>
      </nav>
      <p class="banner">${escapeHtml(HONEST)}</p>
    </header>

    <div id="meshStrip" aria-label="Suite Live Nodes">
      <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
      <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.</div>
      <div class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
      <div>No Node Gate · No auto-heal · Aziel Eliab only</div>
      <div>
        <input id="meshBearer" type="text" maxlength="80" placeholder="bearer (required to enable)" aria-label="mesh bearer">
        <button id="meshEnable" type="button" title="Enable suite mesh. Declared bearer required. Default off.">Enable</button>
        <button id="meshDisable" type="button" title="Disable suite mesh (always allowed)">Disable</button>
        <button id="meshJoin" type="button" title="Join as aznet. Refused while mesh is OFF. No auto-join. AZBrowser stays separate software.">Join</button>
        <button id="meshLeave" type="button" title="Leave this node. No auto-heal.">Leave</button>
      </div>
      <div id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cite only · not AnonBroadcast · not AZMail ring · AZBrowser is sibling pair only · no public qnsd proxy</div>
    </div>

    <section class="card" id="pair">
      <h2><span class="kicker">pair</span>Pair status</h2>
      <p>Separate software. Functional pair only: <code>pair_token</code>, then FragGate <code>pair_flag</code>. No AZBrowser chrome is embedded here. Catalog op: <code>pair_status</code>.</p>
      <p id="pair-status">UNPAIRED · LOCKED</p>
      <div class="actions">
        <button type="button" class="gold" id="btn-pair">Pair AZBrowser</button>
        <button type="button" class="ghost" id="btn-unlock">FragGate unlock</button>
      </div>
    </section>

    <section class="card" id="unlock">
      <h2><span class="kicker">unlock</span>FragGate</h2>
      <p>ONE FragGate door. Agent path is FragGate only: <code>POST /v1/fraggate/call</code> slug=<b>aznet</b>. This Worker <code>/v1/fraggate/*</code> and <code>/v1/mesh/*</code> proxy to aziel-runtime. Catalog MCP: <code>POST https://aziel-runtime.vibelock.workers.dev/mcp</code> (<code>mesh_*</code> + slug=<b>mesh</b>). This host <a href="/mcp">/mcp</a> is a pointer, not a second MCP. AZBrowser is sibling software (functional pair only). Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 cite only (not a Softwares-tab product; no public qnsd proxy). No Node Gate. No auto-heal. Not anonymity.</p>
    </section>

    <section class="card" id="staticclock">
      <h2><span class="kicker">staticclock</span>StaticClock</h2>
      <p>Advisory time. Not a scheduler. <a href="${STATICCLOCK_HOST}/">staticclock-download-tracker</a></p>
      <pre id="clock">loading…</pre>
    </section>

    <section class="workspace" id="garden">
      <h2><span class="kicker">garden</span>Custodian Garden / Gold Pages</h2>
      <p class="lede">Shifting, non-ranked hash directory. Hover to reveal. Click is manual intent. No favorites, analytics, or personalization. Demo garden on this Worker — device-local silent node is the real posture.</p>
      <div class="rolodex" id="rolodex"></div>
    </section>

    <section class="card" id="stamps">
      <h2><span class="kicker">stamps</span>Stamping ledger</h2>
      <p>TemporalLock-style stamp of a hash. Never a payload.</p>
      <label for="hash-hex"><span class="kicker">hash_hex</span></label>
      <input id="hash-hex" maxlength="64" placeholder="64-char sha256 hex">
      <div class="actions">
        <button type="button" class="gold" id="btn-stamp">Stamp</button>
        <button type="button" class="ghost" id="btn-verify">Verify hash</button>
        <button type="button" class="ghost" id="btn-lattice">Lattice</button>
        <button type="button" class="ghost" id="btn-receipt">Receipt verify</button>
      </div>
    </section>

    <section class="card" id="memorial">
      <h2><span class="kicker">memorial</span>Memorial ledger</h2>
      <p>Terminal compromise: genesis / final hash, timestamps, non-actionable summary. No exploit details.</p>
      <select id="reason">
        <option>isolation</option>
        <option>ui_altered</option>
        <option>integrity_refuse</option>
        <option>node_withdraw</option>
        <option>pair_broken</option>
        <option>witness_fail</option>
      </select>
      <div class="actions">
        <button type="button" class="ghost" id="btn-memorial">Memorial append</button>
        <button type="button" class="ghost" id="btn-memorial-list">Memorial list</button>
        <button type="button" class="ghost" id="btn-withdraw">Withdraw</button>
        <button type="button" class="ghost" id="btn-witness">Witness</button>
      </div>
    </section>

    <section class="card" id="receipts">
      <h2><span class="kicker">receipts</span>Hash-chained lattice</h2>
      <div class="status" id="ws-status">Pair AZBrowser, then FragGate unlock. Garden stays hash-only.</div>
      <div class="metrics">
        <div class="metric"><b>Length</b><span id="chain-length">0</span></div>
        <div class="metric"><b>Pair</b><span id="last-pair">UNPAIRED</span></div>
        <div class="metric"><b>Last hash</b><span id="last-hash">—</span></div>
        <div class="metric"><b>Date stamp</b><span id="last-date">—</span></div>
      </div>
      <pre id="receipt-list">[]</pre>
    </section>

    <section class="card" id="install">
      <h2><span class="kicker">Counted package</span>Download and one-click install</h2>
      <div class="nums">
        <p class="count">${v}<span>Views</span></p>
        <p class="count">${n}<span>Downloads</span></p>
      </div>
      <p>Download saves the gzip from this Worker (HTTP 200, counted). After install, run <code>aznet ui</code> and open http://127.0.0.1:8771 on this computer only.</p>
      <div class="btns">
        <a class="btn block primary" href="/download?asset=${DEFAULT_ASSET}">Download</a>
        <button type="button" class="btn block install" id="install-btn">One-click install</button>
      </div>
      <pre id="install-cmd">${INSTALL_LINE}</pre>
      <p class="meta">The download count ticks on the Download click. No 302 to GitHub. ${DEFAULT_ASSET} — ${n} counted.</p>
      <p class="iso">Isolated counter: Worker <code>aznet-download-tracker</code>, project <code>aznet</code>, KV <code>AZNET_DOWNLOADS</code>. /v1 and /mcp do not increment downloads.</p>
      <p class="meta">GitHub: stars ${gh.stars || 0} · forks ${gh.forks || 0} · watchers ${gh.watchers || 0} · release assets ${gh.release_download_count || 0}</p>
      <p class="meta">Pair / time: <a href="${AZBROWSER}">AZBrowser</a> · <a href="${STATICCLOCK_HOST}/">StaticClock</a> · <a href="${TEMPORALLOCK_HOST}/">TemporalLock</a> · <a href="${FRAGGATE}">FragGate</a> · <a href="${CATALOG}">aziel-runtime</a> · <a href="https://www.azielcorpuslibrary.net/">library</a> · <a href="https://godlock.uk/">godlock.uk</a> · <a href="https://www.azieleliab.com/">www.azieleliab.com</a></p>
      <p class="meta"><a href="/stats">JSON stats</a> · <a href="/count">/count</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/mcp">/mcp pointer</a> · <a href="/v1/fraggate/list">FragGate list</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/v1/skill">Skill</a> · <a href="/v1/example">Example</a> · <a href="/ai">AI runtime</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${GITHUB_LATEST}">releases</a></p>
      <h3>Per repo / branch / fork</h3>
      <ul>${breakdownList(stats)}</ul>
    </section>

    <section class="cite" id="cite">
      <h2>How to cite</h2>
      <p>${escapeHtml(HOW_TO_CITE)}</p>
      <p>Author: <strong>${AUTHOR}</strong> only · License: Apache-2.0 · Forks welcome and always allowed · Machine-readable: <a href="/cite.json">/cite.json</a></p>
      <p class="meta">No DOI is invented here. Software deposit still needed. Cite GitHub and this Worker.</p>
      <p><a href="${CATALOG}">Catalog</a> · <a href="${CATALOG_PRODUCT}">Catalog product</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${HOST}/download">Download</a> · <a href="/llms.txt">llms.txt</a></p>
    </section>

    <footer>
      <p>Apache-2.0 · ${AUTHOR} · AZNet v${VERSION}</p>
      <p>${escapeHtml(MARKER)}</p>
      <p>Hashes only. UI is a mandatory witness. The sequence cannot be altered without detection.</p>
    </footer>
  </div>
  <script>
    (function () {
      var SECTIONS = ["garden", "memorial", "stamps", "receipts", "pair", "unlock", "staticclock"];
      var missing = SECTIONS.filter(function (id) { return !document.getElementById(id); });
      if (missing.length) {
        document.body.innerHTML = "<p style='background:#000;color:#c9a227;padding:2rem'>UI witness failed. Terminated. Memorial required. Truth Is No Defense — .AZNet — AZ.</p>";
        throw new Error("ui_altered");
      }
      var STORAGE = "aznet-workspace-ledger-v1";
      var ledger = [];
      var lastResult = null;
      var witnessHash = "";
      function $(id) { return document.getElementById(id); }
      function loadLedger() {
        try {
          var raw = localStorage.getItem(STORAGE);
          if (!raw) return;
          var parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) ledger = parsed;
        } catch (e) { /* local only */ }
      }
      function saveLedger() {
        try { localStorage.setItem(STORAGE, JSON.stringify(ledger)); } catch (e) { /* ignore quota */ }
      }
      function setStatus(kind, text) {
        var el = $("ws-status");
        el.className = "status" + (kind ? " " + kind : "");
        el.textContent = text;
      }
      function render() {
        $("chain-length").textContent = String(ledger.length);
        var last = ledger.length ? ledger[ledger.length - 1] : null;
        $("last-hash").textContent = last && last.receipt_hash ? last.receipt_hash : "—";
        $("last-date").textContent = last && last.date_stamp ? last.date_stamp : "—";
        var pair = "UNPAIRED";
        var unlock = "LOCKED";
        ledger.forEach(function (r) {
          if (r.event_kind === "PAIR" && r.pair_status) pair = r.pair_status;
          if (r.event_kind === "UNLOCK" && r.unlock_status) unlock = r.unlock_status;
        });
        if (pair !== "PAIRED") unlock = "LOCKED";
        $("last-pair").textContent = pair;
        $("pair-status").textContent = pair + " · " + unlock;
        $("receipt-list").textContent = JSON.stringify(lastResult || ledger, null, 2);
      }
      async function api(path, body, method) {
        var res = await fetch(path, {
          method: method || "POST",
          headers: { "Content-Type": "application/json" },
          body: (method || "POST") === "GET" ? undefined : JSON.stringify(Object.assign({ ledger: ledger }, body || {}))
        });
        var data = await res.json();
        if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
        return data;
      }
      function applyResult(data, fallbackMsg) {
        lastResult = data;
        if (Array.isArray(data.ledger)) ledger = data.ledger;
        saveLedger();
        setStatus(data.ok === false || data.error ? "bad" : "ok", data.message || data.action || fallbackMsg);
        render();
      }
      async function run(fn, label) {
        try { applyResult(await fn(), label); }
        catch (err) { setStatus("bad", String(err.message || err)); }
      }
      $("btn-pair").onclick = function () { run(function () { return api("/v1/pair_status", { azbrowser: "${AZBROWSER}" }); }, "Paired. FragGate still required."); };
      $("btn-unlock").onclick = function () { run(function () { return api("/v1/unlock", {}); }, "FragGate unlocked."); };
      $("btn-stamp").onclick = function () { run(function () { return api("/v1/stamp", { hash_hex: $("hash-hex").value }); }, "Stamped. Hash only."); };
      $("btn-verify").onclick = function () { run(function () { return api("/v1/verify_hash", {}); }, "Verify walked hashes and prev links."); };
      $("btn-lattice").onclick = function () { run(function () { return api("/v1/lattice", {}); }, "Lattice walk."); };
      $("btn-receipt").onclick = function () { run(function () { return api("/v1/receipt_verify", {}); }, "Receipt verify."); };
      $("btn-memorial").onclick = function () { run(function () { return api("/v1/memorial_append", { reason: $("reason").value }); }, "Memorial written. Non-actionable."); };
      $("btn-memorial-list").onclick = function () { run(function () { return api("/v1/memorial_list", {}); }, "Memorial list."); };
      $("btn-withdraw").onclick = function () { run(function () { return api("/v1/withdraw", {}); }, "Withdrawn. Silence as security."); };
      $("btn-witness").onclick = function () { run(function () { return api("/v1/witness", { witness_hash: witnessHash }); }, "UI witness intact."); };
      fetch("/v1/garden_list").then(function (r) { return r.json(); }).then(function (g) {
        var box = $("rolodex");
        box.textContent = "";
        (g.cards || []).forEach(function (c) {
          var el = document.createElement("div");
          el.className = "goldcard";
          el.innerHTML = "<div class='kicker'>" + c.label + "</div><div class='hint'>hover reveal</div><div class='full'>" + c.hash_hex + "</div>";
          el.onclick = function () { $("hash-hex").value = c.hash_hex; };
          box.appendChild(el);
        });
      }).catch(function () {});
      fetch("/v1/time").then(function (r) { return r.json(); }).then(function (t) {
        $("clock").textContent = JSON.stringify(t, null, 2);
      }).catch(function () { $("clock").textContent = "StaticClock unavailable"; });
      fetch("/v1/witness").then(function (r) { return r.json(); }).then(function (w) {
        witnessHash = w.witness_hash || "";
      }).catch(function () {});
      fetch("/v1/health").then(function (res) { return res.json(); }).then(function (data) {
        var pill = $("api-pill");
        if (!pill) return;
        if (data && data.ok) {
          pill.textContent = "API live · v" + (data.version || "${VERSION}");
          pill.className = "pill ok";
        } else {
          pill.textContent = "API down";
          pill.className = "pill bad";
        }
      }).catch(function () {
        var pill = $("api-pill");
        if (pill) { pill.textContent = "API down"; pill.className = "pill bad"; }
      });
      var installBtn = $("install-btn");
      var installPre = $("install-cmd");
      var installCmd = ${JSON.stringify(INSTALL_LINE)};
      if (installBtn) {
        installBtn.addEventListener("click", function () {
          function done(ok) {
            installBtn.textContent = ok ? "Copied! Paste in Terminal, then run aznet ui" : "Select the command, copy it, then run aznet ui";
            installBtn.classList.add("copied");
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(installCmd).then(function () { done(true); }).catch(function () { done(false); });
          } else {
            done(false);
            if (installPre && window.getSelection) {
              var r = document.createRange();
              r.selectNodeContents(installPre);
              var sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(r);
            }
          }
        });
      }
      function meshNum() {
        for (var i = 0; i < arguments.length; i++) {
          var raw = arguments[i];
          if (raw == null || raw === "") continue;
          var n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
          if (Number.isFinite(n) && n >= 0) return Math.floor(n);
        }
        return 0;
      }
      function unwrapMesh(j) {
        if (!j || typeof j !== "object") return {};
        if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
        if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
        return j;
      }
      function paintMesh(raw) {
        var j = unwrapMesh(raw);
        var on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
        var r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
        var live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
        var locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
        var isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
        $("meshLiveCount").textContent = String(live);
        $("qnmLive").textContent = String(live);
        $("qnmLocked").textContent = String(locked);
        $("qnmIsolated").textContent = String(isolated);
        var line = $("meshLine");
        if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". QNS-CD-1.0 cite only. Not an anonymity network.";
        else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
        else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. QNS-CD-1.0. Not an anonymity network.";
        var products = j.products_present || j.products || [];
        var names = Array.isArray(products) ? products.map(function (p) { return typeof p === "string" ? p : (p && (p.product || p.slug)) || ""; }).filter(Boolean) : [];
        var nodes = Array.isArray(j.nodes) ? j.nodes : [];
        var extra = names.length ? " · products " + names.join(", ") : (nodes.length ? " · " + nodes.length + " node labels" : "");
        $("meshProducts").textContent = "Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 cite only · not AnonBroadcast · not AZMail ring · AZBrowser is sibling pair only · no public qnsd proxy" + extra;
      }
      async function meshGet(path) {
        var r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
        return r.json();
      }
      async function meshPost(path, payload) {
        var r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
        return r.json();
      }
      async function refreshMesh() {
        try {
          var status = await meshGet("/v1/mesh");
          var merged = status;
          var inner = unwrapMesh(status);
          var on = inner.enabled === true;
          if (on) {
            try {
              var nodes = await meshGet("/v1/mesh/nodes");
              merged = Object.assign({}, inner, unwrapMesh(nodes));
            } catch (e) { /* status is enough */ }
          }
          paintMesh(merged);
          var nodeId = sessionStorage.getItem("aznet_mesh_node");
          if (on && nodeId) {
            try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) { /* no auto-heal */ }
          }
        } catch (e) {
          paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
        }
      }
      $("meshEnable").onclick = async function () {
        var bearer = ($("meshBearer").value || "").trim();
        paintMesh(await meshPost("/v1/mesh/enable", bearer ? { bearer: bearer } : {}));
        refreshMesh();
      };
      $("meshDisable").onclick = async function () {
        sessionStorage.removeItem("aznet_mesh_node");
        paintMesh(await meshPost("/v1/mesh/disable", {}));
        refreshMesh();
      };
      $("meshJoin").onclick = async function () {
        var j = await meshPost("/v1/mesh/join", { product: "aznet", label: "AZNet Worker" });
        var inner = unwrapMesh(j);
        var id = inner.node_id || inner.id || (inner.session && inner.session.node_id);
        if (id) sessionStorage.setItem("aznet_mesh_node", String(id));
        paintMesh(j);
        refreshMesh();
      };
      $("meshLeave").onclick = async function () {
        var id = sessionStorage.getItem("aznet_mesh_node");
        if (id) await meshPost("/v1/mesh/leave", { node_id: id });
        sessionStorage.removeItem("aznet_mesh_node");
        refreshMesh();
      };
      window.addEventListener("pagehide", function () {
        var id = sessionStorage.getItem("aznet_mesh_node");
        if (!id || typeof navigator.sendBeacon !== "function") return;
        try { navigator.sendBeacon("/v1/mesh/leave", new Blob([JSON.stringify({ node_id: id })], { type: "application/json" })); } catch (e) { /* leave expires in 5 minutes */ }
      });
      refreshMesh();
      setInterval(refreshMesh, 30000);
      document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshMesh(); });
      loadLedger();
      render();
    })();
  </script>
</body>
</html>`;
}
