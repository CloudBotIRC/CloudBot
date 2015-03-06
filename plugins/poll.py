from re import findall

from cloudbot import hook

from cloudbot.util.formatting import pluralize, get_text_list


polls = {}


class PollError(Exception):
    pass


class PollOption:
    def __init__(self, title):
        self.title = title
        self.votes = 0


class Poll:
    def __init__(self, question, creator, options=["Yes", "No"]):
        self.question = question
        self.creator = creator
        self.options = {i.lower(): PollOption(i) for i in options}

        self.voted = []

    def vote(self, voted_option, voter):
        """
        Adds a vote to a specific poll option. Raises PollError if option is invalid or user has already voted.
        Returns PollOption if sucessful.
        :param voted_option: The poll option to vote on
        :param voter: The user who is voting on the poll
        """
        voted_option = voted_option.lower()

        # check if the option is valid
        if voted_option not in self.options.keys():
            raise PollError("Invalid option")

        # make sure the user hasn't already voted
        if voter.lower() in self.voted:
            raise PollError("Sorry, you have already voted on this poll.")

        option = self.options.get(voted_option)
        option.votes += 1

        self.voted.append(voter.lower())
        return option


@hook.command()
def poll(text, conn, nick, chan, message):
    global polls

    # get poll ID
    uid = ":".join([conn.name, chan, nick]).lower()

    if text.lower() == "close":
        if uid not in polls.keys():
            return "You have no active poll to close."

        poll = polls.get(uid)
        message("Your poll has been closed. Final results for \x02{}\x02:".format(poll.question, poll.creator))
        #message(", ".join(poll.options.values()))
        del polls[uid]
        return

    if uid in polls.keys():
        return "You already have an active poll in this channel, you must close it before you can create a new one."

    if ':' in text:
        question, options = text.strip().split(':')
        c = findall(r'([^,]+)', options)
        if len(c) == 1:
            c = findall(r'(\S+)', options)
        options = list(set(x.strip() for x in c))
        _poll = Poll(question, nick, options)
    else:
        question = text.strip()
        _poll = Poll(question, nick)

    # store poll in list
    polls[uid] = _poll

    option_str = get_text_list([option.title for option in _poll.options.values()], "and")
    message('Created poll "{}" with the following options: {}'.format(_poll.question, option_str))
    message("Use .vote {} <option> to vote on this poll!".format(nick.lower()))


@hook.command(autohelp=True)
def vote(text, nick, conn, chan, notice):
    """.vote <poll> <choice> - Vote on a poll; responds on error and silently records on success."""
    global polls

    if len(text.split(' ', 1)) == 2:
        _user, option = text.split(' ', 1)
        uid = ":".join([conn.name, chan, _user]).lower()
    else:
        return "Invalid input!"

    if uid not in polls.keys():
        return "There is no poll active from that user!"

    poll = polls.get(uid)

    try:
        voted_option = poll.vote(option, nick)
    except PollError as e:
        return "{}".format(e)

    return "Saved vote. {} now has {} votes.".format(voted_option.title, voted_option.votes)


@hook.command(autohelp=True)
def results(text, conn, chan, message):
    """.vote <poll> <choice> - Vote on a poll; responds on error and silently records on success."""
    global polls

    # get poll ID and see if it exists
    uid = ":".join([conn.name, chan, text]).lower()
    if uid not in polls.keys():
        return "There is no poll active from that user!"

    poll = polls.get(uid)

    message("Results for \x02{}\x02 by \x02{}\x02:".format(poll.question, poll.creator))
    message(", ".join(poll.options.values()))
