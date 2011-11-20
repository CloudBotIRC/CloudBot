from util import hook

def find_location(ip):
    import string
    import urllib
    api = "6ddac03a5a67a534045f59908e5c17fd68169609b453e3c6398823fff86a87c0"
    response = urllib.urlopen("http://api.ipinfodb.com/v3/ip-city/?key="+api+"&ip="+ip).read()
    response = response.split(";")
    give = {}
    give["country"] = response[4].title()
    give["country_short"] = response[3].upper()
    give["state"] = response[5].title()
    give["city"] = response[6].title()
    give["timezone"] = response[10].title()
    return give

def timezone(ip):
    time = find_location(ip)["timezone"]
    time = time.replace(":",".")
    time = time.replace(".00","")
    return int(time)

@hook.command
def location(inp, say = None, me = None):
    ".location <ip> - Performs a GeoIP check on the ip given."
    give = find_location(inp)
    if give["country"] not in [""," ","-"," - "]:
        if give["state"] == give["city"]:
           localstring = give["city"]
        else:
            localstring = give["city"] + ", " + give["state"]
        say("That IP comes from " + give["country"] + " (" + give["country_short"] + ")")
        say("I think it's in " + localstring + " with a timezone of " + give["timezone"] + "GMT")
    else:
        say("Either that wasn't an IP or I cannot locate it in my database. :(")
    return
