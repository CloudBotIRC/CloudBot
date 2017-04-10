from cloudbot import hook
from cloudbot.util import database, colors, web
from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import MySQLdb
import re

station_info = {}

def getStatusCode(statuscode):
	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='utilities')
	cursor = cnx.cursor()

	query = ("SELECT code, name, description FROM sip_status_codes WHERE code = %(statuscode)s")
	cursor.execute(query, {"statuscode": statuscode})
	result = cursor.fetchone()
	return(result)

def getMethod(method):
	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='utilities')
	cursor = cnx.cursor()

	query = ("SELECT name, description FROM sip_methods WHERE name = %(method)s")
	cursor.execute(query, {"method": method})
	result = cursor.fetchone()
	return(result)

@hook.command()
def sip(text, notice):
    """<sip> <status code> - Gets the name and description of a SIP status code."""
    text = text.strip().lower()
    if (re.search('[a-z]', text)):
	    result = getMethod(text)
	    return "{}: {}".format(result[0], result[1])
    else:
	    result = getStatusCode(text)
	    return "{} {}: {}".format(result[0], result[1], result[2])

