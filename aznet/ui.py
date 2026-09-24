"""Loopback UI for AZNet. 127.0.0.1 only. Author: Aziel Eliab only."""

from __future__ import annotations

import html
import json
import sys
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
<script>
try {
  var savedTheme = localStorage.getItem("aznet-theme");
  if (savedTheme === "light" || savedTheme === "dark") document.documentElement.setAttribute("data-theme", savedTheme);
} catch (e) {}
</script>
<style>
  :root {
    color-scheme: light dark;
    --bg: #f7f4ec;
    --ink: #1c1914;
    --muted: #5e584c;
    --gold: #c9a227;
    --gold-ink: #6d5610;
    --panel: #fffdf8;
    --line: #e6dcc4;
    --shadow: 0 1px 2px rgba(28, 25, 20, 0.06);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #0c0c0c;
      --ink: #f3efe4;
      --muted: #c9c2b3;
      --gold: #c9a227;
      --gold-ink: #e4c56a;
      --panel: #141414;
      --line: #3a3218;
      --shadow: none;
    }
  }
  html[data-theme="dark"] {
    color-scheme: dark;
    --bg: #0c0c0c;
    --ink: #f3efe4;
    --muted: #c9c2b3;
    --gold: #c9a227;
    --gold-ink: #e4c56a;
    --panel: #141414;
    --line: #3a3218;
    --shadow: none;
  }
  html[data-theme="light"] {
    color-scheme: light;
    --bg: #f7f4ec;
    --ink: #1c1914;
    --muted: #5e584c;
    --gold: #c9a227;
    --gold-ink: #6d5610;
    --panel: #fffdf8;
    --line: #e6dcc4;
    --shadow: 0 1px 2px rgba(28, 25, 20, 0.06);
  }
  *, *::before, *::after { box-sizing: border-box; }
  html, body { margin: 0; max-width: 100%; overflow-x: clip; background: var(--bg); color: var(--ink); }
  body { font: 16px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  a { color: var(--gold-ink); }
  :focus { outline: none; }
  :focus-visible { outline: 2px solid var(--gold); outline-offset: 3px; }
  .skip {
    position: absolute; left: 0.75rem; top: -3rem;
    background: var(--gold); color: #1a1404; padding: 0.4rem 0.7rem; border-radius: 8px; z-index: 2;
  }
  .skip:focus { top: 0.75rem; }
  .bar {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;
    padding: 0.85rem 1rem; border-bottom: 1px solid var(--line); background: var(--panel);
  }
  .brand { font-weight: 700; }
  .who { color: var(--muted); margin-left: 0.55rem; }
  .wrap { max-width: 40rem; margin: 0 auto; padding: 1.25rem 1.1rem 3rem; }
  h1 { margin: 0.1rem 0 0.45rem; font-size: 1.85rem; line-height: 1.15; font-weight: 650; }
  h2 { margin: 0 0 0.45rem; font-size: 1.15rem; }
  p { margin: 0.4rem 0; }
  .lead { color: var(--muted); }
  .card {
    border: 1px solid var(--line); background: var(--panel); border-radius: 14px;
    padding: 1.15rem 1.2rem; margin: 0 0 1rem; box-shadow: var(--shadow);
  }
  .hero { border-color: var(--gold); }
  .kicker { display: block; color: var(--gold-ink); font-size: 0.75rem; font-weight: 650; letter-spacing: 0.04em; text-transform: uppercase; }
  button, input, select, summary { font: inherit; }
  button {
    background: transparent; color: var(--ink); border: 1px solid var(--line);
    border-radius: 10px; padding: 0.6rem 0.9rem; min-height: 44px; cursor: pointer;
  }
  button.primary {
    background: var(--gold); color: #1a1404; border: 0; font-weight: 700; font-size: 1rem;
    padding: 0.85rem 1.3rem; min-height: 48px;
  }
  button.theme { min-height: 40px; padding: 0.35rem 0.75rem; }
  button:disabled { opacity: 0.6; cursor: wait; }
  .actions { display: flex; flex-wrap: wrap; gap: 0.6rem; margin: 0.9rem 0 0.2rem; }
  .status {
    margin: 0.85rem 0 0; padding: 0.75rem 0.9rem; border-radius: 10px;
    background: var(--bg); color: var(--ink); font-weight: 650;
  }
  .notice { color: var(--muted); min-height: 1.4rem; }
  .next { color: var(--muted); font-size: 0.95rem; }
  .time-row { display: grid; grid-template-columns: 5.5rem minmax(0, 1fr); gap: 0.25rem 0.75rem; margin: 0.35rem 0; }
  .time-k { color: var(--muted); }
  .time-v { overflow-wrap: anywhere; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.85rem; }
  .time-note { margin-top: 0.7rem; }
  .fold {
    border: 1px solid var(--line); border-radius: 14px; background: var(--panel);
    padding: 0.2rem 1.1rem 0.4rem; margin: 0 0 1rem;
  }
  summary { cursor: pointer; font-weight: 650; min-height: 48px; display: flex; align-items: center; }
  .section { border-top: 1px solid var(--line); padding: 0.9rem 0 0.4rem; }
  .hash { font: 0.75rem/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; overflow-wrap: anywhere; white-space: pre-wrap; color: var(--muted); margin: 0.4rem 0 0.8rem; }
  .rolodex { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 16rem), 1fr)); gap: 0.75rem; }
  .goldcard {
    text-align: left; width: 100%; background: var(--bg); color: var(--ink);
    border: 1px solid var(--gold); border-radius: 12px; padding: 0.85rem;
  }
  .goldcard[aria-pressed="true"] { box-shadow: inset 0 0 0 1px var(--gold); }
  .full { display: block; margin-top: 0.45rem; font: 0.75rem/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; overflow-wrap: anywhere; color: var(--muted); }
  input, select {
    width: 100%; background: var(--bg); color: var(--ink); border: 1px solid var(--line);
    padding: 0.55rem 0.7rem; border-radius: 8px;
  }
  label { display: block; margin: 0.7rem 0 0.3rem; }
  .marker { color: var(--gold-ink); }
  .foot { color: var(--muted); font-size: 0.9rem; margin: 0.4rem 0 0; }
  code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.92em; }
  @media (max-width: 480px) {
    .wrap { padding: 1rem 0.9rem 2.5rem; }
    button.primary { width: 100%; }
    h1 { font-size: 1.6rem; }
  }
  @media (prefers-reduced-motion: reduce) {
    * { transition: none !important; }
  }
