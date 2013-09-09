from util import hook, http, web
import json
from urllib2 import HTTPError


def getSoundInfo(game, search):
    search = search.replace(" ", "+")
    try:
        data = http.get_json("http://p2sounds.blha303.com.au/search/%s/%s" % (game, search))
    except HTTPError as e:
        return "Error: " + json.loads(e.read())["error"]
    items = []
    for i in data:
        items.append("{} - {} {}".format(i["who"],
                                         i["text"] if len(i["text"]) < 325 else i["text"][:325] + "...",
                                         i["listen"] ) )
    if len(items) == 1:
        return items[0]
    else:
        return "{} (and {} others: {})".format(items[0], len(items) - 1, web.haste("\n".join(items)) )


@hook.command
def portal2(inp):
    """portal2 <quote> - Look up Portal 2 quote.
    Example: .portal2 demand to see life's manager"""
    return getSoundInfo("portal2", inp)


@hook.command
def portal2dlc(inp):
    """portal2dlc <quote> - Look up Portal 2 DLC quote.
    Example: .portal2dlc1 these exhibits are interactive"""
    return getSoundInfo("portal2dlc1", inp)


@hook.command("portal2pti")
@hook.command
def portal2dlc2(inp):
    """portal2dlc2 <quote> - Look up Portal 2 Perpetual Testing Inititive quote.
    Example: .portal2 Cave here."""
    return getSoundInfo("portal2dlc2", inp)


@hook.command
def portal2music(inp):
    """portal2music <title> - Look up Portal 2 music.
    Example: .portal2music turret opera"""
    return getSoundInfo("portal2music", inp)


@hook.command('portal1')
@hook.command
def portal(inp):
    """portal <quote> - Look up Portal quote.
    Example: .portal The last thing you want to do is hurt me"""
    return getSoundInfo("portal1", inp)


@hook.command('portal1music')
@hook.command
def portalmusic(inp):
    """portalmusic <title> - Look up Portal music.
    Example: .portalmusic still alive"""
    return getSoundInfo("portal1music", inp)


@hook.command('tf2sound')
@hook.command
def tf2(inp):
    """tf2 [who - ]<quote> - Look up TF2 quote.
    Example: .tf2 may i borrow your earpiece"""
    return getSoundInfo("tf2", inp)


@hook.command
def tf2music(inp):
    """tf2music title - Look up TF2 music lyrics.
    Example: .tf2music rocket jump waltz"""
    return getSoundInfo("tf2music", inp)
