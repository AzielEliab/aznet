"""Command-line interface for AZNet.

    aznet
    aznet ui
    aznet pair
    aznet doctor
    aznet time
    aznet time --json

Default ledger: ./aznet_ledger.jsonl
Override: AZNET_LEDGER or --ledger.

Author: Aziel Eliab only.
"""

from __future__ import annotations

import argparse
import json
import re
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

HELP = f"""\
usage: aznet [--json] <command> [options]

AZNet keeps a device-local hash record and pairs with AZBrowser
before a stamp is written.

Author: Aziel Eliab

Common commands:
  ui         Open the local page (http://127.0.0.1:8771)
  pair       Pair this node with AZBrowser
  unlock     FragGate unlock after pair
  doctor     Pass/fail check of this install
  time       Advisory time stamp, in words
  garden     Gold Pages hash cards
  receipts   List ledger receipts
  verify     Check the hash chain
  version    Print the package version
  help       Show this help

Advanced:
  stamp      Stamp one 64-character hash
  memorial   Append a memorial record
  withdraw   Withdraw this node
  witness    Check the UI witness hash
  lattice    Count linked receipts
  names      Mesh-name rules for .aziel
  resolve    Look up one name on the local ledger
  import     Import a JSON document
  export     Export a JSON document

Examples:
  aznet
  aznet ui
  aznet pair
  aznet doctor
  aznet time --json

--json prints the same fields the local API returns.
Version {__version__}.
"""


def _welcome() -> str:
    return (
        f"AZNet {__version__} — Aziel Eliab\n"
        "\n"
        "AZNet keeps a device-local hash record and pairs with AZBrowser before a stamp is written.\n"
        "\n"
        "Next: pair this node, or open the local page.\n"
        "\n"
        "  aznet pair\n"
        "  aznet ui\n"
        "  aznet doctor\n"
        "  aznet --help\n"
    )


def _plain_misuse(prog: str, message: str) -> str:
    command = prog.split()[-1] if prog else "aznet"
    choice = re.search(r"invalid choice: '([^']*)'", message)
    if choice and "argument cmd" in message:
        name = choice.group(1)
        return f'Unknown command "{name}". Try: aznet ui   or   aznet --help'
    if choice and "--reason" in message:
        return (
            "That memorial reason is not recognized.\n"
            "Next: aznet memorial --reason isolation"
        )
    if "required" in message and "--hash" in message:
        return (
            "Stamp needs a 64-character hex hash.\n"
            "Next: aznet stamp --hash <64 hex characters>"
        )
    if "required" in message and "--reason" in message:
        return (
            "Memorial needs a reason.\n"
            "Next: aznet memorial --reason isolation"
        )
    if "required" in message and command == "resolve":
        return "Resolve needs a name.\nNext: aznet resolve <name>.aziel"
    if "required" in message and command in {"import", "export"}:
        return f"{command.capitalize()} needs a file path.\nNext: aznet {command} <file>"
    if message.startswith("unrecognized arguments"):
        return f"{message}\nNext: {prog} --help"
    return f"{message}\nNext: aznet --help"


class FriendlyParser(argparse.ArgumentParser):
    def format_help(self) -> str:
        if self.prog == "aznet":
            return HELP
        return super().format_help()

    def error(self, message: str) -> None:
        self.exit(2, _plain_misuse(self.prog, message) + "\n")


def _json_arg(parser: argparse.ArgumentParser, *, suppress: bool) -> None:
    kwargs: dict = {
        "action": "store_true",
        "dest": "json",
        "help": "Print machine-readable JSON.",
    }
    if suppress:
        kwargs["default"] = argparse.SUPPRESS
    parser.add_argument("--json", **kwargs)


def _wants_json(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "json", False) or getattr(args, "as_json", False))


def _emit_json(payload: object, *, ensure_ascii: bool = True) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=ensure_ascii))


