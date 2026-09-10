# aznet download tracker

Isolated Worker `aznet-download-tracker`. Project `aznet`.
v0.1.0 serves the silent verification side-net (AZN-WP-0.1).
KV namespace `AZNET_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` is the product homepage (Garden Rolodex + counted download). Increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads** and serves the tarball (HTTP 200, live counter, no 302).
GET `/count` returns `{views, downloads, total}`.
GET `/stats` returns views, downloads, `by_repo` / `by_branch` / `by_fork`.
`/v1` and `/mcp` never increment DOWNLOADS KV.
GET|POST `/mcp` is a FragGate pointer (never 404) to slug=`aznet` on aziel-runtime. Not a second MCP.
`/v1/fraggate/*` (list / describe / call / verify) PROXY to aziel-runtime via the `AZIEL_RUNTIME` service binding.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (local qnsd in https://github.com/AzielEliab/qnm-node; runtime cites in https://github.com/AzielEliab/aziel-runtime; pair custody https://github.com/AzielEliab/azinterface). Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Human UI Live Nodes strip polls `GET /v1/mesh`.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.
GET `/cite.json` (and `/cite`), `/sitemap.xml`, `/robots.txt`, `/llms.txt` (and `/ai.txt`) are SEO / cite surfaces. `robots.txt` is a hardcoded Aziel Eliab AI Allow list (`User-agent: *` + GPTBot / ChatGPT-User / Google-Extended / Claude / Perplexity / …). It must never interpolate workspace directory names. Do not increment downloads.

The Worker is a control-plane / demo garden. Device-local silent node is the real posture.

Host: https://aznet-download-tracker.vibelock.workers.dev
