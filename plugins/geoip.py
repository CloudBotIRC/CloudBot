import geoip2.database
import socket
from cloudbot import hook


reader = geoip2.database.Reader('./data/GeoLite2-City.mmdb')

@hook.command
def geoip(text):
    try:
        ip = socket.gethostbyname(text)
    except socket.gaierror:
        return "Invalid input."

    try:
        location_data = reader.city(ip)
    except geoip2.AddressNotFoundError:
        return "Sorry, I can't locate that in my database."

    data = {
        "cc": location_data.country.iso_code or "N/A",
        "country": location_data.country.name or "Unknown",
        "city": location_data.city.name or "Unknown",
        "region": ", " + location_data.subdivisions.most_specific.name or ""
    }

    return "\x02Country:\x02 {country} ({cc}), \x02City:\x02 {city}{region}".format(**data)
