from util import hook


def db_init(db):
    db.execute("create table if not exists botmodes(modename, nick, user, host, authed, admin, channel, chanmodes, usermodes)")
    db.commit()


class Checker(object):
    def __init__(self, bot, user, channel):

        self._bot = bot

        self._user = user
        self._channel = channel

    def check(self, mode, db, bot=None, user=None, channel=None):
        db_init(db)
        bot = bot or self._bot
        user = user or self._user
        channel = channel or self._channel
        checks = [mode]
        if user:
            checks.append(user.nick)
            checks.append(user.user)
            checks.append(user.host)
            checks.append(user.authed or "")
            checks.append(str(user.nick in bot.config["admins"]))
        else:
            checks.extend([""] * 4)
            checks.append(str(False))

        if channel:
            checks.append(channel.name)
            checks.append("".join(channel.modes.keys()))
        else:
            checks.extend([""] * 2)

        if channel and user and user in channel.usermodes:
            checks.append("".join(channel.usermodes[user]))
        else:
            checks.append("")

        return bool(query(db, checks).fetchone())


def query(db, checks):
    return db.execute("select * from botmodes where "
                      "? glob modename and "
                      "lower(?) glob lower(nick) and "
                      "lower(?) glob lower(user) and "
                      "lower(?) glob lower(host) and "
                      "lower(?) glob lower(authed) and "
                      "? glob admin and "
                      "lower(?) glob lower(channel) and "
                      "? glob chanmodes and "
                      "? glob usermodes order by modename", checks)


def posquery(db, checks):
    return db.execute("select * from botmodes where "
                      "modename glob ? and "
                      "lower(nick) glob lower(?) and "
                      "lower(user) glob lower(?) and "
                      "lower(host) glob ? and "
                      "authed glob ? and "
                      "admin glob ? and "
                      "lower(channel) glob lower(?) and "
                      "chanmodes glob ? and "
                      "usermodes glob ? order by modename", checks)


#called from usertracking, not as it's own sieve
def valueadd(bot, input, func, kind, args):
    channel = None
    if input.chan in input.users.channels:
        channel = input.users.channels[input.chan]
    user = None
    if input.nick in input.users.users:
        user = input.users.users[input.nick]
    input["modes"] = Checker(bot, user, channel)


@hook.command
def mode(inp, input=None, db=None):
    ".mode -- Set modes on various things"
    if input.nick not in input.bot.config["admins"]:
        input.notice("Only bot admins can use this command!")
        return
    db_init(db)
    split = inp.split(" ")
    print repr(split)
    if split[0] in ["set", "delete"]:
        names = dict(mode=None, nick="*", user="*", host="*", authed="*", admin="*", channel="*", chanmodes="*", usermodes="*")
    elif split[0] == "search":
        names = dict(mode="*", nick="*", user="*", host="*", authed="*", admin="*", channel="*", chanmodes="*", usermodes="*", limit="5")
    elif split[0] == "query":
        names = dict(mode="", nick="", user="", host="", authed="", admin="", channel="", chanmodes="", usermodes="", limit="5")
    dictized = dict([y for y in [x.split("=") for x in split[1:]] if len(y) == 2])
    names.update(dictized)
    if names["mode"] == None:
        input.notice("mode name is required!")
        return

    namemap = "mode nick user host authed admin channel chanmodes usermodes".split(" ")
    sqlargs = [names[i] for i in namemap]
    if split[0] in ["query", "search"]:
        if split[0] == "query":
            result = query(db, sqlargs).fetchall()
        else:
            result = posquery(db, sqlargs).fetchall()
        names["limit"] = int(names["limit"])
        if not len(result):
            input.notice("no results")
            return
        elif len(result) > names["limit"]:
            input.notice("exceeded your provided limit (limit=%d), cutting off" % names["limit"])

        result = result[:names["limit"]]
        result = [namemap] + [[repr(j)[1:] for j in i] for i in result]

        #hack to justify into a table
        lengths = [[len(result[x][y]) for y in range(len(result[x]))] for x in range(len(result))]
        lengths = [max([lengths[x][i] for x in range(len(result))]) for i in range(len(result[0]))]
        for i in result:
            out = ""
            for j in range(len(result[0])):
                out += i[j].ljust(lengths[j] + 1)
            input.notice(out)
    elif split[0] == "set":
        if "".join(sqlargs[1:]) == "*******" and ("iamsure" not in names or names["iamsure"] != "yes"):
            input.notice("you're trying to set a mode on everything. please repeat with 'iamsure=yes' on the query to confirm.")
            return
        db.execute("insert into botmodes(modename, nick, user, host, authed, admin, channel, chanmodes, usermodes) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", sqlargs)
        db.commit()
        input.notice("done.")
    elif split[0] == "delete":
        db.execute("delete from botmodes where modename=? and nick=? and user=? and host=? and authed=? and admin=? and channel=? and chanmodes=? and usermodes=?", sqlargs)
        db.commit()
        input.notice("done.")
