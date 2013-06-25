from util import hook, http
import json
import gitio

shortcuts = {"cloudbot": "ClouDev/CloudBot"}

def truncate(msg):
    nmsg = msg.split(" ")
    out = None
    x = 0
    for i in nmsg:
      if x <= 7:
        if out:
          out = out + " " + nmsg[x]
        else:
          out = nmsg[x]
      x = x + 1
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
      url = "https://api.github.com/repos/%s/issues" % repo
    except IndexError:
      return "Invalid syntax. .github issues username/repo [number]"
    try:
      url = url + "/%s" % args[1]
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
    fmt = "Issue: #%s (%s) by %s: %s | %s %s" # (number, state, user.login, title, truncate(body), gitio.gitio(data.url))
    fmt1 = "Issue: #%s (%s) by %s: %s %s" # (number, state, user.login, title, gitio.gitio(data.url))
    number = data["number"]
    if data["state"] == "open":
      state = u"\x033\x02OPEN\x02\x0f"
      closedby = None
    else:
      state = u"\x034\x02CLOSED\x02\x0f by %s" % data["closed_by"]["login"]
    user = data["user"]["login"]
    title = data["title"]
    summary = truncate(data["body"])
    gitiourl = gitio.gitio(data["html_url"])
    if summary == "":
      return fmt1 % (number, state, user, title, gitiourl)
    else:
      return fmt % (number, state, user, title, summary, gitiourl)
