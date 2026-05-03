from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

import commands
from commands import Status
from crapi.crapi import CRAPI
from spreadsheet.spreadsheet import Sheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cr-clan-manager",
        description="CR Clan Statistics Managing System",
    )
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    p_init = subparsers.add_parser("init", help="Initialize (setup) the sheet")
    p_init.set_defaults(func=commands.cmd_init)

    p_quit = subparsers.add_parser("quit", help="Quit the REPL")
    p_quit.set_defaults(func=commands.cmd_quit)

    p_show = subparsers.add_parser("show", help="Show information of clan")
    show_subs = p_show.add_subparsers(dest="show_cmd", required=True)

    show_subs.add_parser("members", help="Show all clan members").set_defaults(
        func=commands.show_members
    )
    show_subs.add_parser("race", help="Show current river race").set_defaults(
        func=commands.show_race
    )
    p_show_racelog = show_subs.add_parser("racelog", help="Show racelog (specified number)")
    p_show_racelog.add_argument(
        "count", type=int, nargs="?", default=None, help="Number of records to show"
    )
    p_show_racelog.set_defaults(func=commands.show_racelog)

    p_update = subparsers.add_parser("update", help="Update content of sheet")
    update_subs = p_update.add_subparsers(dest="update_cmd", required=True)

    update_subs.add_parser("members", help="Update members of clan").set_defaults(
        func=commands.update_members
    )
    update_subs.add_parser("trophy", help="Update trophies of members").set_defaults(
        func=commands.update_trophy
    )
    update_subs.add_parser("racelog", help="Update racelog").set_defaults(
        func=commands.update_racelog
    )
    p_update_donation = update_subs.add_parser(
        "donation", help="Update donations of members (specified date)"
    )
    p_update_donation.add_argument("date", nargs="?", default=None, help="Date in YYYYMMDD format")
    p_update_donation.set_defaults(func=commands.update_donation)

    return parser


def run_once(
    parser: argparse.ArgumentParser,
    argv: Sequence[str],
    cr: CRAPI,
    sheet: Sheet,
) -> Status:
    ns = parser.parse_args(argv)
    return ns.func(ns, cr, sheet)


def repl(parser: argparse.ArgumentParser, cr: CRAPI, sheet: Sheet) -> None:
    while True:
        print("❯ ", end="")
        tokens = input().split()
        try:
            status = run_once(parser, tokens, cr, sheet)
        except SystemExit:
            continue
        if status == Status.QUIT:
            break


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    sheet = Sheet()
    cr = CRAPI()
    parser = build_parser()

    if not argv:
        print("CR Clan Statistics Managing System")
        repl(parser, cr, sheet)
        return 0

    try:
        status = run_once(parser, argv, cr, sheet)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 1
    return 0 if status == Status.OK else 1


if __name__ == "__main__":
    sys.exit(main())
