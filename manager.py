# -*- coding: utf-8 -*-

from enum import IntEnum, auto

import crapi
import spreadsheet


# Status code of command_handler
class Status(IntEnum):
	OK = auto()
	FAIL = auto()
	QUIT = auto()

# Help message of commands
cmd_help = (
	"Commands\n"
	"    init          Initialize (setup) the sheet\n"
	"    update        Update content of sheet\n"
	"    show          Show information of clan\n"
	"    quit          Quit\n")

def command_handler(cmd):
	if len(cmd) == 0:
		print(cmd_help)
		return Status.FAIL

	tok = cmd.pop(0)
	if tok == "init":
		sheet.init()
		return Status.OK
	elif tok == "update":
		update_handler(cmd)
		return Status.OK
	elif tok == "show":
		show_handler(cmd)
		return Status.OK
	elif tok == "quit":
		return Status.QUIT
	elif tok == "test":
		return Status.OK
	else:
		print(cmd_help)
		return Status.FAIL

# Help message of command "show"
show_cmd_help = (
	"Show (show)\n"
	"    members               Show all clan members\n"
	"    warlog [count]        Show warlog (specified number)\n")

def show_handler(cmd):
	if len(cmd) == 0:
		print(show_cmd_help)
		return Status.FAIL

	tok = cmd.pop(0)
	if tok == "members":
		crapi.show_members()
		return Status.OK
	elif tok == "warlog":
		if len(cmd) > 0:
			try :
				count = int(cmd.pop(0))
			except Exception as e:
				print(show_cmd_help)
				return Status.FAIL
			crapi.show_warlog(count)
			return Status.OK
		else:
			crapi.show_warlog()
			return Status.OK
	else:
		print(show_cmd_help)
		return Status.FAIL

# Help message of command "update"
update_cmd_help = (
	"Update (update)\n"
	"    members               Update members of clan\n"
	"    trophy                Update trophies of members\n"
	"    warlog                Update warlog\n"
	"    donation [date]       Update donations of members (specified date)\n")

def update_handler(cmd):
	if len(cmd) == 0:
		print(update_cmd_help)
		return Status.FAIL

	tok = cmd.pop(0)
	if tok == "members":
		sheet.update_members()
		return Status.OK
	elif tok == "trophy":
		sheet.update_trophies()
		return Status.OK
	elif tok == "warlog":
		sheet.update_warlog()
		return Status.OK
	elif tok == "donation":
		if len(cmd) > 0:
			date = cmd.pop(0)
			sheet.update_donations(date=date)
			return Status.OK
		else:
			sheet.update_donations()
			return Status.OK
	else:
		print(update_cmd_help)
		return Status.FAIL

if __name__ == "__main__":
	# Open Google Sheet
	sheet = spreadsheet.Sheet()
	# Setup CR API
	crapi = crapi.CRAPI()

	print("CR Clan Statictics Managing System")
	while True:
		print('>> ', end='')
		cmd = input().split()
		ret = command_handler(cmd)
		if ret == Status.QUIT:
			break