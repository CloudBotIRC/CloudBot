from util import hook
import os.path
import pygeoip

# initalise geolocation database
geo = pygeoip.GeoIP(os.path.abspath("./plugins/data/geoip.dat"))


@hook.command
def geoip(inp):
    "geoip <host/ip> -- Gets the location of <host/ip>"
    try:
        record = geo.record_by_name(inp)
    except:
        return "Sorry, I can't locate that in my database."

    record["_cc"] = record["country_code"] or "N/A"
    record["_country"] = record["country_name"] or "Unknown"
    record["_city"] = record["metro_code"] or record["city"] or "Unknown"
    return "Country: %(_country)s (%(_cc)s), City: %(_city)s" % record
