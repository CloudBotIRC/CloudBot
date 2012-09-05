from util import hook
import os.path
import csv
import pygeoip

# initalise geolocation database
geo = pygeoip.GeoIP(os.path.abspath("./plugins/data/geoip.dat"))


regions = {}
# read region database
with open("./plugins/data/geoip_regions.csv", "rb") as f:
    reader = csv.reader(f)
    for row in reader:
        country, region, region_name = row
        if not regions.has_key(country):
            regions[country] = {}
        regions[country][region] = region_name


@hook.command
def geoip(inp):
    "geoip <host/ip> -- Gets the location of <host/ip>"
    try:
        record = geo.record_by_name(inp)
    except:
        return "Sorry, I can't locate that in my database."

    print record
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
    return "\x02Country:\x02 %(country)s (%(cc)s), \x02City:\x02 %(city)s%(region)s" % data
