"""AZNet errors. Author: Aziel Eliab only."""

from __future__ import annotations


class AZNetError(Exception):
    """Base error for AZNet."""


class AppendOnlyError(AZNetError):
    """Raised on any attempt to edit, pop, replace, or delete a receipt."""


class ReceiptError(AZNetError):
    """Raised when a receipt field is invalid."""


class LedgerError(AZNetError):
    """Raised for ledger-level problems."""


class PairError(AZNetError):
    """AZNet + AZBrowser pairing is required. FragGate unlock is required."""


class WitnessError(AZNetError):
    """UI witness failed. Terminate and write a Memorial."""


class InvariantError(AZNetError):
    """Raised when an invariant would be violated."""


class LatticeError(AZNetError):
    """Raised when a lattice walk fails."""


class IntegrityRefuse(AZNetError):
    """Integrity refusal / isolation. Withdraw rather than coerce."""
