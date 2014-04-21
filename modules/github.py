import json
import traceback
import urllib

from util import hook, http


shortcuts = {"cloudbot": "ClouDev/CloudBot"}

# (number, state, user.login, title, truncate(body), gitio.gitio(data.url))
format_with_summary = "Issue: #{} ({}) by {}: {} | {} {}"

# (number, state, user.login, title, gitio.gitio(data.url))
format_without_summary = "Issue: #{} ({}) by {}: {} {}"


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


def shorten_gitio(url, code=None):
    # Make sure the url starts with https://
    if not url.startswith("https://"):
        if url.startswith("http://"):
            url = "https://" + url
        else:
            url = "https://" + url

    data = 'url=' + url
    if code:
        data += '&code=' + code
        print(code)
    req = urllib.request.Request(url='http://git.io', data=data.encode())

    # try getting url, let http error raise to next level
    response = urllib.request.urlopen(req)

    # return location
    return response.headers["Location"]


def try_shorten_gitio(url, code=None):
    try:
        return shorten_gitio(url, code)
    except urllib.error.HTTPError:
        return url


@hook.command
def ghissues(text):
    """ghissues username/repo [number] - Get specified issue summary, or open issue count """
    args = text.split()
    if args[0] in shortcuts:
        repo = shortcuts[args[0]]
    else:
        repo = args[0]
    url = "https://api.github.com/repos/{}/issues".format(repo)

    specific_issue = len(args) > 1
    if specific_issue:
        url += "/{}".format(args[1])
    print("Fetching {}".format(url))
    try:
        raw_data = http.get(url)
    except urllib.error.HTTPError:
        if specific_issue:
            return "Error getting issues for '{}/{}', is it a valid issue?".format(args[0], args[1])
        else:
            return "Error getting issues for '{}', is it a valid repository?".format(args[0])

    issue_list = json.loads(raw_data)

    if not specific_issue:
        if len(issue_list) < 1:
            return "Repository has no open issues"
        issue = issue_list[0]
    else:
        issue = issue_list  # only had one issue

    issue_number = issue["number"]
    if issue["state"] == "open":
        state = "\x033\x02OPEN\x02\x0f"
    else:
        state = "\x034\x02CLOSED\x02\x0f by {}".format(issue["closed_by"]["login"])
    user = issue["user"]["login"]
    title = issue["title"]
    summary = truncate(issue["body"])

    try:
        shorturl = try_shorten_gitio(issue["html_url"])
    except urllib.error.HTTPError:
        shorturl = try_shorten_gitio(issue["html_url"] + " " + repo.split("/")[1] + issue_number)

    if summary:
        return format_with_summary.format(issue_number, state, user, title, summary, shorturl)
    else:
        return format_without_summary.format(issue_number, state, user, title, shorturl)


@hook.command
def gitio(text):
    """gitio <url> [code] -- Shorten Github URLs with git.io. [code] is an optional custom short code."""
    split = text.split()
    url = split[0]

    if len(split) > 1:
        code = split[1]
    else:
        code = None

    try:
        return shorten_gitio(url, code=code)
    except urllib.error.HTTPError:
        traceback.print_exc()
        return "Failed to shorten!"
