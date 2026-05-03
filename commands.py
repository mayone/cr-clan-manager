from __future__ import annotations

import argparse
from enum import IntEnum, auto

import display
from crapi.crapi import CRAPI
from spreadsheet.spreadsheet import Sheet


class Status(IntEnum):
    OK = auto()
    FAIL = auto()
    QUIT = auto()


def cmd_init(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    sheet.init()
    return Status.OK


def cmd_quit(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    return Status.QUIT


def show_members(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    display.show_members(cr.get_members())
    return Status.OK


def show_race(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    display.show_race(cr.get_race(), cr.get_clan_tag())
    return Status.OK


def show_racelog(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    if args.count is not None:
        display.show_racelog(cr.get_racelog(args.count), cr.get_clan_tag())
    else:
        display.show_racelog(cr.get_racelog(), cr.get_clan_tag())
    return Status.OK


def update_members(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    sheet.update_members()
    return Status.OK


def update_trophy(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    sheet.update_trophies()
    return Status.OK


def update_racelog(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    sheet.update_racelog()
    return Status.OK


def update_donation(args: argparse.Namespace, cr: CRAPI, sheet: Sheet) -> Status:
    if args.date is not None:
        sheet.update_donations(date=args.date)
    else:
        sheet.update_donations()
    return Status.OK
