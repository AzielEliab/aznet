"""Loopback UI for AZNet. 127.0.0.1 only. Author: Aziel Eliab only."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from aznet.canon import HONEST, MARKER, VERSION, WITNESS_SECTIONS, witness_digest
from aznet.chain import Ledger, default_ledger_path
from aznet.clock import advise
from aznet.garden import garden_view
from aznet.witness import expected_witness

AUTHOR = "Aziel Eliab"
PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZNet — Aziel Eliab</title>
<style>
  :root { color-scheme: dark; --bg:#000; --ink:#fff; --gold:#c9a227; --muted:#b8b8b8; --panel:#0d0d0d; --line:#3a2f12; }
  html, body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.5 system-ui,sans-serif; }
  a { color:var(--gold); }
  .wrap { max-width:58rem; margin:0 auto; padding:1.4rem 1.2rem 4rem; }
  h1 { margin:0 0 .2rem; }
  .motto { color:var(--gold); font-style:italic; }
  .marker { color:var(--gold); letter-spacing:.04em; }
  .card { border:1px solid var(--gold); background:var(--panel); border-radius:12px; padding:1rem 1.1rem; margin:0 0 1rem; }
  .kicker { display:block; color:var(--gold); font:650 .68rem/1 ui-monospace,monospace; letter-spacing:.12em; text-transform:uppercase; }
  button { background:var(--gold); color:#000; border:0; padding:.7rem .9rem; border-radius:8px; font:700 .88rem/1 ui-monospace,monospace; cursor:pointer; }
  button.ghost { background:transparent; color:var(--ink); border:1px solid var(--line); }
  .actions { display:flex; flex-wrap:wrap; gap:.5rem; margin:.8rem 0; }
  .status { border:1px solid var(--line); padding:.7rem; border-radius:8px; color:var(--muted); }
  .hash { font:12px/1.4 ui-monospace,monospace; word-break:break-all; color:var(--muted); }
  .rolodex { display:grid; grid-template-columns:repeat(auto-fill,minmax(9rem,1fr)); gap:.6rem; }
  .goldcard { border:1px solid var(--gold); min-height:6.5rem; padding:.7rem; border-radius:10px; background:#111; }
  .goldcard .full { display:none; font:11px/1.3 ui-monospace,monospace; word-break:break-all; }
  .goldcard:hover .full { display:block; }
  .goldcard:hover .hint { display:none; }
  input, select { width:100%; background:#000; color:#fff; border:1px solid var(--line); padding:.5rem; border-radius:8px; }
  label { display:block; margin:.6rem 0 .25rem; }
</style>
</head>
<body>
  <div class="wrap">
    <p class="kicker">Device-local silent node</p>
    <h1>AZNet</h1>
    <p class="motto">Verification without hosting. Presence without authority.</p>
    <p class="marker" id="marker">__MARKER__</p>
    <p>Author: Aziel Eliab only. AZNet + AZBrowser both required. FragGate unlocks access. StaticClock stamps time.</p>
    <p>__HONEST__</p>

    <section class="card" id="pair">
      <h2><span class="kicker">pair</span>Pair status</h2>
      <p id="pair-status">UNPAIRED · LOCKED</p>
      <div class="actions">
        <button type="button" id="btn-pair">Pair AZBrowser</button>
        <button type="button" class="ghost" id="btn-unlock">FragGate unlock</button>
      </div>
    </section>

    <section class="card" id="unlock">
      <h2><span class="kicker">unlock</span>FragGate</h2>
      <p>Kernel: <a href="https://github.com/AzielEliab/fraggate">fraggate</a>. Catalog: aziel-runtime slug <code>aznet</code>.</p>
    </section>

    <section class="card" id="staticclock">
      <h2><span class="kicker">staticclock</span>Time</h2>
      <pre id="clock" class="hash"></pre>
    </section>

    <section class="card" id="garden">
      <h2><span class="kicker">garden</span>Custodian Garden / Gold Pages</h2>
      <p>Shifting, non-ranked. Hover to reveal. Manual intent only. No favorites.</p>
      <div class="rolodex" id="rolodex"></div>
    </section>

    <section class="card" id="stamps">
      <h2><span class="kicker">stamps</span>Stamping ledger</h2>
      <label for="hash-hex">Hash (64 hex). Never a payload.</label>
      <input id="hash-hex" maxlength="64" placeholder="sha256 hex">
      <div class="actions">
        <button type="button" id="btn-stamp">Stamp</button>
        <button type="button" class="ghost" id="btn-verify">Verify</button>
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
      <h2><span class="kicker">receipts</span>Lattice</h2>
      <div class="status" id="ws-status">Pair AZBrowser, then FragGate unlock. Garden stays hash-only.</div>
      <pre class="hash" id="receipt-list"></pre>
    </section>
  </div>
  <script>
    var WITNESS = "__WITNESS__";
    var SECTIONS = __SECTIONS__;
    function missing() {
      return SECTIONS.filter(function (id) { return !document.getElementById(id); });
    }
    if (missing().length) {
      document.body.innerHTML = "<p>UI witness failed. Terminated. Memorial required.</p>";
      throw new Error("ui_altered");
    }
    async function api(path, body) {
      var res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
      var data = await res.json();
      if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
      return data;
    }
    function show(data) {
      document.getElementById("ws-status").textContent = data.message || data.action || "ok";
      document.getElementById("receipt-list").textContent = JSON.stringify(data.ledger || data, null, 2);
      if (data.pair_status) document.getElementById("pair-status").textContent = data.pair_status + " · " + (data.unlock_status || "");
    }
    async function refresh() {
      var g = await fetch("/local/garden").then(function (r) { return r.json(); });
      var box = document.getElementById("rolodex");
      box.textContent = "";
      (g.cards || []).forEach(function (c) {
        var el = document.createElement("div");
        el.className = "goldcard";
        el.innerHTML = "<div class='kicker'>" + c.label + "</div><div class='hint'>hover reveal</div><div class='full'>" + c.hash_hex + "</div>";
        el.onclick = function () { document.getElementById("hash-hex").value = c.hash_hex; };
        box.appendChild(el);
      });
      var t = await fetch("/local/time").then(function (r) { return r.json(); });
      document.getElementById("clock").textContent = JSON.stringify(t, null, 2);
    }
    document.getElementById("btn-pair").onclick = function () { api("/local/pair", {}).then(show).catch(function (e) { document.getElementById("ws-status").textContent = String(e.message || e); }); };
    document.getElementById("btn-unlock").onclick = function () { api("/local/unlock", {}).then(show).catch(function (e) { document.getElementById("ws-status").textContent = String(e.message || e); }); };
    document.getElementById("btn-stamp").onclick = function () { api("/local/stamp", { hash_hex: document.getElementById("hash-hex").value }).then(show).catch(function (e) { document.getElementById("ws-status").textContent = String(e.message || e); }); };
    document.getElementById("btn-verify").onclick = function () { api("/local/verify", {}).then(show).catch(function (e) { document.getElementById("ws-status").textContent = String(e.message || e); }); };
    document.getElementById("btn-memorial").onclick = function () { api("/local/memorial", { reason: document.getElementById("reason").value }).then(show).catch(function (e) { document.getElementById("ws-status").textContent = String(e.message || e); }); };
    document.getElementById("btn-withdraw").onclick = function () { api("/local/withdraw", {}).then(show).catch(function (e) { document.getElementById("ws-status").textContent = String(e.message || e); }); };
    document.getElementById("btn-witness").onclick = function () { api("/local/witness", { witness_hash: WITNESS }).then(show).catch(function (e) { document.getElementById("ws-status").textContent = String(e.message || e); }); };
    refresh();
  </script>
</body>
</html>
"""


