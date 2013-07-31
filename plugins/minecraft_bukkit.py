from util import hook, http, web
import time
import json
from urllib2 import HTTPError
import random
from os import path


@hook.command('randomplugin')
@hook.command(autohelp=False)
def randombukkitplugin(inp, reply=None):
    if not path.exists("plugins/data/bukgetplugins"):
        with open("plugins/data/bukgetplugins", "w") as f:
            f.write(http.get("http://api.bukget.org/3/plugins/bukkit"))
    jsahn = json.loads(open("plugins/data/bukgetplugins", "r").read())
    pickslug = random.choice(jsahn)['slug']
    data = getplugininfo(pickslug)
    name = data['plugin_name']
    description = data['description']
    url = data['website']
    authors = data['authors'][0]
    authors = authors[0] + u"\u200b" + authors[1:]
    stage = data['stage']
    lastUpdate = time.strftime('%d %B %Y %H:%M',
                               time.gmtime(data['versions'][0]['date']))
    lastVersion = data['versions'][0]['version']
    bukkitver = ", ".join(data['versions'][0]['game_versions'])
    link = web.isgd(data['versions'][0]['link'])
    if description != "":
        reply("\x02%s\x02, by \x02%s\x02 - %s - (%s) \x02%s"
              % (name, authors, description, stage, url))
    else:
        reply("\x02%s\x02, by \x02%s\x02 (%s) \x02%s"
              % (name, authors, stage, url))
    reply("Last release: \x02v%s\x02 for \x02%s\x02 at %s \x02%s\x02"
          % (lastVersion, bukkitver, lastUpdate, link))


@hook.command('bplugin')
@hook.command('plugin')
@hook.command
def bukkitplugin(inp, reply=None):
    """plugin <bukkit plugin slug> - Look up a plugin on dev.bukkit.org"""
    data = getplugininfo(inp.lower())
    try:
        name = data['plugin_name']
    except ValueError:
        return data
    description = data['description']
    url = data['website']
    authors = data['authors'][0]
    authors = authors[0] + u"\u200b" + authors[1:]
    stage = data['stage']
    lastUpdate = time.strftime('%d %B %Y %H:%M',
                               time.gmtime(data['versions'][0]['date']))
    lastVersion = data['versions'][0]['version']
    bukkitver = ", ".join(data['versions'][0]['game_versions'])
    link = web.isgd(data['versions'][0]['link'])
    if description != "":
        reply("\x02%s\x02, by \x02%s\x02 - %s - (%s) \x02%s"
              % (name, authors, description, stage, url))
    else:
        reply("\x02%s\x02, by \x02%s\x02 (%s) \x02%s"
              % (name, authors, stage, url))
    reply("Last release: \x02v%s\x02 for \x02%s\x02 at %s \x02%s\x02"
          % (lastVersion, bukkitver, lastUpdate, link))


def getplugininfo(inp):
    if len(inp.split(" ")) > 1:
        slug = inp.split(" ")[0]
    else:
        slug = inp
    try:
        data = http.get_json("http://api.bukget.org/3/plugins/bukkit/%s/"
                             % slug)
    except HTTPError as e:
        return "Got error: %s" % e
    return data
