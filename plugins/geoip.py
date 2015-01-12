import socket
import geoip2.database
import geoip2.errors

from cloudbot import hook


@hook.onload()
def load_geoip():
    global geoip_reader
    geoip_reader = geoip2.database.Reader('./data/GeoLite2-City.mmdb')


@hook.command
def geoip(text):
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

    return "\x02Country:\x02 {country} ({cc}), \x02City:\x02 {city}{region}".format(**data)
