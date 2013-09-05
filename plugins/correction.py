from util import hook


@hook.regex(r'^(s|S)/.*/.*/\S*$')
def correction(inp, say=None, input=None, notice=None, db=None):
    splitinput = input.msg.split("/")
    if splitinput[3]:
        nick = splitinput[3]
    else:
        nick = input.nick
    last_message = db.execute("select name, quote from seen_user where name"
                              " like ? and chan = ?", (nick.lower(), input.chan.lower())).fetchone()

    if last_message:
        splitinput = input.msg.split("/")
        find = splitinput[1]
        replace = splitinput[2]
        if find in last_message[1]:
            if "\x01ACTION" in last_message[1]:
                message = last_message[1].replace("\x01ACTION ", "/me ").replace("\x01", "")
            else:
                message = last_message[1]
            say("{} meant to say: {}".format(nick, message.replace(find, "\x02" + replace + "\x02")))
        else:
            notice("{} can't be found in your last message".format(find))
    else:
        if nick == input.nick:
            notice("I haven't seen you say anything here yet")
        else:
            notice("I haven't seen {} say anything here yet".format(nick))