</style>
</head>
<body>
  <a class="skip" href="#pair">Skip to Pair</a>
  <header class="bar">
    <div><span class="brand">AZNet</span><span class="who">Aziel Eliab</span></div>
    <button type="button" class="theme" id="theme">Theme</button>
  </header>
  <main class="wrap">
    <section class="card hero" id="pair">
      <span class="kicker">On this machine</span>
      <h1>Pair with AZBrowser</h1>
      <p class="lead">AZNet keeps a device-local hash record. Pair before a stamp is written.</p>
      <p id="pair-status" class="status">__STATUS__</p>
      <div class="actions">
        <button type="button" class="primary" id="btn-pair">Pair AZBrowser</button>
      </div>
      <p id="notice" class="notice" role="status"></p>
      <p class="next">Then <code>aznet doctor</code> checks this install.</p>
    </section>

    <section class="card" id="staticclock">
      <h2>Time</h2>
      <div id="clock" class="time"></div>
    </section>

    <details class="fold" id="more">
      <summary>Advanced</summary>

      <section class="section" id="unlock">
        <h2>FragGate unlock</h2>
        <p>Unlock after Pair. FragGate sets the pair flag for garden, stamp, and memorial writes.</p>
        <p>Kernel: <a href="https://github.com/AzielEliab/fraggate">fraggate</a>. Catalog slug <code>aznet</code>.</p>
        <div class="actions">
          <button type="button" id="btn-unlock">FragGate unlock</button>
        </div>
      </section>

      <section class="section" id="garden">
        <h2>Gold Pages</h2>
        <p id="garden-lead">Select a card to fill the stamp field. Cards are hashes, and they are not ranked.</p>
        <div class="rolodex" id="rolodex"></div>
      </section>

      <section class="section" id="stamps">
        <h2>Stamp</h2>
        <p>Stores one hash. Pair and unlock first.</p>
        <label for="hash-hex">Hash (64 hex characters)</label>
        <input id="hash-hex" maxlength="64" autocomplete="off" spellcheck="false" placeholder="64 hex characters">
        <div class="actions">
          <button type="button" id="btn-stamp">Stamp</button>
          <button type="button" id="btn-verify">Check ledger</button>
        </div>
      </section>

      <section class="section" id="memorial">
        <h2>Memorial</h2>
        <p>Writes a terminal record: genesis hash, final hash, time, and a short summary.</p>
        <label for="reason">Reason</label>
        <select id="reason">
          <option>isolation</option>
          <option>ui_altered</option>
          <option>integrity_refuse</option>
          <option>node_withdraw</option>
          <option>pair_broken</option>
          <option>witness_fail</option>
        </select>
        <div class="actions">
          <button type="button" id="btn-memorial">Memorial</button>
          <button type="button" id="btn-withdraw">Withdraw</button>
          <button type="button" id="btn-witness">Witness</button>
        </div>
      </section>

      <section class="section" id="receipts">
        <h2>Ledger</h2>
        <p id="lattice-summary">No receipts yet.</p>
        <details>
          <summary>Receipt record</summary>
          <pre class="hash" id="receipt-list"></pre>
        </details>
      </section>
    </details>

    <details class="fold" id="notes">
      <summary>Notes</summary>
      <p>__HONEST__</p>
      <p class="marker">__MARKER__</p>
    </details>
    <p class="foot">Aziel Eliab · AZN-WP-0.1 · v__VERSION__ · this machine only</p>
  </main>
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
    function statusWords(pair, unlock) {
      if (pair === "PAIRED" && unlock === "UNLOCKED") return "Paired and unlocked.";
      if (pair === "PAIRED") return "Paired. FragGate is still locked.";
      if (pair === "BROKEN") return "Pair is broken. Pair again to continue.";
      if (!pair || pair === "UNPAIRED") return "Not paired yet — click Pair.";
      return "Pair status: " + pair + ".";
    }
    function fail(err) {
      var msg = (err && err.message) ? String(err.message) : "That did not work.";
      var next = "";
      if (msg.indexOf("pair_flag required") !== -1) next = " Next: open Advanced and choose FragGate unlock.";
      else if (msg.indexOf("pair_token") !== -1) next = " Next: click Pair.";
      else if (msg.indexOf("64-char") !== -1) next = " Next: choose a Gold Pages card, then Stamp.";
      else next = " Next: aznet doctor";
      document.getElementById("notice").textContent = msg + next;
    }
    async function api(path, body, button) {
      if (button) button.disabled = true;
      try {
        var res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
        var data = await res.json();
        if (!res.ok) throw new Error(data.error || ("HTTP " + res.status));
        return data;
      } finally {
        if (button) button.disabled = false;
      }
    }
    function show(data) {
      if (data.pair_status) {
        document.getElementById("pair-status").textContent = statusWords(data.pair_status, data.unlock_status || "");
      }
      var line = "";
      if (data.action === "paired") line = "Paired. FragGate is still locked.";
      else if (data.action === "unlocked") line = "Paired and unlocked.";
      else if (data.action === "stamped") line = "Stamp written.";
      else if (data.action === "verify") line = data.ok ? "Ledger intact." : "Ledger check failed.";
      else if (data.action === "memorial") line = "Memorial written.";
      else if (data.action === "withdrawn") line = "This node is withdrawn.";
      else if (data.action === "witness") line = "Witness recorded.";
      else if (data.message) line = data.message;
      if (line) document.getElementById("notice").textContent = line;
      var rows = data.ledger;
      if (Array.isArray(rows)) {
        var summary = document.getElementById("lattice-summary");
        summary.textContent = rows.length === 1 ? "1 receipt in the ledger." : rows.length + " receipts in the ledger.";
        document.getElementById("receipt-list").textContent = JSON.stringify(rows, null, 2);
      }
    }
    function paintTime(t) {
      var root = document.getElementById("clock");
      root.textContent = "";
      [["Zone", t.zone], ["Local", t.local], ["Window", t.window], ["Stamp", t.stamp]].forEach(function (row) {
        var line = document.createElement("div");
        line.className = "time-row";
        var k = document.createElement("div");
        k.className = "time-k";
        k.textContent = row[0];
        var v = document.createElement("div");
        v.className = "time-v";
        v.textContent = row[1] == null ? "" : String(row[1]);
        line.appendChild(k);
        line.appendChild(v);
        root.appendChild(line);
      });
      var note = document.createElement("p");
      note.className = "time-note";
      note.textContent = t.note || "StaticClock stamps time.";
      root.appendChild(note);
    }
    async function refresh() {
      try {
        var g = await fetch("/local/garden").then(function (r) { return r.json(); });
        var cards = g.cards || [];
        var lead = document.getElementById("garden-lead");
        lead.textContent = cards.length + (cards.length === 1 ? " hash card." : " hash cards.") + " They shift together and are not ranked. Select one to fill the stamp field.";
        var box = document.getElementById("rolodex");
        box.textContent = "";
        cards.forEach(function (c) {
          var el = document.createElement("button");
          el.type = "button";
          el.className = "goldcard";
          el.setAttribute("aria-pressed", "false");
          var kicker = document.createElement("span");
          kicker.className = "kicker";
          kicker.textContent = c.label || "card";
          var full = document.createElement("span");
          full.className = "full";
          full.textContent = c.hash_hex || "";
          el.appendChild(kicker);
          el.appendChild(full);
          el.addEventListener("click", function () {
            document.getElementById("hash-hex").value = c.hash_hex || "";
            box.querySelectorAll(".goldcard").forEach(function (node) { node.setAttribute("aria-pressed", "false"); });
            el.setAttribute("aria-pressed", "true");
            document.getElementById("garden-lead").textContent = (c.label || "Card") + " is in the stamp field.";
          });
          box.appendChild(el);
        });
      } catch (err) {
        document.getElementById("garden-lead").textContent = "Gold Pages did not load. Next: reload this page.";
      }
      try {
        var t = await fetch("/local/time").then(function (r) { return r.json(); });
        paintTime(t);
      } catch (err) {
        document.getElementById("clock").textContent = "Time is not available yet. Next: reload this page.";
      }
    }
    var themeMode = "system";
    try { themeMode = localStorage.getItem("aznet-theme") || "system"; } catch (e) {}
    function applyTheme(mode) {
      var root = document.documentElement;
      if (mode === "light" || mode === "dark") root.setAttribute("data-theme", mode);
      else root.removeAttribute("data-theme");
      var btn = document.getElementById("theme");
      var label = mode === "light" ? "Light" : mode === "dark" ? "Dark" : "System";
      btn.textContent = label;
      btn.setAttribute("aria-label", "Color theme: " + label);
      btn.setAttribute("aria-pressed", mode === "dark" ? "true" : "false");
    }
    applyTheme(themeMode);
    document.getElementById("theme").addEventListener("click", function () {
      themeMode = themeMode === "system" ? "light" : themeMode === "light" ? "dark" : "system";
      try { localStorage.setItem("aznet-theme", themeMode); } catch (e) {}
      applyTheme(themeMode);
    });
    document.getElementById("btn-pair").addEventListener("click", function (ev) {
      api("/local/pair", {}, ev.currentTarget).then(show).catch(fail);
    });
    document.getElementById("btn-unlock").addEventListener("click", function (ev) {
      api("/local/unlock", {}, ev.currentTarget).then(show).catch(fail);
    });
    document.getElementById("btn-stamp").addEventListener("click", function (ev) {
      api("/local/stamp", { hash_hex: document.getElementById("hash-hex").value }, ev.currentTarget).then(show).catch(fail);
    });
    document.getElementById("btn-verify").addEventListener("click", function (ev) {
      api("/local/verify", {}, ev.currentTarget).then(show).catch(fail);
    });
    document.getElementById("btn-memorial").addEventListener("click", function (ev) {
      api("/local/memorial", { reason: document.getElementById("reason").value }, ev.currentTarget).then(show).catch(fail);
    });
    document.getElementById("btn-withdraw").addEventListener("click", function (ev) {
      api("/local/withdraw", {}, ev.currentTarget).then(show).catch(fail);
    });
    document.getElementById("btn-witness").addEventListener("click", function (ev) {
      api("/local/witness", { witness_hash: WITNESS }, ev.currentTarget).then(show).catch(fail);
    });
    refresh();
  </script>
