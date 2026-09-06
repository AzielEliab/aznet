"""Command-line interface for AZNet.

    aznet pair
    aznet unlock
    aznet garden
    aznet stamp --hash HEX
    aznet memorial --reason isolation
    aznet receipts
    aznet verify
    aznet time
    aznet witness
    aznet ui
    aznet doctor

Default ledger: ./aznet_ledger.jsonl
Override: AZNET_LEDGER or --ledger.

Author: Aziel Eliab only. Not an alt internet. AZNet + AZBrowser required.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from aznet import __version__
from aznet.chain import Ledger, default_ledger_path
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
from aznet.garden import garden_view
from aznet.witness import expected_witness


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aznet",
        description=(
            "AZNet — silent verification side-net (AZN-WP-0.1, Aziel Eliab). "
            "Not an alt internet. Hashes only. AZNet + AZBrowser required. "
            "Local UI: `aznet ui`."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version", help="Print package version.")

    p_ui = sub.add_parser("ui", help="Run the localhost UI (127.0.0.1:8771).")
    p_ui.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    p_ui.add_argument("--port", type=int, default=8771, help="Bind port (default 8771).")

    p_pair = sub.add_parser("pair", help="Pair AZNet + AZBrowser. Both required to run.")
    p_pair.add_argument("--azbrowser", default="https://github.com/AzielEliab/azbrowser")
    p_pair.add_argument("--aznet-node", default="device-local", dest="aznet_node")
    p_pair.add_argument("--note", default="")
    p_pair.add_argument("--ledger", default=None)

    p_un = sub.add_parser("unlock", help="FragGate unlock after pair.")
    p_un.add_argument("--note", default="")
    p_un.add_argument("--ledger", default=None)

    p_g = sub.add_parser("garden", help="Show Custodian Garden / Gold Pages (demo shift).")
    p_g.add_argument("--ledger", default=None)

    p_st = sub.add_parser("stamp", help="TemporalLock-style stamp of a hash. Hash only.")
    p_st.add_argument("--hash", required=True, dest="hash_hex")
    p_st.add_argument("--note", default="")
    p_st.add_argument("--ledger", default=None)

    p_mem = sub.add_parser("memorial", help="Append a Memorial (terminal compromise).")
    p_mem.add_argument(
        "--reason",
        required=True,
        choices=["ui_altered", "integrity_refuse", "node_withdraw", "pair_broken", "witness_fail", "isolation"],
    )
    p_mem.add_argument("--note", default="")
    p_mem.add_argument("--ledger", default=None)

    p_wd = sub.add_parser("withdraw", help="Withdraw the silent node. Withdrawal over coercion.")
    p_wd.add_argument("--note", default="")
    p_wd.add_argument("--ledger", default=None)

    p_show = sub.add_parser("receipts", help="Print receipts in the ledger.")
    p_show.add_argument("--ledger", default=None)
    p_show.add_argument("file", nargs="?", default=None)

    p_ver = sub.add_parser("verify", help="Walk the lattice; exit 0 if intact.")
    p_ver.add_argument("--ledger", default=None)
    p_ver.add_argument("file", nargs="?", default=None)

    p_lat = sub.add_parser("lattice", help="Verify receipt links + counts.")
    p_lat.add_argument("--ledger", default=None)
    p_lat.add_argument("file", nargs="?", default=None)

    p_time = sub.add_parser("time", help="StaticClock advisory display. Not a scheduler.")
    p_time.add_argument("--ledger", default=None)

    p_wit = sub.add_parser("witness", help="Check the mandatory UI witness hash.")
    p_wit.add_argument("--hash", default=None, dest="witness_hash")
    p_wit.add_argument("--ledger", default=None)

    p_doc = sub.add_parser("doctor", help="Self-check. No network, no telemetry.")
    p_doc.add_argument("--json", action="store_true", dest="as_json")

    p_imp = sub.add_parser("import", help="Import a JSON / JSONL document.")
    p_imp.add_argument("path")

    p_exp = sub.add_parser("export", help="Export a JSON document.")
    p_exp.add_argument("path")

    return parser


def _ledger_path(args: argparse.Namespace) -> Path:
    if getattr(args, "ledger", None):
        return Path(args.ledger)
    if args.cmd in {"receipts", "verify", "lattice"} and getattr(args, "file", None):
        return Path(args.file)
    return default_ledger_path()


def _print_receipt(rec, index: int | None = None) -> None:
    prefix = f"[{index}] " if index is not None else ""
    print(f"{prefix}{rec.event_kind}  hash={rec.receipt_hash}")
    print(f"    prev={rec.prev_hash}  ts={rec.timestamp}")
    if rec.hash_hex:
        print(f"    hash_hex={rec.hash_hex}")
    if rec.pair_status:
        print(f"    pair={rec.pair_status}  unlock={rec.unlock_status}")
    if rec.reason:
        print(f"    reason={rec.reason}  summary={rec.summary}")
    print(f"    payload={rec.payload}  keys={rec.keys}  user_content={rec.user_content}")
    if rec.note:
        print(f"    note: {rec.note}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.cmd == "version":
            print(f"aznet {__version__}")
            return 0

        if args.cmd == "ui":
            from aznet.ui import serve

            serve(host=args.host, port=args.port)
            return 0

        if args.cmd == "pair":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.pair(azbrowser=args.azbrowser, aznet_node=args.aznet_node, note=args.note)
            print(f"paired  {rec.receipt_hash}  azbrowser={rec.azbrowser}")
            return 0

        if args.cmd == "unlock":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.unlock(note=args.note)
            print(f"unlocked  {rec.receipt_hash}  fraggate={rec.fraggate}")
            return 0

        if args.cmd == "garden":
            view = garden_view()
            print(json.dumps(view, indent=2))
            return 0

        if args.cmd == "stamp":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.stamp(args.hash_hex, note=args.note)
            print(f"stamped  {rec.receipt_hash}  hash_hex={rec.hash_hex}")
            print(f"staticclock={rec.staticclock}")
            return 0

        if args.cmd == "memorial":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.memorial(reason=args.reason, note=args.note)
            print(f"memorial  {rec.receipt_hash}  reason={rec.reason}")
            print(f"genesis={rec.genesis_hash}  final={rec.final_hash}")
            return 0

        if args.cmd == "withdraw":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.withdraw(note=args.note)
            print(f"withdrawn  {rec.receipt_hash}")
            return 0

        if args.cmd == "receipts":
            path = _ledger_path(args)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            ledger = Ledger.load(path)
            rows = ledger.show()
            print(f"aznet ledger  n={len(rows)}  path={path}")
            for i, rec in enumerate(rows):
                _print_receipt(rec, i)
            return 0

        if args.cmd == "verify":
            path = _ledger_path(args)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            ledger = Ledger.load(path)
            result = ledger.verify()
            payload = {
                "ok": result.ok,
                "length": result.length,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
            }
            print(json.dumps(payload, indent=2))
            return 0 if result.ok else 1

        if args.cmd == "lattice":
            from aznet.lattice import walk

            path = _ledger_path(args)
            if not path.is_file():
                print(f"not found: {path}", file=sys.stderr)
                return 2
            ledger = Ledger.load(path)
            result = walk(ledger)
            payload = {
                "ok": result.ok,
                "length": result.length,
                "garden": result.garden,
                "stamps": result.stamps,
                "memorials": result.memorials,
                "pairs": result.pairs,
                "unlocks": result.unlocks,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
                "role": result.role,
            }
            print(json.dumps(payload, indent=2))
            return 0 if result.ok else 1

        if args.cmd == "time":
            from aznet.clock import advise

            print(json.dumps(advise(), indent=2))
            return 0

        if args.cmd == "witness":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.witness(args.witness_hash or expected_witness())
            print(f"witness  {rec.receipt_hash}  {rec.witness_hash}")
            return 0

        if args.cmd == "doctor":
            from aznet.doctor import run_doctor

            return run_doctor(as_json=getattr(args, "as_json", False))

        if args.cmd == "import":
            from aznet.jsonio import import_json

            rec = import_json(args.path)
            sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
            return 0

        if args.cmd == "export":
            from aznet.jsonio import export_json

            rec = export_json(args.path)
            sys.stdout.write(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
            return 0

        parser.error(f"unknown command {args.cmd}")
        return 2
    except WitnessError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except PairError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (ReceiptError, LedgerError, AppendOnlyError, InvariantError, LatticeError, IntegrityRefuse, AZNetError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
