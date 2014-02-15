from util import hook
from urllib import unquote

@hook.command(autohelp=False)
def googleurl(inp, db=None, nick=None):
    """googleurl [nickname] - Converts Google urls (google.com/url) to normal urls
       where possible, in the specified nickname's last message. If nickname isn't provided,
       action will be performed on user's last message"""
    if not inp:
        inp = nick
    last_message = db.execute("select name, quote from seen_user where name"
                              " like ? and chan = ?", (inp.lower(), input.chan.lower())).fetchone()
    if last_message:
        msg = last_message[1]
        out = ", ".join([(unquote(a[4:]) if a[:4] == "url=" else "") for a in msg.split("&")])\
              .replace(", ,", "").strip()
        return out if out else "No matches in your last message."
    else:
        if inp == nick:
            return "You haven't said anything in this channel yet!"
        else:
            return "That user hasn't said anything in this channel yet!"
