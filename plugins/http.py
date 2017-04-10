from cloudbot import hook
from cloudbot.util import database, colors, web
from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
import MySQLdb

station_info = {}

def getHttpStatusCode(statuscode):
	cnx = MySQLdb.connect(host='mysql.lan.productionservers.net', user='cloudbot', password='QOLo8egoDo4Ac7MeTIQ8Qot8xAxiDo', database='utilities')
	cursor = cnx.cursor()

	query = ("SELECT code, name, description FROM http_status_codes WHERE code = %(statuscode)s")
	cursor.execute(query, {"statuscode": statuscode})
	result = cursor.fetchone()
	return(result)


@hook.command()
def http(text, notice):
    """<http> <status code> - Gets the name and description of a HTTP status code."""
    text = text.strip().lower()
    result = getHttpStatusCode(text)
    return "{} {}: {}".format(result[0], result[1], result[2])

