# aznet download tracker

Isolated Worker `aznet-download-tracker`. Project `aznet`.
v0.1.0 serves the silent verification side-net (AZN-WP-0.1).
KV namespace `AZNET_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` is the product homepage (Garden Rolodex + counted download). Increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
`/v1` never increments DOWNLOADS KV.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.
GET `/cite.json`, `/sitemap.xml`, `/robots.txt`, `/llms.txt` are SEO / cite surfaces. Do not increment downloads.

The Worker is a control-plane / demo garden. Device-local silent node is the real posture.

Host: https://aznet-download-tracker.vibelock.workers.dev
