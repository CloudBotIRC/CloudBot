from urllib.parse import unquote

from cloudbot import hook


@hook.command(autohelp=False)
def googleurl(text, db, nick):
    """[nickname] - converts Google urls (google.com/url) to normal urls where possible, [nickname]'s last message, defaulting to the caller's last message if no nickname is specified"""
    if not text:
        text = nick
    last_message = db.execute("select name, quote from seen_user where name"
                              " like ? and chan = ?", (text.lower(), input.chan.lower())).fetchone()
    if last_message:
        msg = last_message[1]
        out = ", ".join([(unquote(a[4:]) if a[:4] == "url=" else "") for a in msg.split("&")]) \
            .replace(", ,", "").strip()
        return out if out else "No matches in your last message."
    else:
        if text == nick:
            return "You haven't said anything in this channel yet!"
        else:
            return "That user hasn't said anything in this channel yet!"
