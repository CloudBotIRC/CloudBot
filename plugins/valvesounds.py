from util import hook, http, web
from urllib import urlencode

portal2url = "http://www.portal2sounds.com/"
portal2dlc1url = portal2url.replace("www", "dlc")
portal2dlc2url = portal2url.replace("www", "dlc2")
portal2musicurl = portal2url.replace("www", "p2music")
portal1url = portal2url.replace("www", "p1")
portal1musicurl = portal2url.replace("www", "p1music")
tf2url = "http://www.tf2sounds.com/"
tf2musicurl = tf2url.replace("www", "music")


def getSoundInfo(url, inp, jsondata=False):
    if "dostream" in inp:
        inp = inp.replace("dostream", "").replace("  ", " ")
        dostream = True
    else:
        dostream = False
    if len(inp.split(" - ")) > 1:
        who = inp.split(" - ")[0]
        quote = inp.split(" - ")[1]
    else:
        who = None
        quote = inp
    data = http.get_json(url + "list.php?" + urlencode({"quote": quote, "who": who}))
    if len(data) > 3:
        newdata = data[3:]
        text = newdata[0]["text"]
        if "music" in url:
            textsplit = text.split('"')
            text = ""
            for i in xrange(len(textsplit)):
                if i % 2 != 0 and i < 6:
                    if text:
                        text += " / " + textsplit[i]
                    else:
                        text = textsplit[i]
        if not jsondata:
            return "%s - %s %s" % (newdata[0]["who"],
                                   text if len(text) < 325 else text[:325] + "...",
                                   web.try_isgd(
                                       url + newdata[0]["id"] if not dostream else url + "sound.php?id=" + newdata[0][
                                           "id"] + "&stream"))
    else:
        if not jsondata:
            return "No results."
    return data


@hook.command
def portal2(inp):
    """portal2 [who - ]<quote> - Look up Portal 2 quote.
    Example: .portal2 cave johnson - demand to see life's manager,
    .portal2 i own the place | If - is not included, no 'who' data will be sent."""
    return getSoundInfo(portal2url, inp)


@hook.command
def portal2dlc(inp):
    """portal2dlc [who - ]<quote> - Look up Portal 2 DLC quote.
    Example: .portal2dlc1 glados - I lie when i'm nervous
    .portal2 these exhibits are interactive
    If - is not included, no 'who' data will be sent."""
    return getSoundInfo(portal2dlc1url, inp)


@hook.command("portal2pti")
@hook.command
def portal2dlc2(inp):
    """portal2dlc2 [who - ]<quote> - Look up Portal 2 Perpetual Testing Inititive quote.
    Example: .portal2 glados - I lie when i'm nervous
    .portal2dlc2 these exhibits are interactive
    If - is not included, no 'who' data will be sent."""
    return getSoundInfo(portal2dlc2url, inp)


@hook.command
def portal2music(inp):
    """portal2music <title> - Look up Portal 2 music.
    Example: .portal2 turret opera
    .portal2music want you gone
    If - is not included, no 'title' data will be sent."""
    return getSoundInfo(portal2musicurl, inp + " - ")


@hook.command('portal1')
@hook.command
def portal(inp):
    """portal [who - ]<quote> - Look up Portal quote.
    Example: .portal glados - the last thing you want to do is hurt me
    .portal this is your fault
    If - is not included, no 'who' data will be sent."""
    return getSoundInfo(portal1url, inp)


@hook.command('portal1music')
@hook.command
def portalmusic(inp):
    """portalmusic <title> - Look up Portal music.
    Example: .portalmusic still alive
    If - is not included, no 'title' data will be sent."""
    return getSoundInfo(portal1musicurl, inp + " - ")


@hook.command('tf2sound')
@hook.command
def tf2(inp):
    """tf2 [who - ]<quote> - Look up TF2 quote.
    Example: .tf2 spy - may i borrow your earpiece
    .tf2 nom nom nom
    If - is not included, no 'who' data will be sent."""
    return getSoundInfo(tf2url, inp)


@hook.command
def tf2music(inp):
    """tf2music title - Look up TF2 music lyrics.
    Example: .tf2music rocket jump waltz
    If - is not included, no 'title' data will be sent."""
    return getSoundInfo(tf2musicurl, inp + " - ")
