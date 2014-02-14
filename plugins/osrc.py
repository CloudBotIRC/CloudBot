from bs4 import BeautifulSoup

from util import hook, http, web


api_url = "http://osrc.dfm.io/{}/stats"
user_url = "http://osrc.dfm.io/{}"


@hook.command
def osrc(inp):
    """osrc <github user> -- Gets an Open Source Report Card for <github user>"""

    user_nick = inp.strip()
    url = api_url.format(user_nick)

    try:
        response = http.get_json(url)
    except (http.HTTPError, http.URLError):
        return "Couldn't find any stats for this user."

    response["nick"] = user_nick
    soup = BeautifulSoup(response["summary"])
    response["work_time"] = soup.find("a", {"href": "#day"}).contents[0]

    response["short_url"] = web.try_isgd(user_url.format(user_nick))

    return "{nick} is a {lang_user}. {nick} is a {hacker_type} " \
           "who seems to {work_time} - {short_url}".format(**response)
