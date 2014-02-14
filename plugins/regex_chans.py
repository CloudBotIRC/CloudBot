from util import hook


# Default value.
# If True, all channels without a setting will have regex enabled
# If False, all channels without a setting will have regex disabled
default_enabled = True

db_ready = False


def db_init(db):
    global db_ready
    if not db_ready:
        db.execute("CREATE TABLE IF NOT EXISTS regexchans(channel PRIMARY KEY, status)")
        db.commit()
        db_ready = True


def get_status(db, channel):
    row = db.execute("SELECT status FROM regexchans WHERE channel = ?", [channel]).fetchone()
    if row:
        return row[0]
    else:
        return None


def set_status(db, channel, status):
    row = db.execute("REPLACE INTO regexchans (channel, status) VALUES(?, ?)", [channel, status])
    db.commit()


def delete_status(db, channel):
    row = db.execute("DELETE FROM regexchans WHERE channel = ?", [channel])
    db.commit()


def list_status(db):
    row = db.execute("SELECT * FROM regexchans").fetchall()
    result = None
    for values in row:
        if result:
            result += u", {}: {}".format(values[0], values[1])
        else:
            result = u"{}: {}".format(values[0], values[1])
    return result


@hook.sieve
def sieve_regex(bot, inp, func, kind, args):
    db = bot.get_db_connection(inp.conn)
    db_init(db)
    if kind == 'regex' and inp.chan.startswith("#") and func.__name__ != 'factoid':
        chanstatus = get_status(db, inp.chan)
        if chanstatus != "ENABLED" and (chanstatus == "DISABLED" or not default_enabled):
            print u"Denying input.raw={}, kind={}, args={} from {}".format(inp.raw, kind, args, inp.chan)
            return None
        print u"Allowing input.raw={}, kind={}, args={} from {}".format(inp.raw, kind, args, inp.chan)

    return inp


@hook.command(permissions=["botcontrol"])
def enableregex(inp, db=None, message=None, notice=None, chan=None, nick=None):
    db_init(db)
    inp = inp.strip().lower()
    if not inp:
        channel = chan
    elif inp.startswith("#"):
        channel = inp
    else:
        channel = u"#{}".format(inp)

    message(u"Enabling regex matching (youtube, etc) (issued by {})".format(nick), target=channel)
    notice(u"Enabling regex matching (youtube, etc) in channel {}".format(channel))
    set_status(db, channel, "ENABLED")


@hook.command(permissions=["botcontrol"])
def disableregex(inp, db=None, message=None, notice=None, chan=None, nick=None):
    db_init(db)
    inp = inp.strip().lower()
    if not inp:
        channel = chan
    elif inp.startswith("#"):
        channel = inp
    else:
        channel = u"#{}".format(inp)

    message(u"Disabling regex matching (youtube, etc) (issued by {})".format(nick), target=channel)
    notice(u"Disabling regex matching (youtube, etc) in channel {}".format(channel))
    set_status(db, channel, "DISABLED")


@hook.command(permissions=["botcontrol"])
def resetregex(inp, db=None, message=None, notice=None, chan=None, nick=None):
    db_init(db)
    inp = inp.strip().lower()
    if not inp:
        channel = chan
    elif inp.startswith("#"):
        channel = inp
    else:
        channel = u"#{}".format(inp)

    message(u"Resetting regex matching setting (youtube, etc) (issued by {})".format(nick), target=channel)
    notice(u"Resetting regex matching setting (youtube, etc) in channel {}".format(channel))
    delete_status(db, channel)


@hook.command(permissions=["botcontrol"])
def regexstatus(inp, db=None, chan=None):
    db_init(db)
    inp = inp.strip().lower()
    if not inp:
        channel = chan
    elif inp.startswith("#"):
        channel = inp
    else:
        channel = u"#{}".format(inp)

    return u"Regex status for {}: {}".format(channel, get_status(db, channel))


@hook.command(permissions=["botcontrol"])
def listregex(inp, db=None):
    db_init(db)
    return list_status(db)
