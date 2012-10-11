from util import hook
import os.path
import pygeoip
import json

# initalise geolocation database
geo = pygeoip.GeoIP(os.path.abspath("./plugins/data/geoip.dat"))


# load region database
with open("./plugins/data/geoip_regions.json", "rb") as f:
    regions = json.loads(f.read())


@hook.command
def geoip(inp):
    "geoip <host/ip> -- Gets the location of <host/ip>"
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