</body>
</html>
"""


def pair_words(pair: str, unlock: str) -> str:
    if pair == "PAIRED" and unlock == "UNLOCKED":
        return "Paired and unlocked."
    if pair == "PAIRED":
        return "Paired. FragGate is still locked."
    if pair == "BROKEN":
        return "Pair is broken. Pair again to continue."
    if not pair or pair == "UNPAIRED":
        return "Not paired yet — click Pair."
    return f"Pair status: {pair}."


def render_page() -> str:
    try:
        ledger = Ledger.load(default_ledger_path())
        status = pair_words(ledger.pair_status(), ledger.unlock_status())
    except Exception:
        status = pair_words("UNPAIRED", "LOCKED")
    return (
        PAGE.replace("__MARKER__", html.escape(MARKER))
        .replace("__HONEST__", html.escape(HONEST))
        .replace("__WITNESS__", witness_digest())
        .replace("__SECTIONS__", json.dumps(list(WITNESS_SECTIONS)))
        .replace("__STATUS__", html.escape(status))
        .replace("__VERSION__", html.escape(VERSION))
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


def serve(host: str = "127.0.0.1", port: int = 8771) -> int:
    if host not in {"127.0.0.1", "localhost"}:
        print(f"{host} is not a loopback address. Binding 127.0.0.1.", file=sys.stderr, flush=True)
        host = "127.0.0.1"
    try:
        httpd = ThreadingHTTPServer((host, port), Handler)
    except OSError as exc:
        print(
            f"Could not open port {port} on {host}. {exc}\nNext: aznet ui --port {port + 1}",
            file=sys.stderr,
        )
        return 1
    print(f"Open http://{host}:{port}/", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    return 0
