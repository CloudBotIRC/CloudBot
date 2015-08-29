import re
from collections import defaultdict
from cloudbot import hook
from cloudbot.util import http

search_pages = defaultdict(list)

def two_lines(bigstring, chan):
    """Receives a string with new lines. Groups the string into a list of strings with up to 3 new lines per string element. Returns first string element then stores the remaining list in search_pages."""
    global search_pages
    temp = bigstring.split('\n')
    for i in range(0, len(temp), 2):
        search_pages[chan].append('\n'.join(temp[i:i+2]))
    search_pages[chan+"index"] = 0
    return search_pages[chan][0]


def smart_truncate(content, length=400, suffix='...\n'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' | ', 1)[0]+ suffix + content[:length].rsplit(' | ', 1)[1] + smart_truncate(content[length:])


@hook.command("morescore", autohelp=False)
def moregrab(text, chan):
    """if a score list has lots of results the results are pagintated. If the most recent search is paginated the pages are stored for retreival. If no argument is given the next page will be returned else a page number can be specified."""
    if not search_pages[chan]:
        return "There are no score pages to show."
    if text:
        index = ""
        try:
            index = int(text)
        except:
            return "Please specify an integer value."
        if abs(int(index)) > len(search_pages[chan]) or index == 0:
            return "please specify a valid page number between 1 and {}.".format(len(search_pages[chan]))
        else:
            return "{}(page {}/{})".format(search_pages[chan][index-1], index, len(search_pages[chan]))
    else:
        search_pages[chan+"index"] += 1
        if search_pages[chan+"index"] < len(search_pages[chan]):
            return "{}(page {}/{})".format(search_pages[chan][search_pages[chan+"index"]], search_pages[chan+"index"] + 1, len(search_pages[chan]))
        else:
            return "All pages have been shown you can specify a page number or do a new search."

@hook.command("nfl", autohelp=False)
def nflScores(chan, text=" "):
    """nfl <team> gets the score or next schedule game for the specified team. If no team specified all games will be included."""
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    response = http.get_html('http://scores.espn.go.com/nfl/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("nfl_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + " | "
    game = smart_truncate(game)
    game = game[:-2]
    game = two_lines(game, chan)
    if len(search_pages[chan]) > 1:
        return "{}(page {}/{}) .morescore".format(game, search_pages[chan+"index"] + 1, len(search_pages[chan]))
    return(game)


@hook.command("mlb", autohelp=False)
def mlbScores(chan, text=" "):
    """mlb <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    response = http.get_html('http://scores.espn.go.com/mlb/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("mlb_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + " | "
    game = smart_truncate(game)
    game = game[:-2]
    game = two_lines(game, chan)
    if len(search_pages[chan]) > 1:
        return "{}(page {}/{}) .morescore".format(game, search_pages[chan+"index"] + 1, len(search_pages[chan]))
    return(game)


@hook.command("nba", autohelp=False)
def nbaScores(chan, text=" "):
    """nba <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    response = http.get_html('http://scores.espn.go.com/nba/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("nba_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + " | "
    game = smart_truncate(game)
    game = game[:-2]
    game = two_lines(game, chan)
    if len(search_pages[chan]) > 1:
        return "{}(page {}/{}) .morescore".format(game, search_pages[chan+"index"] + 1, len(search_pages[chan]))
    return(game)


@hook.command("ncaab", autohelp=False)
def ncaabScores(chan, text=" "):
    """ncaab <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    response = http.get_html('http://scores.espn.go.com/ncb/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("ncb_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + " | "
    game = smart_truncate(game)
    game = game[:-2]
    game = two_lines(game, chan)
    if len(search_pages[chan]) > 1:
        return "{}(page {}/{}) .morescore".format(game, search_pages[chan+"index"] + 1, len(search_pages[chan]))
    return(game)


@hook.command("ncaaf", autohelp=False)
def ncaafScores(chan, text=" "):
    """ncaaf <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    response = http.get_html('http://scores.espn.go.com/ncf/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n') 
    raw=raw.replace('%26','&')
    pattern = re.compile("ncf_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + " | "
    game = smart_truncate(game)
    game = game[:-2]
    game = two_lines(game, chan)
    if len(search_pages[chan]) > 1:
        return "{}(page {}/{}) .morescore".format(game, search_pages[chan+"index"] + 1, len(search_pages[chan]))
    return(game)

@hook.command("nhl", autohelp=False)
def nhlScores(chan, text=" "):
    """nhl <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    response = http.get_html('http://scores.espn.go.com/nhl/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("nhl_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + " | "
    game = smart_truncate(game)
    game = game[:-2]
    game = two_lines(game, chan)
    if len(search_pages[chan]) > 1:
        return "{}(page {}/{}) .morescore".format(game, search_pages[chan+"index"] + 1, len(search_pages[chan]))
    return(game)

@hook.command("wnba", autohelp=False)
def wnbaScores(chan, text=" "):
    """wnba <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    search_pages[chan] = []
    search_pages[chan+"index"] = 0
    response = http.get_html('http://scores.espn.go.com/wnba/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("wnba_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + " | "
    game = smart_truncate(game)
    game = game[:-2]
    game = two_lines(game, chan)
    if len(search_pages[chan]) > 1:
        return "{}(page {}/{}) .morescore".format(game, search_pages[chan+"index"] + 1, len(search_pages[chan]))
    return(game)