def _build_parser() -> FriendlyParser:
    parser = FriendlyParser(
        prog="aznet",
        description="AZNet keeps a device-local hash record. Author: Aziel Eliab.",
    )
    _json_arg(parser, suppress=False)
    sub = parser.add_subparsers(dest="cmd", required=False, parser_class=FriendlyParser)

    sub.add_parser("version", help="Print the package version.")
    sub.add_parser("help", help="Show commands and examples.")

    p_ui = sub.add_parser("ui", help="Open the local page at http://127.0.0.1:8771.")
    p_ui.add_argument(
        "--host",
        default="127.0.0.1",
        help="Requested bind host. Only 127.0.0.1 and localhost are kept.",
    )
    p_ui.add_argument("--port", type=int, default=8771, help="Bind port (default 8771).")

    p_pair = sub.add_parser("pair", help="Pair this node with AZBrowser.")
    _json_arg(p_pair, suppress=True)
    p_pair.add_argument("--azbrowser", default="https://github.com/AzielEliab/azbrowser")
    p_pair.add_argument("--aznet-node", default="device-local", dest="aznet_node")
    p_pair.add_argument("--note", default="")
    p_pair.add_argument("--ledger", default=None)

    p_un = sub.add_parser("unlock", help="FragGate unlock after pair.")
    _json_arg(p_un, suppress=True)
    p_un.add_argument("--note", default="")
    p_un.add_argument("--ledger", default=None)

    p_g = sub.add_parser("garden", help="Show Gold Pages hash cards.")
    _json_arg(p_g, suppress=True)
    p_g.add_argument("--ledger", default=None)

    p_st = sub.add_parser("stamp", help="Stamp one 64-character hash.")
    _json_arg(p_st, suppress=True)
    p_st.add_argument("--hash", required=True, dest="hash_hex")
    p_st.add_argument("--note", default="")
    p_st.add_argument("--ledger", default=None)

    p_mem = sub.add_parser("memorial", help="Append a memorial record.")
    _json_arg(p_mem, suppress=True)
    p_mem.add_argument(
        "--reason",
        required=True,
        choices=["ui_altered", "integrity_refuse", "node_withdraw", "pair_broken", "witness_fail", "isolation"],
    )
    p_mem.add_argument("--note", default="")
    p_mem.add_argument("--ledger", default=None)

    p_wd = sub.add_parser("withdraw", help="Withdraw this node.")
    _json_arg(p_wd, suppress=True)
    p_wd.add_argument("--note", default="")
    p_wd.add_argument("--ledger", default=None)

    p_show = sub.add_parser("receipts", help="List ledger receipts.")
    _json_arg(p_show, suppress=True)
    p_show.add_argument("--ledger", default=None)
    p_show.add_argument("file", nargs="?", default=None)

    p_ver = sub.add_parser("verify", help="Check the hash chain.")
    _json_arg(p_ver, suppress=True)
    p_ver.add_argument("--ledger", default=None)
    p_ver.add_argument("file", nargs="?", default=None)

    p_lat = sub.add_parser("lattice", help="Count linked receipts.")
    _json_arg(p_lat, suppress=True)
    p_lat.add_argument("--ledger", default=None)
    p_lat.add_argument("file", nargs="?", default=None)

    p_time = sub.add_parser("time", help="Show the StaticClock advisory stamp.")
    _json_arg(p_time, suppress=True)
    p_time.add_argument("--ledger", default=None)

    p_wit = sub.add_parser("witness", help="Check the UI witness hash.")
    _json_arg(p_wit, suppress=True)
    p_wit.add_argument("--hash", default=None, dest="witness_hash")
    p_wit.add_argument("--ledger", default=None)

    p_doc = sub.add_parser("doctor", help="Pass/fail check. No network, no telemetry.")
    p_doc.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable JSON.")

    p_names = sub.add_parser("names", help="Show mesh-name rules for .aziel.")
    _json_arg(p_names, suppress=True)

    p_res = sub.add_parser("resolve", help="Look up one name on the local name ledger.")
    _json_arg(p_res, suppress=True)
    p_res.add_argument("name")
    p_res.add_argument("--names", default=None, help="Name ledger path (default AZNET_NAMES or ./aznet_names.jsonl).")
    p_res.add_argument("--now", default=None, help="TemporalLock timeslate used to evaluate expiry.")

    p_imp = sub.add_parser("import", help="Import a JSON document.")
    _json_arg(p_imp, suppress=True)
    p_imp.add_argument("path")

    p_exp = sub.add_parser("export", help="Export a JSON document.")
    _json_arg(p_exp, suppress=True)
    p_exp.add_argument("path")

    return parser


def _ledger_path(args: argparse.Namespace) -> Path:
    if getattr(args, "ledger", None):
        return Path(args.ledger)
    if args.cmd in {"receipts", "verify", "lattice"} and getattr(args, "file", None):
        return Path(args.file)
    return default_ledger_path()


def _missing_ledger(path: Path) -> int:
    print(f"No ledger at {path}.\nNext: aznet pair", file=sys.stderr)
    return 2


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


