from util import hook
import re

@hook.regex(r'^(s|S)/.*/.*/$')
def correction(inp, say=None, input=None, notice=None, db=None):

    last_message = db.execute("select name, quote from seen_user where name"
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
