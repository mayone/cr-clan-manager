from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum, auto

import display
from crapi.crapi import CRAPI
from spreadsheet.spreadsheet import Sheet


class Status(IntEnum):
    OK = auto()
    FAIL = auto()
    QUIT = auto()


CMD_HELP = (
    "Commands\n"
    "    init          Initialize (setup) the sheet\n"
    "    update        Update content of sheet\n"
    "    show          Show information of clan\n"
    "    quit          Quit\n"
)

SHOW_HELP = (
    "Show (show)\n"
    "    members               Show all clan members\n"
    "    race                  Show current river race\n"
    "    racelog [count]       Show racelog (specified number)\n"
)

UPDATE_HELP = (
    "Update (update)\n"
    "    members               Update members of clan\n"
    "    trophy                Update trophies of members\n"
    "    racelog               Update racelog\n"
    "    donation [date]       Update donations of members (specified date)\n"
)

HandlerFn = Callable[[list[str], CRAPI, Sheet], Status]


def _show_members(args: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    display.show_members(cr.get_members())
    return Status.OK


def _show_race(args: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    display.show_race(cr.get_race(), cr.get_clan_tag())
    return Status.OK


def _show_racelog(args: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    if args:
        try:
            count = int(args.pop(0))
        except ValueError:
            print(SHOW_HELP)
            return Status.FAIL
        display.show_racelog(cr.get_racelog(count), cr.get_clan_tag())
    else:
        display.show_racelog(cr.get_racelog(), cr.get_clan_tag())
    return Status.OK


def _update_members(args: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    sheet.update_members()
    return Status.OK


def _update_trophy(args: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    sheet.update_trophies()
    return Status.OK


def _update_racelog(args: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    sheet.update_racelog()
    return Status.OK


def _update_donation(args: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    if args:
        sheet.update_donations(date=args.pop(0))
    else:
        sheet.update_donations()
    return Status.OK


SHOW_COMMANDS: dict[str, HandlerFn] = {
    "members": _show_members,
    "race": _show_race,
    "racelog": _show_racelog,
}

UPDATE_COMMANDS: dict[str, HandlerFn] = {
    "members": _update_members,
    "trophy": _update_trophy,
    "racelog": _update_racelog,
    "donation": _update_donation,
}


def _dispatch(
    cmd: list[str],
    dispatch_table: dict[str, HandlerFn],
    help_text: str,
    cr: CRAPI,
    sheet: Sheet,
) -> Status:
    if not cmd:
        print(help_text)
        return Status.FAIL
    tok = cmd.pop(0)
    handler = dispatch_table.get(tok)
    if handler:
        return handler(cmd, cr, sheet)
    print(help_text)
    return Status.FAIL


def command_handler(cmd: list[str], cr: CRAPI, sheet: Sheet) -> Status:
    if not cmd:
        print(CMD_HELP)
        return Status.FAIL

    tok = cmd.pop(0)
    if tok == "init":
        sheet.init()
        return Status.OK
    elif tok == "update":
        return _dispatch(cmd, UPDATE_COMMANDS, UPDATE_HELP, cr, sheet)
    elif tok == "show":
        return _dispatch(cmd, SHOW_COMMANDS, SHOW_HELP, cr, sheet)
    elif tok == "quit":
        return Status.QUIT
    else:
        print(CMD_HELP)
        return Status.FAIL


def main() -> None:
    sheet = Sheet()
    cr = CRAPI()

    print("CR Clan Statistics Managing System")
    while True:
        print("❯ ", end="")
        cmd = input().split()
        ret = command_handler(cmd, cr, sheet)
        if ret == Status.QUIT:
            break


if __name__ == "__main__":
    main()
