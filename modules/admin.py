import re

from cloudbot import hook


@hook.command(["groups", "listgroups", "permgroups"], permissions=["permissions_users"], autohelp=False)
def get_permission_groups(conn):
    """groups -- lists all valid groups
    :type conn: core.irc.BotConnection
    """
    return "Valid groups: {}".format(conn.permissions.get_groups())


@hook.command("gperms", permissions=["permissions_users"])
def get_group_permissions(text, conn, notice):
    """gperms <group> -- lists permissions of a group
    :type text: str
    :type conn: core.irc.BotConnection
    """
    group = text.strip().lower()
    permission_manager = conn.permissions
    group_users = permission_manager.get_group_users(group)
    group_permissions = permission_manager.get_group_permissions(group)
    if group_permissions:
        return "Group {} has permissions {}".format(group, group_permissions)
    elif group_users:
        return "Group {} exists, but has no permissions".format(group)
    else:
        notice("Unknown group '{}'".format(group))


@hook.command("gusers", permissions=["permissions_users"])
def get_group_users(text, conn, notice):
    """gusers <group> -- lists users in a group
    :type text: str
    :type conn: core.irc.BotConnection
    """
    group = text.strip().lower()
    permission_manager = conn.permissions
    group_users = permission_manager.get_group_users(group)
    group_permissions = permission_manager.get_group_permissions(group)
    if group_users:
        return "Group {} has members: {}".format(group, group_users)
    elif group_permissions:
        return "Group {} exists, but has no members".format(group, group_permissions)
    else:
        notice("Unknown group '{}'".format(group))


@hook.command("uperms", autohelp=False)
def get_user_permissions(text, conn, mask, has_permission, notice):
    """uperms [user] -- lists all permissions given to a user, or the current user if none is given
    :type text: str
    :type conn: core.irc.BotConnection
    :type mask: str
    """
    if text:
        if not has_permission("permissions_users"):
            notice("Sorry, you are not allowed to use this command on another user")
            return
        user = text.strip().lower()
    else:
        user = mask.lower()

    permission_manager = conn.permissions

    user_permissions = permission_manager.get_user_permissions(user)
    if user_permissions:
        return "User {} has permissions: {}".format(user, user_permissions)
    else:
        return "User {} has no elevated permissions".format(user)


@hook.command("ugroups", autohelp=False)
def get_user_groups(text, conn, mask, has_permission, notice):
    """uperms [user] -- lists all permissions given to a user, or the current user if none is given
    :type text: str
    :type conn: core.irc.BotConnection
    :type mask: str
    """
    if text:
        if not has_permission("permissions_users"):
            notice("Sorry, you are not allowed to use this command on another user")
            return
        user = text.strip().lower()
    else:
        user = mask.lower()

    permission_manager = conn.permissions

    user_groups = permission_manager.get_user_groups(user)
    if user_groups:
        return "User {} is in groups: {}".format(user, user_groups)
    else:
        return "User {} is in no permission groups".format(user)


@hook.command("deluser", permissions=["permissions_users"])
def remove_permission_user(text, bot, conn, notice, reply):
    """deluser <user> [group] -- Removes a user from a permission group, or all permission groups if none is specified
    :type text: str
    :type bot: core.bot.CloudBot
    :type conn: core.irc.BotConnection
    """
    split = text.split()
    if len(split) > 2:
        notice("Too many arguments")
        return
    elif len(split) < 1:
        notice("Not enough arguments")
        return

    if len(split) > 1:
        user = split[0].lower()
        group = split[1].lower()
    else:
        user = split[0].lower()
        group = None

    permission_manager = conn.permissions
    changed = False
    if group is not None:
        if not permission_manager.group_exists(group):
            notice("Unknown group '{}'".format(group))
            return
        changed_masks = permission_manager.remove_group_user(group, user)
        if changed_masks:
            changed = True
        if len(changed_masks) > 1:
            reply("Removed {} and {} from {}".format(", ".join(changed_masks[:-1]), changed_masks[-1], group))
        elif changed_masks:
            reply("Removed {} from {}".format(changed_masks[0], group))
        else:
            reply("No masks in {} matched {}".format(group, user))
    else:
        groups = permission_manager.get_user_groups(user)
        for group in groups:
            changed_masks = permission_manager.remove_group_user(group, user)
            if changed_masks:
                changed = True
            if len(changed_masks) > 1:
                reply("Removed {} and {} from {}".format(", ".join(changed_masks[:-1]), changed_masks[-1], group))
            elif changed_masks:
                reply("Removed {} from {}".format(changed_masks[0], group))
        if not changed:
            reply("No masks with elevated permissions matched {}".format(group, user))

    if changed:
        bot.config.save_config()
        permission_manager.reload()


