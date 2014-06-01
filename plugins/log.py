"""
log.py: written by Scaevolus 2009

edited 2014
"""
import asyncio
import os
import codecs
import time
import re

from cloudbot import hook

log_dir = os.path.join(os.path.abspath("."), "logs")

stream_cache = {}  # '{server} {chan}': (filename, fd)

formats = {
    "PRIVMSG": "[{server}:{chan}] <{nick}> {message}",
    "PART": "[{server}:{chan}] -!- {nick} [{user}@{host}] has left {chan}",
    "JOIN": "[{server}:{chan}] -!- {nick} [{user}@{host}] has joined {chan}",
    "MODE": "[{server}:{chan}] -!- mode/{chan} [{param_tail}] by {nick}",
    "KICK": "[{server}:{chan}] -!- {param1} was kicked from {chan} by {nick} ({message})",
    "TOPIC": "[{server}:{chan}] -!- {nick} changed the topic of {chan} to: {message}",
    "QUIT": "[{server}] -!- {nick} has quit ({message})",
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


def get_log_filename(server, chan):
    _time = time.gmtime()
    return os.path.join(log_dir, time.strftime('%Y', _time), server, chan,
                        (time.strftime("{}.%m-%d.log".format(chan), _time)).lower())


def beautify(event):
    """
    :type event: cloudbot.core.events.BaseEvent
    :rtype: str
    """
    if event.bot.config.get("skip_motd", False) and event.irc_command in ["375", "372", "376"]:
        return None
    if event.bot.config.get("skip_server_info", False) and event.irc_command in ["003", "005", "250", "251", "252",
                                                                                 "253", "254", "255", "256"]:
        return None
    if event.irc_command == "PING":
        return None
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


def get_log_stream(server, chan):
    new_filename = get_log_filename(server, chan)
    cache_key = (server, chan)
    old_filename, log_stream = stream_cache.get(cache_key, (None, None))

    if new_filename != old_filename:  # we need to open a new stream
        if log_stream:
            # already open stream needs to be closed
            log_stream.flush()
            log_stream.close()
        data_dir = os.path.dirname(new_filename)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        log_stream = codecs.open(new_filename, "a", "utf-8")
        stream_cache[cache_key] = (new_filename, log_stream)

    return log_stream


@hook.irc_raw("*", singlethread=True)
def log(event):
    """
    :type event: cloudbot.core.events.BaseEvent
    """
    raw_log = get_log_stream(event.conn.name, "raw")
    raw_log.write(event.irc_raw + "\n")

    human_readable = beautify(event)

    if human_readable:
        # beautify will return an empty string if event.irc_command is "PING"
        if event.irc_command in ["PRIVMSG", "PART", "JOIN", "MODE", "TOPIC", "QUIT", "NOTICE"] and event.chan:
            channel = event.chan
            # temporary fix until presence tracking is implemented:
        elif event.irc_command == 'QUIT':
            channel = 'quit'
        elif event.irc_command == 'NICK':
            channel = 'nick'
        else:
            channel = None
        if channel:
            channel_log = get_log_stream(event.conn.name, channel)
            channel_log.write(human_readable + '\n')


# Log console separately to prevent lag
@asyncio.coroutine
@hook.irc_raw("*")
def console_log(bot, event):
    """
    :type bot: cloudbot.core.bot.CloudBot
    :type event: cloudbot.core.events.BaseEvent
    """
    human_readable = beautify(event)
    if human_readable:
        # beautify will return an empty string if event.irc_command is "PING"
        bot.logger.info(human_readable)
