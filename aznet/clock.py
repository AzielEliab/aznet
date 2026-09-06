"""StaticClock advisory stamps for AZNet. Not a scheduler.

StaticClock controls time on the side-net. Five advisory fields.
Author: Aziel Eliab only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from aznet.canon import MARKER, sha256_text


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def advise(now: str | None = None, *, zone: str = "UTC") -> dict[str, Any]:
    """Five advisory fields. Not a scheduler. Not a clock-in product."""
    stamp_at = now or utc_now()
    return {
        "zone": zone,
        "local": stamp_at,
        "window": "advisory stamp window",
        "stamp": sha256_text(f"{stamp_at}|{zone}|{MARKER}"),
        "note": "StaticClock stamps time. Not a scheduler.",
        "product": "staticclock",
        "github": "https://github.com/AzielEliab/staticclock",
        "worker": "https://staticclock-download-tracker.vibelock.workers.dev/",
    }
