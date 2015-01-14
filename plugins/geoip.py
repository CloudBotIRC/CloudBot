import socket
import time
import requests
import asyncio
import shutil
import os.path
import geoip2.database
import geoip2.errors

from cloudbot import hook

DB_URL = "http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz"
PATH = "./data/GeoLite2-City.mmdb"

geoip_reader = None


def fetch_db():
    r = requests.get(DB_URL, stream=True)
    if r.status_code == 200:
        with open(PATH, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


def update_db():
    global geoip_reader
    if os.path.isfile(PATH):
        # check if file is over 2 weeks old
        if time.time() - os.path.getmtime(PATH) > (14 * 24 * 60 * 60):
            geoip_reader = None
            fetch_db()
            geoip_reader = geoip2.database.Reader(PATH)
        else:
            if not geoip_reader:
                geoip_reader = geoip2.database.Reader(PATH)
    else:
        geoip_reader = None
        fetch_db()
        geoip_reader = geoip2.database.Reader(PATH)


@asyncio.coroutine
@hook.onload
def load_geoip(loop):
    loop.run_in_executor(None, update_db)


@hook.command
def geoip(text, reply):
    if not geoip_reader:
        return "GeoIP database is updating, please wait a minute"

    try:
        ip = socket.gethostbyname(text)
    except socket.gaierror:
        return "Invalid input."

    try:
        location_data = geoip_reader.city(ip)
    except geoip2.errors.AddressNotFoundError:
        return "Sorry, I can't locate that in my database."

    data = {
        "cc": location_data.country.iso_code or "N/A",
        "country": location_data.country.name or "Unknown",
        "city": location_data.city.name or "Unknown",
        "region": ", " + location_data.subdivisions.most_specific.name or ""
    }

    reply("\x02Country:\x02 {country} ({cc}), \x02City:\x02 {city}{region}".format(**data))

    # check the DB
    update_db()
