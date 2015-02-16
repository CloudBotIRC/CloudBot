import re
from cloudbot import hook
from cloudbot.util import http

@hook.command("nfl", autohelp=False)
def nflScores(text=" "):
    """nfl <team> gets the score or next schedule game for the specified team. If no team specified all games will be included."""
    response = http.get_html('http://scores.espn.go.com/nfl/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("nfl_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + "  "
    return(game)


@hook.command("mlb", autohelp=False)
def mlbScores(text=" "):
    """mlb <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    response = http.get_html('http://scores.espn.go.com/mlb/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("mlb_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + "  "
    return(game)


@hook.command("nba", autohelp=False)
def nbaScores(text=" "):
    """nba <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    response = http.get_html('http://scores.espn.go.com/nba/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("nba_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + "  "
    return(game)


@hook.command("ncaab", autohelp=False)
def ncaabScores(text=" "):
    """ncaab <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    response = http.get_html('http://scores.espn.go.com/ncb/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("ncb_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + "  "
    return(game)


@hook.command("ncaaf", autohelp=False)
def ncaafScores(text=" "):
    """ncaaf <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
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
            game = game +  match + "  "
    return(game)

@hook.command("nhl", autohelp=False)
def nhlScores(text=" "):
    """nhl <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    response = http.get_html('http://scores.espn.go.com/nhl/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("nhl_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + "  "
    return(game)

@hook.command("wnba", autohelp=False)
def wnbaScores(text=" "):
    """wnba <team city> gets the score or next scheduled game for the specified team. If no team is specified all games will be included."""
    response = http.get_html('http://scores.espn.go.com/wnba/bottomline/scores', decode=False)
    game = ""
    score = response.text_content()
    raw=score.replace('%20',' ')
    raw=raw.replace('^','')
    raw=raw.replace('&','\n')
    pattern = re.compile("wnba_s_left\d+=(.*)")
    for match in re.findall(pattern, raw):
        if text.lower() in match.lower():
            game = game +  match + "  "
    return(game)
