"""
log.py: written by Scaevolus 2009

edited 2014
"""

import os
import codecs
import time
import re

from cloudbot import hook

stream_cache = {}  # '{server} {chan}': (filename, fd)

formats = {
    "PRIVMSG": "[{server}:{chan}] <{nick}> {message}",
    "PART": "[{server}] -!- {nick} [{user}@{host}] has left {chan}",
    "JOIN": "[{server}] -!- {nick} [{user}@{host}] has joined {param0}",
    "MODE": "[{server}] -!- mode/{chan} [{param_tail}] by {nick}",
    "KICK": "[{server}] -!- {param1} was kicked from {chan} by {nick} ({message})",
    "TOPIC": "[{server}] -!- {nick} changed the topic of {chan} to: {message}",
    "QUIT": "[{server}] -!- {nick} has quit ({message})",
    "PING": "",
    "NOTICE": "[{server}:{chan}] -{nick}- {message}",
    "default": "[{server}] {irc_raw}"
}

action_ctcp_format = "[{server}:{chan}] * {nick} {ctcpmsg}"
known_ctcp_format = "[{server}:{chan}] {nick} has requested CTCP {ctcpcmd}: {ctcpmsg}"
unknown_ctcp_format = "[{server}:{chan}] {nick} ({user}@{host}) requested unknown CTCP {ctcpcmd}: {ctcpmsg}"


def get_ctcp_format(ctcpcmd):
    if ctcpcmd.lower() == "action":
        return action_ctcp_format
    elif ctcpcmd.lower() in ("version", "ping", "time", "finger"):
        return known_ctcp_format
    else:
        return unknown_ctcp_format


irc_color_re = re.compile(r"(\x03(\d+,\d+|\d)|[\x0f\x02\x16\x1f])")


def get_log_filename(data_dir, server, chan):
    return os.path.join(data_dir, "log", gmtime('%Y'), server, chan, (gmtime("%%s.%m-%d.log") % chan).lower())


def gmtime(time_format):
    return time.strftime(time_format, time.gmtime())


def beautify(event):
    """
    :type event: cloudbot.core.events.BaseEvent
    """
    log_format = formats.get(event.irc_command)
    if not log_format:
        return formats["default"].format(server=event.conn.readable_name, irc_raw=event.irc_raw)

    args = {
        "server": event.conn.readable_name, "param_tail": " ".join(event.irc_paramlist[1:]),
        "message": irc_color_re.sub("", event.irc_message), "nick": event.nick, "chan": event.chan,
        "user": event.user, "host": event.host
    }

    _len = len(event.irc_paramlist)
    for n, p in enumerate(event.irc_paramlist):
        args["param" + str(n)] = p
        args["param_" + str(abs(n - _len))] = p

    if event.irc_command == "PRIVMSG" and event.irc_message.count("\x01") >= 2:
        ctcp_split = event.irc_message.split("\x01", 2)[1].split(' ', 1)

        args["ctcpcmd"] = ctcp_split[0]
        if len(ctcp_split) < 2:
            args["ctcpmsg"] = ""
        else:
            args["ctcpmsg"] = ctcp_split[1]

        log_format = get_ctcp_format(args["ctcpcmd"])

    return log_format.format(**args)


def get_log_stream(data_dir, server, chan):
    new_filename = get_log_filename(data_dir, server, chan)
    cache_key = (server, chan)
    old_filename, log_stream = stream_cache.get(cache_key, (None, None))

    if new_filename != old_filename:  # we need to open a new stream
        if log_stream:
            # already open stream needs to be closed
            log_stream.flush()
            log_stream.close()
        data_dir = os.path.split(new_filename)[0]
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        log_stream = codecs.open(new_filename, "a", "utf-8")
        stream_cache[cache_key] = (new_filename, log_stream)

    return log_stream


@hook.event("*", singlethread=True)
def log(bot, event):
    """
    :type bot: cloudbot.core.bot.CloudBot
    :type event: cloudbot.core.events.BaseEvent
    """
    raw_log = get_log_stream(bot.data_dir, event.conn.name, "raw")
    raw_log.write(event.irc_raw + "\n")

    human_readable = beautify(event)

    if human_readable:
        # beautify will return an empty string if event.irc_command is "PING"
        if event.chan:
            channel = event.chan
            # temporary fix until presence tracking is implemented:
        elif event.irc_command == 'QUIT':
            channel = 'quit'
        elif event.irc_command == 'NICK':
            channel = 'nick'
        else:
            channel = None
        if channel:
            channel_log = get_log_stream(bot.data_dir, event.conn.name, channel)
            channel_log.write(human_readable + '\n')


# Log console separately to prevent lag
@hook.event("*", threaded=False)
def console_log(bot, event):
    """
    :type bot: cloudbot.core.bot.CloudBot
    :type event: cloudbot.core.events.BaseEvent
    """
    human_readable = beautify(event)
    if human_readable:
        # beautify will return an empty string if event.irc_command is "PING"
        bot.logger.info(human_readable)
