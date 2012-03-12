# plugin created by neersighted and lukeroge
from util import hook
import urllib2


@hook.command
def gitio(inp):
    ".gitio <url> [code] -- Shorten Github URLs with git.io.  [code] is a optional custom short code."
    split = inp.split(" ")
    url = split[0]

    try:
        code = split[1]
    except:
        code = None

    # if the first 8 chars of "url" are not "https://" then append
    # "https://" to the url, also convert "http://" to "https://"
    if url[:8] != "https://":
        if url[:7] != "http://":
            url = "https://" + url
        else:
            url = "https://" + url[7:]
    url = 'url=' + str(url)
    if code:
        url = url + '&code=' + str(code)
    req = urllib2.Request(url='http://git.io', data=url)

    # try getting url, catch http error
    try:
        f = urllib2.urlopen(req)
    except urllib2.HTTPError:
        return "Failed to get URL!"
    urlinfo = str(f.info())

    # loop over the rows in urlinfo and pick out location and
    # status (this is pretty odd code, but urllib2.Request is weird)
    for row in urlinfo.split("\n"):
        if row.find("Status") != -1:
            status = row
        if row.find("Location") != -1:
            location = row

    print status
    if not "201" in status:
        return "Failed to get URL!"

    # this wont work for some reason, so lets ignore it ^

    # return location, minus the first 10 chars
    return location[10:]
