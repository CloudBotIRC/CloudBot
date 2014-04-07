from fnmatch import fnmatch


class PermissionManager(object):
    """
    :type logger: logging.Logger
    :type bot: core.bot.CloudBot
    :type name: str
    :type config: dict[str, ?]
    :type group_perms: dict[str, list[str]]
    :type group_users: dict[str, list[str]]
    :type perm_users: dict[str, list[str]]
    """
    def __init__(self, bot, conn):
        """
        :type bot: core.bot.CloudBot
        :type conn: core.irc.BotConnection
        """
        self.logger = bot.logger

        self.logger.info("Created permission manager for {}.".format(conn.name))

        # stuff
        self.bot = bot
        self.name = conn.name
        self.config = conn.config

        self.group_perms = {}
        self.group_users = {}
        self.perm_users = {}

        self.reload()

    def reload(self):
        self.logger.info("Reloading permissions for {}.".format(self.name))
        groups = self.config.get("permissions", {})
        # work out the permissions and users each group has
        for key, value in groups.items():
            key = key.lower()
            self.group_perms[key] = []
            self.group_users[key] = []
            for permission in value["perms"]:
                self.group_perms[key].append(permission.lower())
            for user in value["users"]:
                self.group_users[key].append(user.lower())

        for group, users in self.group_users.items():
            group_perms = self.group_perms[group]
            for perm in group_perms:
                if self.perm_users.get(perm) is None:
                    self.perm_users[perm] = []
                self.perm_users[perm].extend(users)

        self.logger.debug("Group permissions for {}: {}".format(self.name, self.group_perms))
        self.logger.debug("Group users for {}: {}".format(self.name, self.group_users))
        self.logger.debug("Permission users for {}: {}".format(self.name, self.perm_users))

    def has_perm_mask(self, user_mask, perm):
        """
        :type user_mask: str
        :type perm: str
        :rtype: bool
        """
        allowed_users = self.perm_users[perm.lower()]

        for allowed_mask in allowed_users:
            if fnmatch(user_mask.lower(), allowed_mask):
                self.logger.info("Allowed user {} access to {}".format(user_mask, perm))
                return True

        return False

    def get_group_permissions(self, group):
        """
        :type group: str
        :rtype: list[str]
        """
        return self.group_perms.get(group.lower())

    def get_group_users(self, group):
        """
        :type group: str
        :rtype: list[str]
        """
        return self.group_users.get(group.lower())

    def get_user_permissions(self, user_mask):
        """
        :type user_mask: str
        :rtype: list[str]
        """
        permissions = []
        for permission, users in self.perm_users.items():
            for mask_to_check in users:
                if fnmatch(user_mask.lower(), mask_to_check):
                    permissions.append(permission)
        return permissions