def _print_garden(view: dict) -> None:
    cards = view.get("cards") or []
    print(view.get("name") or "Custodian Garden / Gold Pages")
    print(f"{len(cards)} hash cards. Not ranked. No favorites.")
    for card in cards:
        print(f"  {card.get('label', 'card')}  {card.get('hash_hex', '')}")
    print("Select a card in aznet ui, or stamp a hash after pair and unlock.")


def _print_time(clock: dict) -> None:
    print("Time")
    print(f"  Zone    {clock.get('zone', '')}")
    print(f"  Local   {clock.get('local', '')}")
    print(f"  Window  {clock.get('window', '')}")
    print(f"  Stamp   {clock.get('stamp', '')}")
    note = clock.get("note") or ""
    if note:
        print(note)


def _print_verify(payload: dict) -> None:
    if payload["ok"]:
        print(f"Ledger intact. {payload['length']} receipt(s).")
    else:
        print(f"Ledger check failed. {payload['length']} receipt(s).")
    if payload.get("first_hash"):
        print(f"  First  {payload['first_hash']}")
    if payload.get("last_hash"):
        print(f"  Last   {payload['last_hash']}")
    for err in payload.get("errors") or []:
        print(f"  {err}")
    if not payload["ok"]:
        print("Next: aznet receipts")


def _print_lattice(payload: dict) -> None:
    state = "intact" if payload["ok"] else "failed"
    print(f"Lattice {state}.")
    print(f"  Receipts   {payload['length']}")
    print(f"  Garden     {payload['garden']}")
    print(f"  Stamps     {payload['stamps']}")
    print(f"  Memorials  {payload['memorials']}")
    print(f"  Pairs      {payload['pairs']}")
    print(f"  Unlocks    {payload['unlocks']}")
    for err in payload.get("errors") or []:
        print(f"  {err}")
    if not payload["ok"]:
        print("Next: aznet verify")


def _print_names(surface: dict) -> None:
    print("Mesh names")
    print(f"  Spec     {surface.get('spec', '')}")
    print(f"  TLD      .{surface.get('mesh_tld', '')}")
    print(f"  Handle   {surface.get('handle', '')}")
    print(f"  Final    {surface.get('finality', '')}")
    user = surface.get("user_slots", "")
    reserved = surface.get("reserved_slots", "")
    cap = surface.get("cap_per_handle", "")
    print(f"  Cap      {cap} per handle ({user} user, {reserved} reserved)")
    print("Look up a name with: aznet resolve <name>")


def _print_resolve(data: dict) -> None:
    state = "ok" if data.get("ok") else "refused"
    print(f"{data.get('query', '')}  {data.get('code', '')}  ({state})")
    detail = data.get("detail") or ""
    if detail:
        print(f"  {detail}")
    if data.get("owner"):
        print(f"  Owner   {data['owner']}")
    if data.get("target"):
        print(f"  Target  {data['target']}")
    if not data.get("ok"):
        print("Next: aznet names")


