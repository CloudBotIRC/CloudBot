import asyncio
import logging
import os
import codecs
import time
import re
import itertools

import cloudbot
from cloudbot import hook
from cloudbot.event import EventType

logger = logging.getLogger('cloudbot')

irc_color_re = re.compile(r"(\x03(\d+,\d+|\d)|[\x0f\x02\x16\x1f])")


def strip_colors(text):
    """
    :param text: Text to strip
    :return: Text stripped of IRC colors
    :type text: str
    :rtype: str
    """
    return irc_color_re.sub('', text)

# +---------+
# | Formats |
# +---------+


base_formats = {
    EventType.message: "[{server}:{channel}] <{nick}> {content}",
    EventType.action: "[{server}:{channel}] * {nick} {content}",
    EventType.join: "[{server}:{channel}] -!- {nick} [{user}@{host}] has joined",
    EventType.part: "[{server}:{channel}] -!- {nick} [{user}@{host}] has left ({content})",
    EventType.kick: "[{server}:{channel}] -!- {nick} has kicked {target} ({content})",
}

irc_formats = {
    "MODE": "[{server}:{channel}] -!- mode/{channel} [{param_tail}] by {nick}",
    "MODE2": "[{server}] -!- mode/{target} [{param_tail}] by {nick}",
    "TOPIC": "[{server}:{channel}] -!- {nick} has changed the topic to: {content}",
    "QUIT": "[{server}] -!- {nick} has quit ({content})",
    "INVITE": "[{server}] -!- {nick} has invited {target} to {content}",
    "NICK": "[{server}] {nick} is now known as {content}",
    "NOTICE": "[{server}:{channel}] -{nick}- {content}",
}

irc_default = "[{server}] {irc_raw}"

ctcp_known = "[{server}:{channel}] {nick} [{user}@{host}] has requested CTCP {ctcp_command}"
ctcp_known_with_message = ("[{server}:{channel}] {nick} [{user}@{host}] "
                           "has requested CTCP {ctcp_command}: {ctcp_message}")


# +------------+
# | Formatting |
# +------------+

def format_event(event):
    """
    Format an event
    :type event: cloudbot.event.Event
    :rtype: str
    """

    # Setup arguments

    args = {
        "server": event.conn.readable_name, "target": event.target, "channel": event.chan_name, "nick": event.nick,
        "user": event.user, "host": event.host
    }

    if event.content is not None:
        # We can't strip colors from None
        args["content"] = strip_colors(event.content)
    else:
        args["content"] = None

    # Try formatting with non-connection-specific formats

    if event.type in base_formats:
        return base_formats[event.type].format(**args)

    # Try formatting with IRC-formats, if this is an IRC event
    if event.irc_command is not None:
        return format_irc_event(event, args)


def format_irc_event(event, args):
    """
    Format an IRC event
    :type event: cloudbot.event.Event
    :param event: The event to format
    :param args: The pre-created arguments
    """

    # Setup arguments

    # Add the IRC-specific param_tail argument to the generic arguments
    args["param_tail"] = " ".join(event.irc_command_params[1:])

    # Try formatting with the IRC command

    if event.irc_command in irc_formats:
        if event.irc_command == "MODE" and event.chan_name is None:
            return irc_formats["MODE2"].format(**args)  # special mode case
        return irc_formats[event.irc_command].format(**args)

    # Try formatting with the CTCP command

    if event.irc_ctcp_text is not None:
        ctcp_command, ctcp_message = event.irc_ctcp_text.split(None, 1)
        args["ctcp_command"] = ctcp_command
        args["ctcp_message"] = ctcp_message

        if ctcp_message:
            return ctcp_known_with_message.format(**args)
        else:
            return ctcp_known.format(**args)

    # No formats have been found, resort to the default

    # Check if the command is blacklisted for raw output

    logging_config = event.bot.config.get("logging", {})

    if not logging_config.get("show_motd", True) and event.irc_command in ("375", "372", "376"):
        return None
    elif not logging_config.get("show_server_info", True) and event.irc_command in (
            "003", "005", "250", "251", "252", "253", "254", "255", "256"):
        return None
    elif event.irc_command == "PING":
        return None

    # Format using the default raw format

    return irc_default.format(server=event.conn.readable_name, irc_raw=event.irc_raw)

