from fnmatch import fnmatch


class PermissionManager(object):
    def __init__(self, bot, conn):

        # this is all legacy code, needs to be redone with classes and whatnot
        self.logger = bot.logger

        self.logger.info("Creating simple permission manager for {}.".format(conn.name))

        # stuff
        self.bot = bot
        self.conn = conn
        self.config = conn.config

        self.group_perms = {}
        self.group_users = {}
        self.perm_users = {}

        self.reload()

    def reload(self):
        self.logger.info("Reloading permissions for {}.".format(self.conn.name))
        groups = self.conn.config.get("permissions", [])
        # work out the permissions and users each group has
        for key, value in groups.items():
            self.group_perms[key] = []
            self.group_users[key] = []
            for permission in value["perms"]:
                self.group_perms[key].append(permission)
            for user in value["users"]:
                self.group_users[key].append(user)

        for group, users in self.group_users.items():
            group_perms = self.group_perms[group]
            for perm in group_perms:
                self.perm_users[perm] = []
                self.perm_users[perm] = users

    def has_perm_mask(self, mask, perm):

        allowed_users = self.perm_users[perm]

        for pattern in allowed_users:
            if fnmatch(mask.lower(), pattern.lower()):
                return input

