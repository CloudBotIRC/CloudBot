from cloudbot import hook
from cloudbot.util import database, colors, web

import datetime
import MySQLdb

lat = 0.0
lon = 0.0
station = ""

## WXDATA
location = ""
observation_time = ""
weather = ""
temp_f = ""
relative_humidity = ""
wind_string = ""
pressure_string = ""
dewpoint_string = ""
windchill_string = ""
visibility_mi = ""

def getLatLon(zipcode):
	global lat
	global lon

	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='zip')
	cursor = cnx.cursor()

	query = ("SELECT latitude, longitude FROM zipcodes WHERE zip=%(zipcode)s;");

	cursor.execute(query, {"zipcode": zipcode})

	for (latitude, longitude) in cursor:
		lat = latitude
		lon = longitude

	cursor.close()
	cnx.close()

def getStation(lat, lon):
	global station

	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='wxdata')
	cursor = cnx.cursor()

	query = ("SELECT x.station_id FROM (SELECT station_id, TRUNCATE(((ACOS(SIN(%(lat)s * PI() / 180) * SIN(`latitude` * PI() / 180) + COS(%(lat)s * PI() / 180) * COS(`latitude` * PI() / 180) * COS((%(lon)s - `longitude`) * PI() / 180)) * 180 / PI()) * 60 * 1.1515), 1) AS `distance` FROM `nws` WHERE (`latitude` BETWEEN (%(lat)s - 1) AND (%(lat)s + 1) AND `longitude` BETWEEN (%(lon)s - 1) AND (%(lon)s + 1) AND `station_id` REGEXP '^[A-Z]+$') ORDER BY `distance` ASC LIMIT 1)x")

	cursor.execute(query, {"lat": lat, "lon": lon})

	for (station_id) in cursor:
		station = station_id[0]
	
	cursor.close()
	cnx.close()

def getWX(station):
	global location
	global observation_time
	global weather
	global temp_f
	global relative_humidity
	global wind_string
	global pressure_string
	global dewpoint_string
	global windchill_string
	global visibility_mi

	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='wxdata')
	cursor = cnx.cursor()

	query = ("SELECT location, observation_time, weather, temp_f, relative_humidity, wind_string, pressure_string, dewpoint_string, windchill_string, visibility_mi FROM nws WHERE station_id = %(station)s;")

	cursor.execute(query, {"station": station})
	data = cursor.fetchone()

	location = data[0]
	observation_time = data[1]
	weather = data[2]
	temp_f = data[3]
	relative_humidity = data[4]
	wind_string = data[5]
	pressure_string = data[6]
	dewpoint_string = data[7]
	windchill_string = data[8]
	visibility_mi = data[9]

@hook.command()
def wx(text, notice):
    """<wx> <zipcode> - shows the weather for <zipcode>"""
    global lat
    global lon
    global station
    global location
    global observation_time
    global weather
    global temp_f
    global relative_humidity
    global wind_string
    global pressure_string
    global dewpoint_string
    global windchill_string
    global visibility_mi

    text = text.strip().lower()
    getLatLon(text)
    getStation(lat, lon)
    getWX(station)
    return "{}, {}: {} {}°F, Humidity {}%, Winds {}, Atmospheric Pressure {}, Dewpoint {}, Windchill {}, Visibility {} miles".format(location, observation_time, weather, temp_f, relative_humidity, wind_string, pressure_string, dewpoint_string, windchill_string, visibility_mi)

