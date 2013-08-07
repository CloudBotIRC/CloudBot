from util import hook
import re

db_ready=False

# from seen.py
def db_init(db):
    "check to see that our db has the the correction table and return a connection."
    db.execute("create table if not exists correct_user(name, quote, chan, "
                 "primary key(name, chan))")
    db.commit()
    db_ready = True

@hook.singlethread
@hook.event('PRIVMSG')
def message_sieve(paraml, input=None, db=None, bot=None):
    if not db_ready:
        db_init(db)
    if not re.findall('^s/.*/.*/$', input.msg.lower()):
        db.execute("insert or replace into correct_user(name, quote, chan)"
            "values(?,?,?)", (input.nick.lower(), input.msg, input.chan.lower()))
        db.commit()

@hook.regex(r'^(s|S)/.*/.*/$')
def correction(inp, say=None, input=None, notice=None, db=None):
    if not db_ready:
        db_init(db)

    last_message = db.execute("select name, quote from correct_user where name"
                           " like ? and chan = ?", (input.nick.lower(), input.chan.lower())).fetchone()

    if last_message:
        splitinput = input.msg.split("/")
        find = splitinput[1]
        replace = splitinput[2]
        if find in last_message[1]:
            say("%s meant to say: %s" % (input.nick, last_message[1].replace(find, replace)))
        else:
            notice("%s can't be found in your last message" % find)
    else:
        notice("I haven't seen you say anything here yet")