def render_page() -> str:
    return (
        PAGE.replace("__MARKER__", MARKER)
        .replace("__HONEST__", HONEST)
        .replace("__WITNESS__", witness_digest())
        .replace("__SECTIONS__", json.dumps(list(WITNESS_SECTIONS)))
    )


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return

    def _json(self, payload: dict, status: int = 200) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, text: str) -> None:
        raw = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/ui"}:
            self._html(render_page())
            return
        if path == "/local/garden":
            self._json(garden_view())
            return
        if path == "/local/time":
            self._json(advise())
            return
        self._json({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        body: dict = {}
        if length:
            try:
                body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            except Exception:
                body = {}
        ledger = Ledger.load(default_ledger_path())
        path = urlparse(self.path).path
        try:
            if path == "/local/pair":
                rec = ledger.pair()
                self._json({"action": "paired", "receipt": rec.to_dict(), "ledger": ledger.as_rows(), "pair_status": "PAIRED", "unlock_status": "LOCKED"})
                return
            if path == "/local/unlock":
                rec = ledger.unlock()
                self._json({"action": "unlocked", "receipt": rec.to_dict(), "ledger": ledger.as_rows(), "pair_status": "PAIRED", "unlock_status": "UNLOCKED"})
                return
            if path == "/local/stamp":
                rec = ledger.stamp(body.get("hash_hex") or "")
                self._json({"action": "stamped", "receipt": rec.to_dict(), "ledger": ledger.as_rows()})
                return
            if path == "/local/verify":
                result = ledger.verify()
                self._json({"action": "verify", "ok": result.ok, "length": result.length, "errors": result.errors, "ledger": ledger.as_rows()})
                return
            if path == "/local/memorial":
                rec = ledger.memorial(reason=body.get("reason") or "isolation")
                self._json({"action": "memorial", "receipt": rec.to_dict(), "ledger": ledger.as_rows()})
                return
            if path == "/local/withdraw":
                rec = ledger.withdraw()
                self._json({"action": "withdrawn", "receipt": rec.to_dict(), "ledger": ledger.as_rows()})
                return
            if path == "/local/witness":
                rec = ledger.witness(body.get("witness_hash") or expected_witness())
                self._json({"action": "witness", "receipt": rec.to_dict(), "ledger": ledger.as_rows()})
                return
            self._json({"error": "not found"}, 404)
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc), "ok": False}, 400)


def serve(host: str = "127.0.0.1", port: int = 8771) -> None:
    if host not in {"127.0.0.1", "localhost"}:
        host = "127.0.0.1"
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"AZNet UI  http://{host}:{port}  (loopback only)  v{VERSION}  {AUTHOR}")
    print(MARKER)
    httpd.serve_forever()
