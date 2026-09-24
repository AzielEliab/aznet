"""AZNet mesh naming library (AZN-NAME-1.0).

Usable by AZBrowser and qnm-node. AZNet and AZBrowser stay separate
software; this package only resolves names. It does not host payloads
and it does not accept private keys into the ledger.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from aznet.names.ledger import NameLedger, default_names_path
from aznet.names.namespace import honesty
from aznet.names.record import sign_record
from aznet.names.resolver import ResolveResult, resolve

__all__ = [
    "NameLedger",
    "ResolveResult",
    "default_names_path",
    "honesty",
    "resolve",
    "sign_record",
]
