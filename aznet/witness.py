"""UI is a mandatory witness. If altered, terminate and memorial.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from aznet.canon import MARKER, SPEC, WITNESS_SECTIONS, witness_digest
from aznet.errors import WitnessError


def expected_witness() -> str:
    return witness_digest()


def check_witness(witness_hash: str | None) -> str:
    expected = expected_witness()
    if not witness_hash or witness_hash != expected:
        raise WitnessError(
            "UI witness failed. Terminate and memorial. "
            f"{MARKER} Expected {expected}."
        )
    return expected


def witness_payload() -> dict[str, object]:
    return {
        "marker": MARKER,
        "spec": SPEC,
        "sections": list(WITNESS_SECTIONS),
        "witness_hash": expected_witness(),
        "rule": "If the UI is altered, terminate and write a Memorial (ui_altered).",
    }
