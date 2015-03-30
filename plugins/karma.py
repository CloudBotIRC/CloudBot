from cloudbot import hook
from cloudbot.util import timeformat, formatting, database

import time
import re

CAN_DOWNVOTE = False

from sqlalchemy import Table, Column, Integer, String, PrimaryKeyConstraint
from sqlalchemy import select

karma_table = Table(
    'karma',
    database.metadata,
    Column('nick_vote', String(25)),
    Column('up_karma', Integer, default=0),
    Column('down_karma', Integer, default=0),
    PrimaryKeyConstraint('nick_vote')
)

voters = {}


def up(db, nick_vote):
    """ gives one karma to a user """
    db.execute("""INSERT or IGNORE INTO karma(
        nick_vote,
        up_karma,
        down_karma,
        total_karma) values(:nick,0,0,0)""", {'nick': nick_vote.lower()})
    query = karma_table.update().values(
        up_karma=karma_table.c.up_karma + 1
    ).where(karma_table.c.nick_vote == nick_vote.lower())
    db.execute(query)
    db.commit()


def down(db, nick_vote):
    """ takes one karma away from a user """
    db.execute("""INSERT or IGNORE INTO karma(
        nick_vote,
        up_karma,
        down_karma,
        total_karma) values(:nick,0,0,0)""", {'nick': nick_vote.lower()})
    query = karma_table.update().values(
        down_karma=karma_table.c.down_karma + 1
    ).where(karma_table.c.nick_vote == nick_vote.lower())
    db.execute(query)
    db.commit()


def allowed(uid):
    """ checks if a user is allowed to vote, and keeps track of voters """
    global voters
    time_restriction = 300.0

    # clear expired voters
    for _uid, _timestamp in voters.items():
        if (time.time() - _timestamp) >= time_restriction:
            del voters[_uid]

    if uid in voters:
        last_voted = voters[uid]
        return False, timeformat.time_until(last_voted, now=time.time() - time_restriction)
    else:
        voters[uid] = time.time()
        return True, 0

karma_re = re.compile('^([a-z0-9_\-\[\]\\^{}|`]{3,})(\+\+|\-\-)$', re.I)


@hook.regex(karma_re)
def karma_add(match, nick, conn, db, notice):
    nick_vote = match.group(1).strip()
    if nick.lower() == nick_vote.lower():
        notice("You can't vote on yourself!")
        return

    uid = ":".join([conn.name, nick, nick_vote]).lower()
    vote_allowed, when = allowed(uid)

    if vote_allowed:
        if match.group(2) == '++':
            up(db, nick_vote)
            notice("Gave {} 1 karma!".format(nick_vote))
        if match.group(2) == '--' and CAN_DOWNVOTE:
            down(db, nick_vote)
            notice("Took away 1 karma from {}.".format(nick_vote))
        else:
            return
    else:
        notice("You are trying to vote too often. You can vote on this user again in {}!".format(when))


@hook.command('karma', 'k')
def karma(text, chan, db):
    """k/karma <nick> -- returns karma stats for <nick>"""

    if not chan.startswith('#'):
        return

    nick_vote = text

    query = db.execute(
        select([karma_table])
        .where(karma_table.c.nick_vote == nick_vote.lower())
    ).fetchall()

    if not query:
        return "That user has no karma."
    else:
        query = query[0]
        karma_text = formatting.pluralize(query['up_karma'] - query['down_karma'], 'karma point')
        return "{} has {}.".format(nick_vote, karma_text)