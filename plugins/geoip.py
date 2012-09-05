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

    return "Country: %(country_name)s (%(country_code)s), City: %(city)s" % record
