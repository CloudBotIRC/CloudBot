from cloudbot import hook, web, textutils

import requests

shortcuts = {
    'cloudbot': 'CloudBotIRC/Refresh'
}

@hook.command
def issues(text):
    """issues <repo> [issue] - Get issues for <repo>. If [issue] is specified, summarize that issue."""
    args = text.split()
    repo = args[0] if args[0] not in shortcuts else shortcuts[args[0]]
    issue = args[1] if len(args) > 1 else None   

    if issue:
        r = requests.get("https://api.github.com/repos/{}/issues/{}".format(repo, issue))
        j = r.json()
        
        gitio = web.Gitio()

        url          = gitio.shorten(j["html_url"])
        number       = j["number"]
        user         = j["user"]["login"]
        title        = j["title"]
        summary      = textutils.truncate(j["body"])
        if j["state"] is "open":
            state    = "\x033\x02OPEN\x02\x0f"
        else:
            state    = "\x034\x02CLOSED\x02\x0f by {}".format(j["closed_by"]["login"])

        return "Issue: #{} ({}) by {}: {} | {} {}".format(number, state, user, title, summary, url)
    else:
        r = requests.get("https://api.github.com/repos/{}/issues".format(repo))
        j = r.json()
        
        count = len(j)
        if count is 0:
            return "Repository has no open issues."
        else:
            return "Repository has {} open issues.".format(count)

