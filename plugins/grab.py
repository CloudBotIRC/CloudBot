import re

from cloudbot import hook

db_ready = []


def db_init(db, conn_name):
    """Check to see that our DB has the grab  table.
    connection name is for caching the result per connection
    :type db: sqlalchemy.orm.Session
    """
    global db_ready
    if db_ready.count(conn_name) < 1:
        db.execute("create table if not exists grab(name, time, quote, chan)")
        db.commit()
        db_ready.append(conn_name)


def grab_add(nick, time, msg, chan, db, conn):
    # Adds a quote to the grab table
    # add the nick, chan, timestamp, msg to the database
    db.execute(
        "insert or replace into grab(name, time, quote, chan)"
        " values(:name, :time, :quote, :chan)",
        {'name': nick, 'time': time, 'quote': msg, 'chan': chan})
    db.commit()


@hook.command()
def grab(text, chan, db, conn):
    """grab <nick> grabs the last message from the
    specified nick and adds it to the quote database"""
    db_init(db, conn.name)
    lastq = db.execute("select name, time, quote, chan from seen_user "
                       "where name = :name and chan = :chan ",
                       {'name': text.lower(), 'chan': chan}).fetchone()
    if lastq:
        #msg = ""
        #if lastq[2].startswith("\x01ACTION"):
        #    msg = lastq[2].replace("\x01ACTION", "* ").replace("\x01", "")
        #else:
        #    msg = lastq[2]

        check = db.execute("select * from grab where name = :name "
                           "and quote = :quote and chan = :chan ",
                           {'name': lastq[0], 'quote': lastq[2],
                            'chan': lastq[3]}).fetchone()
        if check:
            return "the quote has already been added to the database."
        else:
            #if lastq[2].startswith("\x01ACTION"):
            #    msg = lastq[2].replace("\x01ACTION", "* ").replace("\x01", "")
            #else:
            #    msg = lastq[2]    
            grab_add(lastq[0], lastq[1], lastq[2], lastq[3], db, conn)
            lastcheck = db.execute("select * from grab "
                                   "where name = :name and quote = :quote and "
                                   "chan = :chan ", {'name': lastq[0],
                                                     'quote': lastq[2],
                                                     'chan': lastq[3]}
                                   ).fetchone()
            if lastcheck:
                return ("the operation succeeded.")
            else:
                return ("There was a problem adding {} to the DB"
                        ).format(lastq)
    else:
        return ("I couldn't find anything from {}"
                " in the recent messages.".format(text))

def format_grab(name, quote):
    if quote.startswith("\x01ACTION") or quote.startswith("*"):
        quote = quote.replace("\x01ACTION", "").replace("\x01", "")
        out = "* {}{}".format(name, quote)
        return out
    else:
        out = "<{}> {}".format(name, quote)
        return out

@hook.command()
def lastgrab(text, chan, db, message, conn):
    """prints the last grabbed quote from <nick>."""
    db_init(db, conn.name)
    lgrab = db.execute("select name, quote from grab "
                       "where name = :name and chan = :chan order by time "
                       "desc", {'name': text.lower(), 'chan': chan}).fetchone()
    if lgrab:
        quote = lgrab[1]
        message(format_grab(text, quote),chan)
    else:
        return "<{}> has never been grabbed.".format(text)


@hook.command(autohelp=False)
def grabrandom(text, chan, message, db, conn):
    """grabs a random quote from the grab database"""
    db_init(db, conn.name)
    grablist = ""
    name = ""
    if not text:
        grablist = db.execute("select name, quote from grab "
                              "where chan = :chan order by random()",
                              {'chan': chan}).fetchone()
        name = grablist[0]
    else:
        name = text.split(' ')[0]
        grablist = db.execute("select name, quote from grab "
                              "where chan = :chan and name = :name "
                              "order by random()",
                              {'chan': chan, 'name': name.lower()}).fetchone()
    if grablist:
        quote = grablist[1]
        message(format_grab(name, quote), chan)
    else:
        return ("somebody really fucked up, or no quotes have been "
                "grabbed from that nick.")


@hook.command(autohelp=False)
def grabsearch(text, chan, db, conn):
    """.grabsearch <text> matches "text" against nicks or grab strings in the database"""
    out = ""
    result = db.execute(
        "select name, quote from grab where (chan = :chan) and (name like :name or quote like :quote)", {
            "chan": chan, "name": "%{}%".format(
                text.lower()), "quote": "%{}%".format(text)}).fetchall()
    if result:
        for grab in result:
            name = grab[0]
            if text.lower() == name:
                name = text
            quote = grab[1]
            out += "{} {} ".format(format_grab(name, quote), u'\u2022')
        out = out[:-2]
        return out
    else:
        return "I couldn't find any matches for {}.".format(text)