def _exit_code(exc: SystemExit) -> int:
    code = exc.code
    if code is None or code == 0:
        return 0
    if isinstance(code, int):
        return code
    return 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as exc:
        return _exit_code(exc)

    try:
        if args.cmd is None:
            print(_welcome(), end="")
            if _wants_json(args):
                print("Add a command for JSON. Try: aznet time --json")
            return 0

        if args.cmd == "help":
            print(HELP, end="")
            return 0

        if args.cmd == "version":
            if _wants_json(args):
                _emit_json({"product": "AZNet", "version": __version__, "author": "Aziel Eliab"})
            else:
                print(f"aznet {__version__}")
            return 0

        if args.cmd == "ui":
            from aznet.ui import serve

            return serve(host=args.host, port=args.port)

        as_json = _wants_json(args)

        if args.cmd == "pair":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.pair(azbrowser=args.azbrowser, aznet_node=args.aznet_node, note=args.note)
            if as_json:
                _emit_json(rec.to_dict())
            else:
                print(f"paired  {rec.receipt_hash}  azbrowser={rec.azbrowser}")
            return 0

        if args.cmd == "unlock":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.unlock(note=args.note)
            if as_json:
                _emit_json(rec.to_dict())
            else:
                print(f"unlocked  {rec.receipt_hash}  fraggate={rec.fraggate}")
            return 0

        if args.cmd == "garden":
            view = garden_view()
            if as_json:
                _emit_json(view)
            else:
                _print_garden(view)
            return 0

        if args.cmd == "stamp":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.stamp(args.hash_hex, note=args.note)
            if as_json:
                _emit_json(rec.to_dict())
            else:
                print(f"stamped  {rec.receipt_hash}  hash_hex={rec.hash_hex}")
                print(f"staticclock={rec.staticclock}")
            return 0

        if args.cmd == "memorial":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.memorial(reason=args.reason, note=args.note)
            if as_json:
                _emit_json(rec.to_dict())
            else:
                print(f"memorial  {rec.receipt_hash}  reason={rec.reason}")
                print(f"genesis={rec.genesis_hash}  final={rec.final_hash}")
            return 0

        if args.cmd == "withdraw":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.withdraw(note=args.note)
            if as_json:
                _emit_json(rec.to_dict())
            else:
                print(f"withdrawn  {rec.receipt_hash}")
            return 0

        if args.cmd == "receipts":
            path = _ledger_path(args)
            if not path.is_file():
                return _missing_ledger(path)
            ledger = Ledger.load(path)
            rows = ledger.show()
            if as_json:
                _emit_json(ledger.as_rows())
            else:
                print(f"aznet ledger  n={len(rows)}  path={path}")
                for i, rec in enumerate(rows):
                    _print_receipt(rec, i)
            return 0

        if args.cmd == "verify":
            path = _ledger_path(args)
            if not path.is_file():
                return _missing_ledger(path)
            ledger = Ledger.load(path)
            result = ledger.verify()
            payload = {
                "ok": result.ok,
                "length": result.length,
                "first_hash": result.first_hash,
                "last_hash": result.last_hash,
                "errors": result.errors,
            }
            if as_json:
                _emit_json(payload)
            else:
                _print_verify(payload)
            return 0 if result.ok else 1

        if args.cmd == "lattice":
            from aznet.lattice import walk

            path = _ledger_path(args)
            if not path.is_file():
                return _missing_ledger(path)
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
            if as_json:
                _emit_json(payload)
            else:
                _print_lattice(payload)
            return 0 if result.ok else 1

        if args.cmd == "time":
            from aznet.clock import advise

            clock = advise()
            if as_json:
                _emit_json(clock)
            else:
                _print_time(clock)
            return 0

        if args.cmd == "witness":
            ledger = Ledger.load(_ledger_path(args))
            rec = ledger.witness(args.witness_hash or expected_witness())
            if as_json:
                _emit_json(rec.to_dict())
            else:
                print(f"witness  {rec.receipt_hash}  {rec.witness_hash}")
            return 0

        if args.cmd == "doctor":
            from aznet.doctor import run_doctor

            return run_doctor(as_json=_wants_json(args))

        if args.cmd == "names":
            from aznet.names import honesty

            surface = honesty()
            if as_json:
                _emit_json(surface)
            else:
                _print_names(surface)
            return 0

        if args.cmd == "resolve":
            from aznet.names import resolve
            from aznet.names.ledger import default_names_path

            path = Path(args.names) if args.names else default_names_path()
            result = resolve(path, args.name, now=args.now)
            data = result.to_dict()
            if as_json:
                _emit_json(data)
            else:
                _print_resolve(data)
            return 0 if result.ok else 1

        if args.cmd == "import":
            from aznet.jsonio import import_json

            rec = import_json(args.path)
            if as_json:
                _emit_json(rec, ensure_ascii=False)
            else:
                print(f"Imported {rec.get('count', 0)} rows from {rec.get('imported', args.path)}.")
                print(f"Stored at {rec.get('stored', '')}.")
            return 0

        if args.cmd == "export":
            from aznet.jsonio import export_json

            rec = export_json(args.path)
            if as_json:
                _emit_json(rec, ensure_ascii=False)
            else:
                print(f"Exported to {rec.get('exported', args.path)}.")
            return 0

        print(f'Unknown command "{args.cmd}". Try: aznet ui   or   aznet --help', file=sys.stderr)
        return 2
    except WitnessError as exc:
        print(f"{exc}\nNext: aznet receipts", file=sys.stderr)
        return 3
    except PairError as exc:
        text = str(exc)
        hint = "Next: aznet unlock" if "pair_flag required" in text else "Next: aznet pair"
        print(f"{text}\n{hint}", file=sys.stderr)
        return 2
    except (ReceiptError, LedgerError, AppendOnlyError, InvariantError, LatticeError, IntegrityRefuse, AZNetError) as exc:
        print(f"{exc}\nNext: aznet --help", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"{exc}\nNext: check the path, or run aznet --help", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