# +--------------+
# | File logging |
# +--------------+

file_format = "{server}_{chan}_%Y%m%d.log"
raw_file_format = "{server}_%Y%m%d.log"

folder_format = "%Y"

# Stream cache, (server, chan) -> (file_name, stream)
stream_cache = {}
# Raw stream cache, server -> (file_name, stream)
raw_cache = {}


def get_log_filename(server, chan):
    current_time = time.gmtime()
    folder_name = time.strftime(folder_format, current_time)
    file_name = time.strftime(file_format.format(chan=chan, server=server), current_time).lower()
    return os.path.join(cloudbot.log_dir, folder_name, file_name)


def get_log_stream(server, chan):
    new_filename = get_log_filename(server, chan)
    cache_key = (server, chan)
    old_filename, log_stream = stream_cache.get(cache_key, (None, None))

    # If the filename has changed since we opened the stream, we should re-open
    if new_filename != old_filename:
        # If we had a stream open before, we should close it
        if log_stream is not None:
            log_stream.flush()
            log_stream.close()

        log_dir = os.path.dirname(new_filename)
        os.makedirs(log_dir, exist_ok=True)

        log_stream = codecs.open(new_filename, "a", "utf-8")
        stream_cache[cache_key] = (new_filename, log_stream)

    return log_stream


def get_raw_log_filename(server):
    current_time = time.gmtime()
    folder_name = time.strftime(folder_format, current_time)
    file_name = time.strftime(raw_file_format.format(server=server), current_time).lower()
    return os.path.join(cloudbot.log_dir, "raw", folder_name, file_name)


def get_raw_log_stream(server):
    new_filename = get_raw_log_filename(server)
    old_filename, log_stream = stream_cache.get(server, (None, None))

    # If the filename has changed since we opened the stream, we should re-open
    if new_filename != old_filename:
        # If we had a stream open before, we should close it
        if log_stream is not None:
            log_stream.flush()
            log_stream.close()

        log_dir = os.path.dirname(new_filename)
        os.makedirs(log_dir, exist_ok=True)

        log_stream = codecs.open(new_filename, "a", "utf-8")
        stream_cache[server] = (new_filename, log_stream)

    return log_stream


@hook.irc_raw("*", singlethread=True)
def log_raw(event):
    """
    :type event: cloudbot.event.Event
    """
    logging_config = event.bot.config.get('logging', {})
    if not logging_config.get("raw_file_log", False):
        return

    get_raw_log_stream(event.conn.name).write(event.irc_raw + "\n")


@hook.irc_raw("*", singlethread=True)
def log(event):
    """
    :type event: cloudbot.event.Event
    """
    text = format_event(event)

    if text is not None:
        if event.irc_command in ["PRIVMSG", "PART", "JOIN", "MODE", "TOPIC", "QUIT", "NOTICE"] and event.chan_name:
            get_log_stream(event.conn.name, event.chan_name).write(text + '\n')


# Log console separately to prevent lag
@asyncio.coroutine
@hook.irc_raw("*", run_first=True)
def console_log(event):
    """
    :type event: cloudbot.event.Event
    """
    text = format_event(event)
    if text is not None:
        logger.info(text)


@hook.command('flushlogs', permissions=["bot.manage"])
def flush_log():
    for stream in [pair[1] for pair in itertools.chain(stream_cache.values(), raw_cache.values())]:
        stream.flush()


@hook.on_stop()
def close_logs():
    for stream in [pair[1] for pair in itertools.chain(stream_cache.values(), raw_cache.values())]:
        stream.flush()
        stream.close()