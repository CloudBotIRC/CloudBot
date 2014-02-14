import json
import urllib2

from util import hook, http


shortcuts = {"cloudbot": "ClouDev/CloudBot"}


def truncate(msg):
    nmsg = msg.split()
    out = None
    x = 0
    for i in nmsg:
        if x <= 7:
            if out:
                out = out + " " + nmsg[x]
            else:
                out = nmsg[x]
        x += 1
    if x <= 7:
        return out
    else:
        return out + "..."


@hook.command
def ghissues(inp):
    """ghissues username/repo [number] - Get specified issue summary, or open issue count """
    args = inp.split(" ")
    try:
        if args[0] in shortcuts:
            repo = shortcuts[args[0]]
        else:
            repo = args[0]
        url = "https://api.github.com/repos/{}/issues".format(repo)
    except IndexError:
        return "Invalid syntax. .github issues username/repo [number]"
    try:
        url += "/%s" % args[1]
        number = True
    except IndexError:
        number = False
    try:
        data = json.loads(http.open(url).read())
        print url
        if not number:
            try:
                data = data[0]
            except IndexError:
                print data
                return "Repo has no open issues"
    except ValueError:
        return "Invalid data returned. Check arguments (.github issues username/repo [number]"
    fmt = "Issue: #%s (%s) by %s: %s | %s %s"  # (number, state, user.login, title, truncate(body), gitio.gitio(data.url))
    fmt1 = "Issue: #%s (%s) by %s: %s %s"  # (number, state, user.login, title, gitio.gitio(data.url))
    number = data["number"]
    if data["state"] == "open":
        state = u"\x033\x02OPEN\x02\x0f"
    else:
        state = u"\x034\x02CLOSED\x02\x0f by {}".format(data["closed_by"]["login"])
    user = data["user"]["login"]
    title = data["title"]
    summary = truncate(data["body"])
    gitiourl = gitio(data["html_url"])
    if "Failed to get URL" in gitiourl:
        gitiourl = gitio(data["html_url"] + " " + repo.split("/")[1] + number)
    if summary == "":
        return fmt1 % (number, state, user, title, gitiourl)
    else:
        return fmt % (number, state, user, title, summary, gitiourl)


@hook.command
def gitio(inp):
    """gitio <url> [code] -- Shorten Github URLs with git.io.  [code] is
    a optional custom short code."""
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
