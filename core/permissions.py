class PermissionManager(object):
    def __init__(self, bot, conn):
        self.logger = bot.logger

        self.logger.info("Creating permission manager for {}.".format(conn.name))

        # stuff
        self.bot = bot
        self.conn = conn
        self.config = conn.config

        self.group_perms = {}

        self.reload()

    def reload(self):
        self.logger.error("reload perms stub")
        pass