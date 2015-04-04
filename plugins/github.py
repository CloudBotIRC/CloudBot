import requests

from cloudbot import hook
from cloudbot.util import web, formatting

shortcuts = {
    'cloudbot': 'CloudBotIRC/CloudBot'
}


@hook.command("ghissue", "issue")
def issue(text):
    """<username|repo> [number] - gets issue [number]'s summary, or the open issue count if no issue is specified"""
    args = text.split()
    repo = args[0] if args[0] not in shortcuts else shortcuts[args[0]]
    issue = args[1] if len(args) > 1 else None

    if issue:
        r = requests.get('https://api.github.com/repos/{}/issues/{}'.format(repo, issue))
        j = r.json()

        url = web.try_shorten(j['html_url'], service='git.io')
        number = j['number']
        title = j['title']
        summary = formatting.truncate(j['body'].split('\n')[0], 25)
        if j['state'] == 'open':
            state = '\x033\x02Opened\x02\x0f by {}'.format(j['user']['login'])
        else:
            state = '\x034\x02Closed\x02\x0f by {}'.format(j['closed_by']['login'])

        return 'Issue #{} ({}): {} | {}: {}'.format(number, state, url, title, summary)
    else:
        r = requests.get('https://api.github.com/repos/{}/issues'.format(repo))
        j = r.json()

        count = len(j)
        if count is 0:
            return 'Repository has no open issues.'
        else:
            return 'Repository has {} open issues.'.format(count)