@hook.command("adduser", permissions=["permissions_users"])
def add_permissions_user(text, conn, bot, notice, reply):
    """adduser <user> <group> -- Adds a user to a permission group
    :type text: str
    :type conn: core.irc.BotConnection
    :type bot: core.bot.CloudBot
    """
    split = text.split()
    if len(split) > 2:
        notice("Too many arguments")
        return
    elif len(split) < 2:
        notice("Not enough arguments")
        return

    user = split[0].lower()
    group = split[1].lower()

    if not re.search('.+!.+@.+', user):
        # TODO: When we have presence tracking, check if there are any users in the channel with the nick given
        notice("The user must be in the format 'nick!user@host'")
        return

    permission_manager = conn.permissions

    group_exists = permission_manager.group_exists(group)

    changed = permission_manager.add_user_to_group(user, group)

    if not changed:
        reply("User {} is already matched in group {}".format(user, group))
    elif group_exists:
        reply("User {} added to group {}".format(user, group))
    else:
        reply("Group {} created with user {}".format(group, user))

    if changed:
        bot.config.save_config()
        permission_manager.reload()


@hook.command(["stop", "quit"], permissions=["botcontrol"], autohelp=False)
def stop(text, bot):
    """stop [reason] -- Stops the bot with [reason] as its quit message.
    :type text: str
    :type bot: core.bot.CloudBot
    """
    if text:
        bot.stop(reason=text)
    else:
        bot.stop()


@hook.command(permissions=["botcontrol"], autohelp=False)
def restart(text, bot):
    """restart [reason] -- Restarts the bot with [reason] as its quit message.
    :type text: str
    :type bot: core.bot.CloudBot
    """
    if text:
        bot.restart(reason=text)
    else:
        bot.restart()


@hook.command(permissions=["botcontrol"])
def join(text, conn, notice):
    """join <channel> -- Joins a given channel
    :type text: str
    :type conn: core.irc.BotConnection
    """
    for target in text.split():
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to join {}...".format(target))
        conn.join(target)


@hook.command(permissions=["botcontrol"], autohelp=False)
def part(text, conn, chan, notice):
    """part [channel] -- Leaves a given channel, or the current one if no channel is specified
    :type text: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    if text:
        targets = text
    else:
        targets = chan
    for target in targets.split():
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to leave {}...".format(target))
        conn.part(target)


@hook.command(autohelp=False, permissions=["botcontrol"])
def cycle(text, conn, chan, notice):
    """cycle <channel> -- Cycles a given channel, or the current one if no channel is specified
    :type text: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    if text:
        targets = text
    else:
        targets = chan
    for target in targets.split():
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to cycle {}...".format(target))
        conn.part(target)
        conn.join(target)


@hook.command(permissions=["botcontrol"])
def nick(text, conn, notice):
    """nick <nick> -- Changes the bot's nickname
    :type text: str
    :type conn: core.irc.BotConnection
    """
    if not re.match("^[a-z0-9_|.-\]\[]*$", text.lower()):
        notice("Invalid username '{}'".format(text))
        return
    notice("Attempting to change nick to '{}'...".format(text))
    conn.set_nick(text)


@hook.command(permissions=["botcontrol"])
def raw(text, conn, notice):
    """raw <command> -- Sends a irc_raw IRC command
    :type text: str
    :type conn: core.irc.BotConnection
    """
    notice("Raw command sent.")
    conn.send(text)


@hook.command(permissions=["botcontrol"])
def say(text, conn, chan):
    """say [channel] <message> -- Makes the bot say <message> in [channel], or the current channel if none is specified
    :type text: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    text = text.strip()
    if text.startswith("#"):
        split = text.split(None, 1)
        channel = split[0]
        text = split[1]
    else:
        channel = chan
        text = text
    conn.msg(channel, text)


@hook.command(permissions=["botcontrol"])
def message(text, conn):
    """message <name> <message> -- Makes the bot say <message> to <name>, <name> may be a #channel or a nickname
    :type text: str
    :type conn: core.irc.BotConnection
    """
    split = text.split(None, 1)
    channel = split[0]
    text = split[1]
    conn.msg(channel, text)


@hook.command("act", permissions=["botcontrol"])
@hook.command(permissions=["botcontrol"])
def me(text, conn, chan):
    """me [channel] <action> -- Makes the bot act out <action> in a [channel], or the current channel if none is given
    :type text: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    text = text.strip()
    if text.startswith("#"):
        split = text.split(None, 1)
        channel = split[0]
        text = split[1]
    else:
        channel = chan
        text = text
    conn.ctcp(channel, "ACTION", text)
