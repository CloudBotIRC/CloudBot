#import asyncio
import re

from cloudbot import hook
#from cloudbot.util import timesince
from cloudbot.event import EventType

karmaplus_re = re.compile('^.*\+\+$')
karmaminus_re = re.compile('^.*\-\-$')
db_ready = []

def db_init(db, conn_name):
    """Check to see if the DB has the herald table. Connection name is for caching the result per connection.
    :type db: sqlalchemy.orm.Session
    """
    global db_ready
    if db_ready.count(conn_name) < 1:
        db.execute("create table if not exists karma(name, chan, thing, score INTEGER, primary key(name, chan, thing))")
        db.commit()
        db_ready.append(conn_name)


@hook.command("pp", "addpoint")
def addpoint(text, nick, chan, db, conn):
    """.addpoint or (.pp) <thing> adds a point to the <thing>"""
    
    db_init(db, conn.name)
    karma = db.execute("select score from karma where name = :name and chan = :chan and thing = :thing", {'name':nick, 'chan': chan, 'thing': text.lower()}).fetchone()
    if karma:
        score = int(karma[0])
        score = score + 1
        db.execute("insert or replace into karma(name, chan, thing, score) values (:name, :chan, :thing, :score)", {'name': nick, 'chan': chan, 'thing': text.lower(), 'score': score})
        db.commit()
        # return "{} is now worth {} in {}'s eyes.".format(text, score, nick)
    else:
        db.execute("insert or replace into karma(name, chan, thing, score) values (:name, :chan, :thing, :score)", {'name': nick, 'chan': chan, 'thing': text.lower(), 'score': 1})
        db.commit()
        #return "{} is now worth 1 in {}'s eyes.".format(text, nick)

@hook.regex(karmaplus_re)
def re_addpt(match, nick, chan, db, conn, notice):
    """no useful help txt"""
    thing = match.group().split('++')[0]
    if thing:
        addpoint(thing, nick, chan, db, conn)
        #return out
    else:
        notice(pluspts(nick, chan, db, conn))

@hook.command("mm", "rmpoint")
def rmpoint(text, nick, chan, db, conn):
    """.rmpoint or (.mm) <thing> subtracts a point from the <thing>"""

    db_init(db, conn.name)
    karma = db.execute("select score from karma where name = :name and chan = :chan and thing = :thing", {'name':nick, 'chan': chan, 'thing': text.lower()}).fetchone()
    if karma:
        score = int(karma[0])
        score = score - 1
        db.execute("insert or replace into karma(name, chan, thing, score) values (:name, :chan, :thing, :score)", {'name': nick, 'chan': chan, 'thing': text.lower(), 'score': score})
        db.commit()
        #return "{} is now worth {} in {}'s eyes.".format(text, score, nick)
    else:
        db.execute("insert or replace into karma(name, chan, thing, score) values (:name, :chan, :thing, :score)", {'name': nick, 'chan': chan, 'thing': text.lower(), 'score': -1})
        db.commit()
        #return "{} is now worth -1 in {}'s eyes.".format(text, nick)


@hook.command("pluspts", autohelp=False)
def pluspts(nick, chan, db, conn):
    """prints the things you have liked"""
    db_init(db, conn.name)
    output = ""
    likes = db.execute("select thing, score from karma where name = :name and chan = :chan and score >= 0 order by score desc", { 'name': nick, 'chan': chan }).fetchall()
    for like in likes:
       output = output + str(like[0]) + " has " + str(like[1]) + " points "
    return output

@hook.command("minuspts", autohelp=False)
def minuspts(nick, chan, db, conn):
    """prints the things you have liked"""
    db_init(db, conn.name)
    output = ""
    likes = db.execute("select thing, score from karma where name = :name and chan = :chan and score <= 0 order by score", { 'name': nick, 'chan': chan }).fetchall()
    for like in likes:
       output = output + str(like[0]) + " has " + str(like[1]) + " points "
    return output

@hook.regex(karmaminus_re)
def re_rmpt(match, nick, chan, db, conn, notice):
    """no useful help txt"""
    thing = match.group().split('--')[0]
    if thing:
        rmpoint(thing, nick, chan, db, conn)
        #return out
    else:
        notice(minuspts(nick, chan, db, conn))


@hook.command("points", autohelp=False)
def points(text, chan, db, conn):
    """.points <thing> will print the total points for <thing> in the channel."""
    db_init(db, conn.name)
    score = 0
    karma = db.execute("select score from karma where thing = :thing and chan = :chan", {'thing': text.lower(), 'chan': chan }).fetchall()
    if karma:
        for k in karma:
            score = score + int(k[0])
        return "{} has a total score of {} in {}.".format(text, score, chan)
    else:
        return "I couldn't find {} in the database.".format(text)
