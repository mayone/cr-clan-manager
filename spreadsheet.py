# -*- coding: utf-8 -*-

import pprint
import datetime
from tqdm import tqdm

import pygsheets

import crapi
import utils

from enum import IntEnum, auto

pp = pprint.PrettyPrinter()

class Color():
	# In tuple (red, green, blue, alpha)
	white = (0, 0, 0, 0)
	red = (1, 0, 0, 0)
	skin = (1, 0.8980392, 0.6, 0)
	pink = (0.95686275, 0.8, 0.8, 0)

class RecordGenre(IntEnum):
	UNKNOWN = auto()
	WAR = auto()
	DONATE = auto()

class Sheet():
	def __init__(self, index=0):
		self.__sheet = self.__open_sheet(index)
		self.__crapi = crapi.CRAPI()

	def __open_sheet(self, index):
		"""Open worksheet.

		Parameters
		----------
		index : int
		    Index of worksheet in spreadsheet (starts from 0).
		"""
		client = pygsheets.authorize(service_file='client_secret.json')

		# Open a worksheet from spreadsheet
		spreadsheet = client.open('[皇室戰爭] 部落統計')
		sheet = spreadsheet.worksheet(value=index)

		return sheet

	def __get_tag_cells(self):
		sheet = self.__sheet
		start = sheet.find('標籤')[0].neighbour('bottom')
		end = start
		while end.neighbour('bottom').value != '':
			end = end.neighbour('bottom')

		tag_cells = [list[0] for list in sheet.range(start.label + ':' + end.label, returnas='cells')]

		return tag_cells

	def __sort_by_trophies(self):
		sheet = self.__sheet

		print("Sorting by trophies...")
		# basecolumnindex starts from 0
		sheet.sort_range(
			start=(2, 1),
			end=(51, sheet.cols),
			basecolumnindex=sheet.find('最高盃數')[0].col - 1,
			sortorder='DESCENDING')

		print("Sorted by trophies")

	def update_trophies(self):
		sheet = self.__sheet
		tag_cells = self.__get_tag_cells()
		members = self.__crapi.get_members()
		updated = False

		print("Updating trophies...")

		for tag_cell in tag_cells:
			tag = tag_cell.value
			try:
				member = members[tag]
			except Exception as e:
				print("Warning: player tag " + tag + " do not exists")
				continue
			trophy_cell = tag_cell.neighbour('right')
			if trophy_cell.value < str(member['bestTrophies']):
				print("Update player {0} trophies: {1} -> {2}".format(
						align(member['name'], 32),
						trophy_cell.value, member['bestTrophies']))
				trophy_cell.value = str(member['bestTrophies'])
				updated = True

		if updated:
			self.__sort_by_trophies()
			print("Trophies updated")
		else:
			print("Trophies are already up to date")

	def update_warlog(self):
		sheet = self.__sheet
		header_cells = sheet.get_row(1, returnas='cells')

		# Set index to latest updated in sheet
		for header_cell in reversed(header_cells):
			if header_cell.note != None:
				try:
					latest_updated_date = header_cell.note.split()[1]
					latest_updated_col_offset = sheet.cols - header_cell.col
					break
				except Exception as e:
					continue

		warlog = self.__crapi.get_warlog()
		warlog_unrecorded_offset = -1

		# Set index to the unrecorded war in warlog
		for i in range(len(warlog)):		
			war = warlog[i]
			date = war['createdDate'].split('T')[0]
			if date > latest_updated_date:
				warlog_unrecorded_offset = i
			else:
				break

		for i in range(warlog_unrecorded_offset, -1, -1):
			war = warlog[i]
			# Keep the last column empty
			if latest_updated_col_offset <= 1:
				# insert and inherit from the last column
				sheet.insert_cols(sheet.cols - 1, number=1, values=None, inherit=False)
				latest_updated_col_offset += 1
			self.__update_war(latest_updated_col_offset - 1, war)
			latest_updated_col_offset -= 1

		return True

	def __update_war(self, col_offset, war):
		"""Update specified war records to the target column.

		Parameters
		----------
		col_offset : int
		    Offset of the target column from the last column.
		war: Object
		    The war from the warlog to be recorded
		"""
		sheet = self.__sheet
		col_index = sheet.cols - col_offset
		tag_cells = self.__get_tag_cells()

		# Get info from warlog
		date = war['createdDate'].split('T')[0]
		participants = war['participants']
		standings = war['standings']
		for standing in standings:
			if standing['clan']['tag'] == crapi.clan_tag:
				trophy_change = standing['trophyChange']
				break

		print("Updating war " + date)

		header_cell = sheet.cell((1, col_index))
		header_cell.value = "部落戰 " + str(trophy_change)
		header_cell.note = "發起日 " + date
		header_cell.color = Color.pink

		# Fill war records into sheet
		for p in tqdm(participants):
			tag = p['tag']
			row_index = 0
			for tag_cell in tag_cells:
				if tag == tag_cell.value:
					row_index = tag_cell.row
					break
			if row_index:
				cell = sheet.cell((row_index, col_index))
			else:
				print("Warning: player tag " + tag + " do not exists")
				continue

			warday_played = p['battlesPlayed']
			wins = p['wins']
			loses = warday_played - wins

			# Form record and fill in
			record = ""
			record += str(p['cardsEarned'])
			record += 'L' * loses
			record += 'w' * wins
			if warday_played == 0:
				record += "x"
			cell.value = record

			# Mark with color red if didn't complete all battles
			if warday_played == 0 or p['collectionDayBattlesPlayed'] < 3:
				cell.color = Color.red
				if (p['collectionDayBattlesPlayed'] < 3):
					cell.note = "準備日({0}/3)".format(p['collectionDayBattlesPlayed'])

	def update_donations(self, date=None, delay=None):
		sheet = self.__sheet
		tag_cells = self.__get_tag_cells()
		members = self.__crapi.get_members()

		header_cells = sheet.get_row(1, returnas='cells')

		# Search and set latest updated (genre, date, col_offset)
		latest_updated_genre = RecordGenre.UNKNOWN
		for header_cell in reversed(header_cells):
			if header_cell.note != None:
				try:
					if header_cell.note.split()[0] == "發起日":
						latest_updated_genre = RecordGenre.WAR
					elif header_cell.note.split()[0] == "統計日":
						latest_updated_genre = RecordGenre.DONATE
					latest_updated_date = header_cell.note.split()[1]
					latest_updated_col_offset = sheet.cols - header_cell.col
					break
				except Exception as e:
					continue

		now = datetime.datetime.now()
		if date:
			record_date = datetime.datetime(now.year, int(date.split('/')[0]), int(date.split('/')[1]))
			full_date = record_date.strftime("%Y%m%d")
		else:
			date = now.strftime("%m/%d")
			full_date = now.strftime("%Y%m%d")

		if latest_updated_date == full_date and \
			latest_updated_genre == RecordGenre.DONATE:
			# Update the existed record
			col_index = sheet.cols - latest_updated_col_offset
		else:
			# Keep the last column empty
			if latest_updated_col_offset <= 1:
				# insert and inherit from the last column
				sheet.insert_cols(sheet.cols - 1, number=1, values=None, inherit=False)
				latest_updated_col_offset += 1
			# Record in new coulumn
			col_offset = latest_updated_col_offset - 1
			col_index = sheet.cols - col_offset

		header_cell = sheet.cell((1, col_index))
		header_cell.value = "捐贈 " + date
		header_cell.note = "統計日 " + full_date
		header_cell.color = Color.skin

		print("Updating donations " + date)

		# Update donations of each player
		for tag_cell in tqdm(tag_cells):
			tag = tag_cell.value
			try:
				member = members[tag]
			except Exception as e:
				print("Warning: player tag " + tag + " do not exists")
				continue

			row_index = tag_cell.row

			cell = sheet.cell((row_index, col_index))
			cell.value = str(member['donations'])

	def __print_all(self):
		sheet = self.__sheet
		result = sheet.get_all_values(include_tailing_empty_rows=False)
		pp.pprint(result)