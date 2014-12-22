from fnmatch import fnmatch
import logging

logger = logging.getLogger("cloudbot")


class PermissionManager(object):
    """
    :type connection_name: str
    :type config: dict[str, ?]
    :type group_perms: dict[str, list[str]]
    :type group_users: dict[str, list[str]]
    :type perm_users: dict[str, list[str]]
    """

    def __init__(self, conn):
        """
        :type conn: cloudbot.client.Client
        """
        logger.info("[{}] Created permission manager for {}.".format(conn.name, conn.name))

        # stuff
        self.connection_name = conn.name
        self.config = conn.config

        self.group_perms = {}
        self.group_users = {}
        self.perm_users = {}

        self.reload()

    def reload(self):
        self.group_perms = {}
        self.group_users = {}
        self.perm_users = {}
        logger.info("[{}] Reloading permissions for {}.".format(self.connection_name, self.connection_name))
        groups = self.config.get("permissions", {})
        # work out the permissions and users each group has
        for key, value in groups.items():
            if not key.islower():
                logger.warning("[{}] Warning! Non-lower-case group '{}' in config. This will cause problems when"
                               "setting permissions using the bot's permissions commands"
                               .format(self.connection_name, key))
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

        logger.debug("[{}] Group permissions: {}".format(self.connection_name, self.group_perms))
        logger.debug("[{}] Group users: {}".format(self.connection_name, self.group_users))
        logger.debug("[{}] Permission users: {}".format(self.connection_name, self.perm_users))

    def has_perm_mask(self, user_mask, perm, notice=True):
        """
        :type user_mask: str
        :type perm: str
        :rtype: bool
        """

        if not perm.lower() in self.perm_users:
            # no one has access
            return False

        allowed_users = self.perm_users[perm.lower()]

        for allowed_mask in allowed_users:
            if fnmatch(user_mask.lower(), allowed_mask):
                if notice:
                    logger.info("[{}] Allowed user {} access to {}".format(self.connection_name, user_mask, perm))
                return True

        return False

    def get_groups(self):
        return set().union(self.group_perms.keys(), self.group_users.keys())

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
        permissions = set()
        for permission, users in self.perm_users.items():
            for mask_to_check in users:
                if fnmatch(user_mask.lower(), mask_to_check):
                    permissions.add(permission)
        return permissions

    def get_user_groups(self, user_mask):
        """
        :type user_mask: str
        :rtype: list[str]
        """
        groups = []
        for group, users in self.group_users.items():
            for mask_to_check in users:
                if fnmatch(user_mask.lower(), mask_to_check):
                    groups.append(group)
                    continue
        return groups

    def group_exists(self, group):
        """
        Checks whether a group exists
        :type group: str
        :rtype: bool
        """
        return group.lower() in self.group_perms

    def user_in_group(self, user_mask, group):
        """
        Checks whether a user is matched by any masks in a given group
        :type group: str
        :type user_mask: str
        :rtype: bool
        """
        users = self.group_users.get(group.lower())
        if not users:
            return False
        for mask_to_check in users:
            if fnmatch(user_mask.lower(), mask_to_check):
                return True
        return False

    def remove_group_user(self, group, user_mask):
        """
        Removes all users that match user_mask from group. Returns a list of user masks removed from the group.
        Use permission_manager.reload() to make this change take affect.
        Use bot.config.save_config() to save this change to file.
        :type group: str
        :type user_mask: str
        :rtype: list[str]
        """
        masks_removed = []

        config_groups = self.config.get("permissions", {})

        for mask_to_check in list(self.group_users[group.lower()]):
            if fnmatch(user_mask.lower(), mask_to_check):
                masks_removed.append(mask_to_check)
                # We're going to act like the group keys are all lowercase.
                # The user has been warned (above) if they aren't.
                # Okay, maybe a warning, but no support.
                if group not in config_groups:
                    logger.warning(
                        "[{}] Can't remove user from group due to upper-case group names!".format(self.connection_name))
                    continue
                config_group = config_groups.get(group)
                config_users = config_group.get("users")
                config_users.remove(mask_to_check)

        return masks_removed

    def add_user_to_group(self, user_mask, group):
        """
        Adds user to group. Returns whether this actually did anything.
        Use permission_manager.reload() to make this change take affect.
        Use bot.config.save_config() to save this change to file.
        :type group: str
        :type user_mask: str
        :rtype: bool
        """
        if self.user_in_group(user_mask, group):
            return False
        # We're going to act like the group keys are all lowercase.
        # The user has been warned (above) if they aren't.
        groups = self.config.get("permissions", {})
        if group in groups:
            group_dict = groups.get(group)
            users = group_dict["users"]
            users.append(user_mask)
        else:
            # create the group
            group_dict = {"users": [user_mask], "perms": []}
            groups[group] = group_dict

        return True
