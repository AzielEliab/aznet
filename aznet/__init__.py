"""AZNet: silent verification side-net.

AZN-WP-0.1. Author: Aziel Eliab only.

Not an alt internet. Not a host. Not a payload store. Not a VPN.
AZNet + AZBrowser are both required to run. FragGate unlocks access.
StaticClock stamps time. Forks are welcome and always allowed.
"""

from __future__ import annotations

from aznet.canon import ABSENT, GENESIS_PREV_HASH, MARKER, SPEC
from aznet.chain import Ledger, VerifyResult
from aznet.errors import (
    AZNetError,
    AppendOnlyError,
    IntegrityRefuse,
    InvariantError,
    LatticeError,
    LedgerError,
    PairError,
    ReceiptError,
    WitnessError,
)
from aznet.hashing import canonical_bytes, digest
from aznet.lattice import verify_lattice
from aznet.receipt import Receipt

__version__ = "0.1.0"
__author__ = "Aziel Eliab"
__all__ = [
    "ABSENT",
    "AZNetError",
    "AppendOnlyError",
    "GENESIS_PREV_HASH",
    "IntegrityRefuse",
    "InvariantError",
    "LatticeError",
    "Ledger",
    "LedgerError",
    "MARKER",
    "PairError",
    "Receipt",
    "ReceiptError",
    "SPEC",
    "VerifyResult",
    "WitnessError",
    "canonical_bytes",
    "digest",
    "verify_lattice",
    "__version__",
]
