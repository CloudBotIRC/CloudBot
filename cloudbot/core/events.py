class Input:
    """
    :type bot: cloudbot.core.bot.CloudBot
    :type conn: cloudbot.core.connection.BotConnection
    :type raw: str
    :type prefix: str
    :type command: str
    :type params: str
    :type nick: str
    :type user: str
    :type host: str
    :type mask: str
    :type text: str
    :type match: re.__Match
    :type lastparam: str
    """

    def __init__(self, bot=None, conn=None, raw=None, prefix=None, command=None, params=None, nick=None, user=None,
                 host=None, mask=None, paramlist=None, lastparam=None, text=None, match=None, trigger=None):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type conn: cloudbot.core.irc.BotConnection
        :type raw: str
        :type prefix: str
        :type command: str
        :type params: str
        :type nick: str
        :type user: str
        :type host: str
        :type mask: str
        :type paramlist: list[str]
        :type lastparam: str
        :type text: str
        :type match: re.__Match
        :type trigger: str
        """
        self.bot = bot
        self.conn = conn
        self.raw = raw
        self.prefix = prefix
        self.command = command
        self.params = params
        self.nick = nick
        self.user = user
        self.host = host
        self.mask = mask
        self.paramlist = paramlist
        self.lastparam = lastparam
        self.text = text
        self.match = match
        self.trigger = trigger

    @property
    def paraml(self):
        """
        :rtype: list[str]
        """
        return self.paramlist

    @property
    def msg(self):
        """
        :rtype: str
        """
        return self.lastparam

    @property
    def inp(self):
        """
        :rtype str | re.__Match | list[str]
        """
        if self.text is not None:
            return self.text
        elif self.match is not None:
            return self.match
        else:
            return self.paramlist

    @property
    def server(self):
        """
        :rtype: str
        """
        if self.conn is not None:
            if self.nick is not None and self.chan == self.conn.nick.lower():
                return self.nick
            return self.conn.server
        else:
            return None

    @property
    def chan(self):
        """
        :rtype: str
        """
        if self.paramlist:
            return self.paramlist[0].lower()
        else:
            return None

    @property
    def input(self):
        """
        :rtype; cloudbot.core.main.Input
        """
        return self

    @property
    def loop(self):
        """
        :rtype: asyncio.BaseEventLoop
        """
        return self.bot.loop

    def message(self, message, target=None):
        """sends a message to a specific or current channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan
        self.conn.msg(target, message)

    def reply(self, message, target=None):
        """sends a message to the current channel/user with a prefix
        :type message: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan

        if target == self.nick:
            self.conn.msg(target, message)
        else:
            self.conn.msg(target, "({}) {}".format(self.nick, message))

    def action(self, message, target=None):
        """sends an action to the current channel/user or a specific channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan

        self.conn.ctcp(target, "ACTION", message)

    def ctcp(self, message, ctcp_type, target=None):
        """sends an ctcp to the current channel/user or a specific channel/user
        :type message: str
        :type ctcp_type: str
        :type target: str
        """
        if target is None:
            if self.chan is None:
                raise ValueError("Target must be specified when chan is not assigned")
            target = self.chan
        self.conn.ctcp(target, ctcp_type, message)

    def notice(self, message, target=None):
        """sends a notice to the current channel/user or a specific channel/user
        :type message: str
        :type target: str
        """
        if target is None:
            if self.nick is None:
                raise ValueError("Target must be specified when nick is not assigned")
            target = self.nick

        self.conn.cmd('NOTICE', [target, message])

    def has_permission(self, permission, notice=True):
        """ returns whether or not the current user has a given permission
        :type permission: str
        :rtype: bool
        """
        if not self.mask:
            raise ValueError("has_permission requires mask is not assigned")
        return self.conn.permissions.has_perm_mask(self.mask, permission, notice=notice)

