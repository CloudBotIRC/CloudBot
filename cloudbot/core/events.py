class BaseEvent:
    """
    :type bot: cloudbot.core.bot.CloudBot
    :type conn: cloudbot.core.connection.BotConnection
    :type hook: cloudbot.core.pluginmanager.Hook
    :type irc_raw: str
    :type irc_prefix: str
    :type irc_command: str
    :type irc_paramlist: str
    :type irc_message: str
    :type nick: str
    :type user: str
    :type host: str
    :type mask: str
    """

    def __init__(self, bot=None, conn=None, hook=None, base_event=None, irc_raw=None, irc_prefix=None, irc_command=None,
                 irc_paramlist=None, irc_message=None, nick=None, user=None, host=None, mask=None):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type conn: cloudbot.core.irc.BotConnection
        :type hook: cloudbot.core.pluginmanager.Hook
        :type base_event: cloudbot.core.events.BaseEvent
        :type irc_raw: str
        :type irc_prefix: str
        :type irc_command: str
        :type irc_paramlist: list[str]
        :type irc_message: str
        :type nick: str
        :type user: str
        :type host: str
        :type mask: str
        """
        self.bot = bot
        self.conn = conn
        self.hook = hook
        if base_event is not None:
            # We're copying an event
            if self.bot is None and base_event.bot is not None:
                self.bot = base_event.bot
            if self.conn is None and base_event.conn is not None:
                self.conn = base_event.conn
            if self.hook is None and base_event.hook is not None:
                self.hook = base_event.hook
            self.irc_raw = base_event.irc_raw
            self.irc_prefix = base_event.irc_prefix
            self.irc_command = base_event.irc_command
            self.irc_paramlist = base_event.irc_paramlist
            self.irc_message = base_event.irc_message
            self.nick = base_event.nick
            self.user = base_event.user
            self.host = base_event.host
            self.mask = base_event.mask
        else:
            self.irc_raw = irc_raw
            self.irc_prefix = irc_prefix
            self.irc_command = irc_command
            self.irc_paramlist = irc_paramlist
            self.irc_message = irc_message
            self.nick = nick
            self.user = user
            self.host = host
            self.mask = mask

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
        if self.irc_paramlist:
            if self.irc_paramlist[0].lower() == self.conn.nick.lower():
                # this is a private message - set the nick to the sender's nick
                return self.nick.lower()
            else:
                return self.irc_paramlist[0].lower()
        else:
            return None

    @property
    def event(self):
        """
        :rtype; cloudbot.core.events.BaseEvent
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


class CommandEvent(BaseEvent):
    """
    :type hook: cloudbot.core.pluginmanager.CommandHook
    :type text: str
    :type triggered_command: str
    """

    def __init__(self, bot=None, conn=None, text=None, triggered_command=None, hook=None, base_event=None, irc_raw=None,
                 irc_prefix=None, irc_command=None, irc_paramlist=None, irc_message=None, nick=None, user=None,
                 host=None, mask=None):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type conn: cloudbot.core.irc.BotConnection
        :type hook: cloudbot.core.pluginmanager.CommandHook
        :type text: str
        :type triggered_command: str
        :type base_event: cloudbot.core.events.BaseEvent
        :type irc_raw: str
        :type irc_prefix: str
        :type irc_command: str
        :type irc_paramlist: list[str]
        :type irc_message: str
        :type nick: str
        :type user: str
        :type host: str
        :type mask: str
        """
        super().__init__(bot=bot, conn=conn, hook=hook, base_event=base_event, irc_raw=irc_raw, irc_prefix=irc_prefix,
                         irc_command=irc_command, irc_paramlist=irc_paramlist, irc_message=irc_message, nick=nick,
                         user=user, host=host, mask=mask)
        self.hook = hook
        self.text = text
        self.triggered_command = triggered_command

    def notice_doc(self, target=None):
        """sends a notice containing this command's docstring to the current channel/user or a specific channel/user
        :type target: str
        """
        if self.triggered_command is None:
            raise ValueError("Triggered command not set on this event")
        if self.hook.doc is None:
            message = "{}{} requires additional arguments.".format(self.conn.config["command_prefix"],
                                                                   self.triggered_command)
        else:
            message = "{}{} {}".format(self.conn.config["command_prefix"], self.triggered_command, self.hook.doc)
        self.notice(message, target=target)


class RegexEvent(BaseEvent):
    """
    :type hook: cloudbot.core.pluginmanager.RegexHook
    :type match: re.__Match
    """

    def __init__(self, bot=None, conn=None, match=None, hook=None, base_event=None, irc_raw=None,
                 irc_prefix=None, irc_command=None, irc_paramlist=None, irc_message=None, nick=None, user=None,
                 host=None, mask=None):
        """
        :type bot: cloudbot.core.bot.CloudBot
        :type conn: cloudbot.core.irc.BotConnection
        :type hook: cloudbot.core.pluginmanager.RegexHook
        :type match: re.__Match
        :type base_event: cloudbot.core.events.BaseEvent
        :type irc_raw: str
        :type irc_prefix: str
        :type irc_command: str
        :type irc_paramlist: list[str]
        :type irc_message: str
        :type nick: str
        :type user: str
        :type host: str
        :type mask: str
        """
        super().__init__(bot=bot, conn=conn, hook=hook, base_event=base_event, irc_raw=irc_raw, irc_prefix=irc_prefix,
                         irc_command=irc_command, irc_paramlist=irc_paramlist, irc_message=irc_message, nick=nick,
                         user=user, host=host, mask=mask)
        self.match = match
