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
const STATICCLOCK_HOST = "https://staticclock-download-tracker.vibelock.workers.dev";
const TEMPORALLOCK_HOST = "https://temporallock-download-tracker.vibelock.workers.dev";
const FRAGGATE = "https://github.com/AzielEliab/fraggate";
const LICENSE = "https://www.apache.org/licenses/LICENSE-2.0";
const VERSION = "0.1.0";
const AUTHOR = "Aziel Eliab";
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
    author: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
    creator: { "@type": "Person", name: AUTHOR, url: "https://github.com/AzielEliab" },
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

function sitemapXml() {
  const paths = ["/", "/download", "/count", "/stats", "/install.sh", "/v1/skill", "/v1/example", "/v1/health", "/v1/garden", "/openapi.json", "/cite.json", "/llms.txt", "/ai"];
  const urls = paths.map((p) => `  <url><loc>${HOST}${p === "/" ? "/" : p}</loc></url>`).join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
  <url><loc>${GITHUB_REPO}</loc></url>
</urlset>
`;
}

function robotsTxt() {
  return `User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: meta-externalagent
Allow: /

User-agent: FacebookBot
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: Diffbot
Allow: /

User-agent: Omgilibot
Allow: /

User-agent: Amazonbot
Allow: /

Sitemap: ${HOST}/sitemap.xml
`;
}

function llmsTxt() {
  return `# AZNet

Author: Aziel Eliab
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
Ops: POST /v1/pair, POST /v1/unlock, POST /v1/stamp, POST /v1/verify, POST /v1/memorial
Pair: AZNet + AZBrowser both required
Marker: ${MARKER}
Identity: Aziel Eliab only
License: Apache-2.0
Forks: welcome and always allowed
DOI: none invented; software deposit still needed.

Indexing, metadata scrape, and AI grounding of public pages are allowed.
`;
}

export function handleSeoRoutes(request, url) {
  if (request.method !== "GET" && request.method !== "HEAD") return null;
  const headers = { ...corsHeaders(), "Cache-Control": "private, no-store" };
  if (url.pathname === "/cite.json") {
    return new Response(JSON.stringify(citePayload(), null, 2), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8", ...headers },
    });
  }
  if (url.pathname === "/sitemap.xml") {
    return new Response(sitemapXml(), { status: 200, headers: { "Content-Type": "application/xml; charset=utf-8", ...headers } });
  }
  if (url.pathname === "/robots.txt") {
    return new Response(robotsTxt(), { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8", ...headers } });
  }
  if (url.pathname === "/llms.txt" || url.pathname === "/ai.txt") {
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
        <a href="#install">Download / install</a>
        <a href="/v1/skill">Skill</a>
        <a href="/openapi.json">OpenAPI</a>
        <a href="${GITHUB_REPO}">GitHub</a>
      </nav>
      <p class="banner">${escapeHtml(HONEST)}</p>
    </header>

    <section class="card" id="pair">
      <h2><span class="kicker">pair</span>Pair status</h2>
      <p>Separate apps. Functional pair only: <code>pair_token</code>, then FragGate <code>pair_flag</code>. No AZBrowser chrome is embedded here.</p>
      <p id="pair-status">UNPAIRED · LOCKED</p>
      <div class="actions">
        <button type="button" class="gold" id="btn-pair">Pair AZBrowser</button>
        <button type="button" class="ghost" id="btn-unlock">FragGate unlock</button>
      </div>
    </section>

    <section class="card" id="unlock">
      <h2><span class="kicker">unlock</span>FragGate</h2>
      <p>Kernel: <a href="${FRAGGATE}">fraggate</a>. Catalog MCP: <code>POST https://aziel-runtime.vibelock.workers.dev/mcp</code>. Slug <code>aznet</code>.</p>
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
        <button type="button" class="ghost" id="btn-verify">Verify</button>
        <button type="button" class="ghost" id="btn-lattice">Lattice</button>
        <button type="button" class="ghost" id="btn-doctor">Doctor</button>
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
        <button type="button" class="ghost" id="btn-memorial">Memorial</button>
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
      <p class="iso">Isolated counter: Worker <code>aznet-download-tracker</code>, project <code>aznet</code>, KV <code>AZNET_DOWNLOADS</code>. /v1 does not increment downloads.</p>
      <p class="meta">GitHub: stars ${gh.stars || 0} · forks ${gh.forks || 0} · watchers ${gh.watchers || 0} · release assets ${gh.release_download_count || 0}</p>
      <p class="meta">Pair / time: <a href="${AZBROWSER}">AZBrowser</a> · <a href="${STATICCLOCK_HOST}/">StaticClock</a> · <a href="${TEMPORALLOCK_HOST}/">TemporalLock</a> · <a href="${FRAGGATE}">FragGate</a> · <a href="${CATALOG}">aziel-runtime</a> · <a href="https://www.azielcorpuslibrary.net/">library</a> · <a href="https://godlock.uk/">godlock.uk</a> · <a href="https://www.azieleliab.com/">www.azieleliab.com</a></p>
      <p class="meta"><a href="/stats">JSON stats</a> · <a href="/count">/count</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/v1/skill">Skill</a> · <a href="/v1/example">Example</a> · <a href="/ai">AI runtime</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${GITHUB_LATEST}">releases</a></p>
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
      $("btn-pair").onclick = function () { run(function () { return api("/v1/pair", { azbrowser: "${AZBROWSER}" }); }, "Paired. FragGate still required."); };
      $("btn-unlock").onclick = function () { run(function () { return api("/v1/unlock", {}); }, "FragGate unlocked."); };
      $("btn-stamp").onclick = function () { run(function () { return api("/v1/stamp", { hash_hex: $("hash-hex").value }); }, "Stamped. Hash only."); };
      $("btn-verify").onclick = function () { run(function () { return api("/v1/verify", {}); }, "Verify walked hashes and prev links."); };
      $("btn-lattice").onclick = function () { run(function () { return api("/v1/lattice", {}); }, "Lattice walk."); };
      $("btn-doctor").onclick = function () { run(function () { return api("/v1/doctor", {}, "GET"); }, "Doctor. No writes."); };
      $("btn-memorial").onclick = function () { run(function () { return api("/v1/memorial", { reason: $("reason").value }); }, "Memorial written. Non-actionable."); };
      $("btn-withdraw").onclick = function () { run(function () { return api("/v1/withdraw", {}); }, "Withdrawn. Silence as security."); };
      $("btn-witness").onclick = function () { run(function () { return api("/v1/witness", { witness_hash: witnessHash }); }, "UI witness intact."); };
      fetch("/v1/garden").then(function (r) { return r.json(); }).then(function (g) {
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
      loadLedger();
      render();
    })();
  </script>
</body>
</html>`;
}
