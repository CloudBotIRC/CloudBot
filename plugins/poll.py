from collections import defaultdict
from json import dumps
from re import findall
from cloudbot import hook
from cloudbot.util import web


def tree():  # autovivification
    return defaultdict(tree)


active_polls = tree()


@hook.command(autohelp=True)
def poll(text, conn, nick, chan, message):
    """poll <description>: choice1, choice2, ... - Begins a poll (if it does not exist). Choice defaults are [yes|no]. end poll and get results with 'poll close'."""
    global active_polls
    active_polls[chan]  # init

    global bot_prefix
    bot_prefix = conn.config["command_prefix"]

    if text == "close":
        if active_polls.get(chan).get(nick) is None:
            return "You do not have an active poll."
        else:
            active_polls[chan][nick]['results']['total'] = len(active_polls[chan][nick]['votes'].keys())
            for choice in active_polls[chan][nick]['choices']:
                active_polls[chan][nick]['results']['choices'][choice] = len([x for x in active_polls[chan][nick]['votes'] if active_polls[chan][nick]['votes'][x] == choice])
            results = web.paste(dumps(dict(active_polls.get(chan).get(nick)), sort_keys=True, indent=2))
            del active_polls[chan][nick]
            message("Results for {}'s poll: {}".format(nick, results))
            return
    if active_polls.get(chan).get(nick) is not None:
        return "You already have an active poll: '{}'.".format(active_polls[chan][nick]['description'])

    if ':' in text:
        desc, choices = text.split(':')
        c = findall(r'([^,]+)', choices)
        if len(c) == 1:
            c = findall(r'(\S+)', choices)
        choices = list(set(x.strip() for x in c))
    else:
        desc = text
        choices = ["yes", "no"]

    active_polls[chan][nick]['description'] = desc
    active_polls[chan][nick]['choices'] = choices
    active_polls[chan][nick]['votes']
    message("Poll '{1}' started by {0}; to vote use '{3}vote {0} <{2}>'.".format(nick, desc, "|".join(choices), bot_prefix))


@hook.command(autohelp=False)
def polls(text, chan, message):
    """.polls [user] - Gets a list of active polls, or information on a specific poll."""
    global active_polls
    active_polls[chan]  # init

    if text:
        if active_polls.get(chan).get(text):
            message("{}'s '{}' poll choices: {}".format(text, active_polls.get(chan).get(text).get('description'), ', '.join(active_polls.get(chan).get(text).get('choices'))))
        else:
            message("No active poll for {}.".format(text))
    else:
        message("Active polls: {}".format((", ".join(active_polls.get(chan).keys()) if active_polls.get(chan) else "None")))


@hook.command(autohelp=True)
def vote(text, nick, chan, notice):
    """.vote <poll> <choice> - Vote on a poll; responds on error and silently records on success."""
    global active_polls
    active_polls[chan]  # init

    if len(text.split(' ', 1)) == 2:
        poll, vote = text.split(' ', 1)
        if active_polls.get(chan).get(poll) is None:
            return "The poll you are trying to vote for no longer exists."
        if vote not in active_polls.get(chan).get(poll).get('choices'):
            return "Invalid vote; valid choices are: {}".format(', '.join(active_polls.get(chan).get(poll).get('choices')))
    else:
        return "Please use form '{0}vote <poll> <choice>'. Check active polls with '{0}polls'.".format(bot_prefix)

    active_polls[chan][poll]['votes'][nick] = vote
    notice("You have successfully voted for {}".format(vote))