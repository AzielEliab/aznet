# AZNet

**Silent verification SIDE-NET — hash continuity without hosting**

Aziel Eliab
September 2026
License: Apache-2.0
Spec: AZN-WP-0.1

> Truth Is No Defense — .AZNet — AZ.

## Abstract

AZNet is an open-source silent verification side-net. It is not an
alternate internet. It does not host payloads. It does not store keys
or user content. It mirrors cryptographic hashes so a device-local
silent node can verify continuity without granting anyone authority
over the node.

The Worker homepage is a control-plane / demo garden. Honest scope:
the hosted surface demonstrates the garden, the Memorial, stamps, and
receipts. The real posture is device-local.

AZNet + AZBrowser are both required to run. AZBrowser views the
side-net. FragGate unlocks access. StaticClock stamps time.

This document is the specification implemented by the `aznet`
Python package (v0.1.0). Forks are welcome and always allowed.

---

## 1. Purpose

Networks that host become networks that rule. AZNet refuses that
trade. Verification is enough. Presence does not become authority.
When integrity fails, the node withdraws. Silence is the security
model, not persuasion.

Whitepaper themes:

- **Node sovereignty** — the device-local silent node is first.
- **Hash continuity** — SHA-256 lattice receipts; genesis and tip.
- **Integrity refusal / isolation** — refuse leakage; isolate rather than coerce.
- **Memorial ledger** — terminal compromise is recorded, not exploited.
- **Cold storage** — hashes survive without payloads.
- **No persuasion / engagement optimization** — no favorites, ranks, or analytics.

---

## 2. Invariants

| Id | Rule |
|----|------|
| I1 | Hashes only. `payload`, `keys`, `user_content` are always `ABSENT`. |
| I2 | Presence without authority. Garden is non-ranked. No favorites. |
| I3 | Withdrawal over coercion. A node may leave. Nothing forces stay. |
| I4 | Silence as security. No analytics, personalization, or engagement. |
| I5 | Hash continuity. Append-only SHA-256 lattice. |
| I6 | UI is a mandatory witness. Altered UI terminates and writes a Memorial. |
| I7 | Pairing required. AZNet + AZBrowser both required to run. |
| I8 | Memorial is non-actionable. Genesis / final hash, timestamps, closed-set summary. No exploit details. |
| I9 | Worker is a demo garden. Device-local silent node is the real posture. |
| I10 | No persuasion / engagement optimization. |

---

## 3. Custodian Garden / Gold Pages

A shifting, non-ranked directory of hashes. Cards rotate by
StaticClock stamp. Hover reveal. Click is manual intent. There is no
favorite list, no personalization, and no analytics.

Demo cards on the Worker are public labels hashed in-process. They
are not user content and not payloads.

---

## 4. Stamping ledger

A TemporalLock-style stamp binds a hash to a StaticClock advisory
stamp. The stamp is a receipt. It is not a scheduler and not a host.

---

## 5. Memorial ledger

Terminal compromise writes:

- `genesis_hash`
- `final_hash`
- `timestamp` / `date_stamp`
- `reason` / `summary` from a closed set: `ui_altered`,
  `integrity_refuse`, `node_withdraw`, `pair_broken`, `witness_fail`,
  `isolation`

No exploit details. No payloads. No keys.

---

## 6. Pairing

AZNet, AZBrowser, and FragGate are separate apps with separate Worker
UIs. Do not embed AZNet chrome inside AZBrowser or FragGate.

Functional order only: issue a `pair_token`, then set FragGate
`pair_flag`, then garden / stamp / memorial writes. Health, skill,
pair, and time remain available so an operator can complete the pair.
AZBrowser may view side-net status from its own UI by calling this
runtime.

AZBrowser: https://github.com/AzielEliab/azbrowser

Do not wire Lumen, AZInterface, AZ-OS Hub, or Interface products.

---

## 7. UI witness

The UI is part of the product law. Required sections: garden,
memorial, stamps, receipts, pair, unlock, staticclock. The witness
hash is SHA-256 of the marker, the section list, and the spec. If the
hash does not match, AZNet terminates and writes a Memorial
(`ui_altered`).

Marker: `Truth Is No Defense — .AZNet — AZ.`

---

## 8. Honest banner

THIS IS: a silent verification SIDE-NET.
THIS IS NOT: an alt internet, a host, a payload store, a VPN, or a key store.

Author: Aziel Eliab only.
License: Apache-2.0.
Forks are welcome and always allowed.
