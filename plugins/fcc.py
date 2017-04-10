from cloudbot import hook
from cloudbot.util import database, colors, web

import datetime
import MySQLdb

station_info = {}

def getStation(callsign):
	global station_info
	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='fcc')
	cursor = cnx.cursor()

	query = ("SELECT `ham_EN`.`Call Sign`, `ham_EN`.`Entity Name`, `ham_EN`.`Street Address`, `ham_EN`.City, `ham_EN`.State, `ham_EN`.`Zip Code`, `ham_EN`.FRN, `ham_HD`.`License Status`, `ham_HD`.`Radio Service Code`, `ham_HD`.`Grant Date`, `ham_HD`.`Expired Date`, `ham_HD`.`Cancellation Date`, `ham_HD`.`Effective Date`, `ham_AM`.`Operator Class` FROM ham_EN LEFT JOIN ham_HD ON ham_EN.`Unique System Identifier`=ham_HD.`Unique System Identifier` LEFT JOIN ham_AM ON ham_EN.`Unique System Identifier`=ham_AM.`Unique System Identifier` WHERE `ham_EN`.`Call Sign` = %(callsign)s")

	cursor.execute(query, {"callsign": callsign })

	station = cursor.fetchone()
	
	print(station)
	station_info['callsign'] = station[0]
	station_info['Entity Name'] = station[1]
	station_info['Street Address'] = station[2]
	station_info['City'] = station[3]
	station_info['State'] = station[4]
	station_info['Zip'] = station[5]
	station_info['FRN'] = station[6]
	station_info['License Status'] = station[7]
	station_info['Radio Service Code'] = station[8]
	station_info['Grant Date'] = station[9]
	station_info['Expired Date'] = station[10]
	station_info['Cancellation Date'] = station[11]
	station_info['Effective Date'] = station[12]
	station_info['Operator Class'] = station[13]
	
	cursor.close()
	cnx.close()

def getFCCStats(state):
	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='fcc')
	cursor = cnx.cursor()

	query = ("SELECT count(`ham_EN`.`Call Sign`) FROM ham_EN LEFT JOIN ham_HD ON ham_EN.`Unique System Identifier`=ham_HD.`Unique System Identifier` WHERE `ham_EN`.`State` = %(state)s AND `ham_HD`.`License Status` = 'A'")
	cursor.execute(query, {"state": state})
	result = cursor.fetchone()
	print(result)
	return(result[0])

def getFCCStatsZip(zipcode):
	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='fcc')
	cursor = cnx.cursor()

	query = ("SELECT count(`ham_EN`.`Call Sign`) FROM ham_EN LEFT JOIN ham_HD ON ham_EN.`Unique System Identifier`=ham_HD.`Unique System Identifier` WHERE `ham_EN`.`Zip Code` = %(zip)s AND `ham_HD`.`License Status` = 'A'")
	cursor.execute(query, {"zip": zipcode})
	result = cursor.fetchone()
	print(result)
	return(result[0])

@hook.command()
def hamzip(text, notice):
	"""<hamzip> <zip> - shows number of licensed amateur radio operators in <zip>"""
	text = text.strip().lower()
	licensestat = getFCCStatsZip(text)
	return "\x02{}\x02: {} licensed HAMs".format(text, licensestat)

@hook.command()
def hamstat(text, notice):
	"""<hamstat> <state> - shows number of licensed amateur radio operators in <state>"""
	text = text.strip().lower()
	licensestat = getFCCStats(text)
	return "\x02{}\x02: {} licensed HAMs".format(text, licensestat)

@hook.command()
def fcc(text, notice):
    """<fcc> <callsign> - shows info for <callsign>"""
    global station_info
    text = text.strip().lower()
    getStation(text)
    return "\x02Callsign\x02: {} | \x02Name\x02: {} | \x02License Class\x02: {} | \x02Address\x02: {} {}, {} {} | \x02License Status\x02: {} | \x02Radio Service Code\x02: {} | \x02Grant Date\x02: {} | \x02Expiration Date\x02: {}".format(station_info['callsign'], station_info['Entity Name'], station_info['Operator Class'], station_info['Street Address'], station_info['City'], station_info['State'], station_info['Zip'], station_info['License Status'], station_info['Radio Service Code'], station_info['Grant Date'], station_info['Expired Date'])

