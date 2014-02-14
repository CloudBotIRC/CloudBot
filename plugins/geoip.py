import os.path
import json
import gzip
from StringIO import StringIO

import pygeoip

from util import hook, http


# load region database
with open("./plugins/data/geoip_regions.json", "rb") as f:
    regions = json.loads(f.read())

if os.path.isfile(os.path.abspath("./plugins/data/GeoLiteCity.dat")):
    # initialise geolocation database
    geo = pygeoip.GeoIP(os.path.abspath("./plugins/data/GeoLiteCity.dat"))
else:
    download = http.get("http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz")
    string_io = StringIO(download)
    geoip_file = gzip.GzipFile(fileobj=string_io, mode='rb')

    output = open(os.path.abspath("./plugins/data/GeoLiteCity.dat"), 'wb')
    output.write(geoip_file.read())
    output.close()

    geo = pygeoip.GeoIP(os.path.abspath("./plugins/data/GeoLiteCity.dat"))


@hook.command
def geoip(inp):
    """geoip <host/ip> -- Gets the location of <host/ip>"""

    try:
        record = geo.record_by_name(inp)
    except:
        return "Sorry, I can't locate that in my database."

    data = {}

    if "region_name" in record:
        # we try catching an exception here because the region DB is missing a few areas
        # it's a lazy patch, but it should do the job
        try:
            data["region"] = ", " + regions[record["country_code"]][record["region_name"]]
        except:
            data["region"] = ""
    else:
        data["region"] = ""

    data["cc"] = record["country_code"] or "N/A"
    data["country"] = record["country_name"] or "Unknown"
    data["city"] = record["city"] or "Unknown"
    return "\x02Country:\x02 {country} ({cc}), \x02City:\x02 {city}{region}".format(**data)
