"""
log.py: written by Scaevolus 2009

edited 2014
"""

import os
import codecs
import time
import re

from util import hook


stream_cache = {}  # '{server} {chan}': (filename, fd)

formats = {
    "PRIVMSG": "[{server}:{chan}] <{nick}> {msg}",
    "PART": "[{server}] -!- {nick} [{user}@{host}] has left {chan}",
    "JOIN": "[{server}] -!- {nick} [{user}@{host}] has joined {param0}",
    "MODE": "[{server}] -!- mode/{chan} [{param_tail}] by {nick}",
    "KICK": "[{server}] -!- {param1} was kicked from {chan} by {nick} ({msg})",
    "TOPIC": "[{server}] -!- {nick} changed the topic of {chan} to: {msg}",
    "QUIT": "[{server}] -!- {nick} has quit ({msg})",
    "PING": "",
    "NOTICE": "[{server}:{chan}] -{nick}- {msg}",
    "default": "[{server}] {raw}"
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


def beautify(input):
    log_format = formats.get(input.command, formats.get("default"))
    args = input.__dict__

    leng = len(args["paraml"])
    for n, p in enumerate(args["paraml"]):
        args["param" + str(n)] = p
        args["param_" + str(abs(n - leng))] = p

    args["param_tail"] = " ".join(args["paraml"][1:])
    args["msg"] = irc_color_re.sub("", args["msg"])

    if input.command == "PRIVMSG" and input.msg.count("\x01") >= 2:
        ctcp_split = input.msg.split("\x01", 2)[1].split(' ', 1)

        args["ctcpcmd"] = ctcp_split[0]
        if len(ctcp_split) < 2:
            args["ctcpmsg"] = ""
        else:
            args["ctcpmsg"] = ctcp_split[1]

        log_format = get_ctcp_format(args["ctcpcmd"])

    return log_format.format(**args)


def get_log_stream(data_dir, server, chan):
    new_filename = get_log_filename(data_dir, server, chan)
    cache_key = "{} {}".format(server, chan)
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


@hook.event("*")
def log(paraml, input=None, bot=None):
    """
    :type input: core.main.Input
    :type bot: core.bot.CloudBot
    """
    raw_log = get_log_stream(bot.data_dir, input.server, "raw")
    raw_log.write(input.raw + "\n")

    human_readable = beautify(input)

    if human_readable:
        # beautify will return an empty string if input.command is "PING"
        if input.chan:
            channel = input.chan
            # temporary fix until presence tracking is implemented:
        elif input.command == 'QUIT':
            channel = 'quit'
        elif input.command == 'NICK':
            channel = 'nick'
        else:
            channel = None
        if channel:
            channel_log = get_log_stream(bot.data_dir, input.server, channel)
            channel_log.write(human_readable + '\n')

        bot.logger.info(human_readable)
