# Contributing to AZNet

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute. Pull requests are welcome
if you want a change upstream. Keep a fork forever if you do not.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core is stdlib only (`hashlib`, `json`, `argparse`).
pytest is the dev extra. No network.

## Ground rules

1. **Identity is Aziel Eliab only.** Do not credit other names.
2. **I1 Hashes only.** `payload`, `keys`, and `user_content` are always `ABSENT`.
3. **I2 Presence without authority.** Garden is non-ranked. No favorites.
4. **I3 Withdrawal over coercion.** A node may withdraw. Do not add force.
5. **I4 Silence as security.** No analytics, personalization, or engagement.
6. **I5 Hash continuity.** Append-only SHA-256 lattice.
7. **I6 UI is a mandatory witness.** If the UI is altered, terminate and memorial.
8. **I7 Pairing required.** AZNet + AZBrowser both required to run.
9. **I8 Memorial is non-actionable.** Genesis / final hash, timestamps, closed-set summary. No exploit details.
10. **I9 Worker is a demo garden.** Do not claim the Worker is the silent node.
11. **I10 No persuasion / engagement optimization.**
12. **Do not wire** Lumen, AZInterface, AZ-OS Hub, or Interface products.
13. New behavior needs a test that fails without the change.

## Where to change things

- Canonical encoding / SHA-256: `aznet/canon.py`, `aznet/hashing.py`
- Receipt dataclass: `aznet/receipt.py`
- Ledger / lattice: `aznet/chain.py`, `aznet/lattice.py`
- Garden: `aznet/garden.py`
- Pairing / witness: `aznet/chain.py`, `aznet/witness.py`
- CLI: `aznet/cli.py`
- Errors: `aznet/errors.py`
- Suite mesh / QNM Live Nodes: `workers/download-tracker/src/mesh.js` (`/v1/mesh/*` PROXY to aziel-runtime). Local ops are `/v1/{op}` only. Never treat `fraggate/call` or `mesh/status` as a local op name. Suite mesh default OFF; QNM rollup live|locked|isolated; no Node Gate; no auto-heal; not anonymity.

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Author: Aziel Eliab only.
