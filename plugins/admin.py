import re

from util import hook


@hook.command("groups", permissions=["permissions_users"], autohelp=False)
@hook.command("listgroups", permissions=["permissions_users"], autohelp=False)
@hook.command("permgroups", permissions=["permissions_users"], autohelp=False)
def get_permission_groups(inp, conn=None):
    """groups -- lists all valid groups
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    return "Valid groups: {}".format(conn.permissions.get_groups())


@hook.command("gperms", permissions=["permissions_users"])
def get_group_permissions(inp, conn=None, notice=None):
    """gperms <group> -- lists permissions of a group
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    group = inp.strip().lower()
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
def get_group_users(inp, conn=None, notice=None):
    """gusers <group> -- lists users in a group
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    group = inp.strip().lower()
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
def get_user_permissions(inp, conn=None, has_permission=None, notice=None, mask=None):
    """uperms [user] -- lists all permissions given to a user, or the current user if none is given
    :type inp: str
    :type conn: core.irc.BotConnection
    :type mask: str
    """
    if inp:
        if not has_permission("permissions_users"):
            notice("Sorry, you are not allowed to use this command on another user")
            return
        user = inp.strip().lower()
    else:
        user = mask.lower()

    permission_manager = conn.permissions

    user_permissions = permission_manager.get_user_permissions(user)
    if user_permissions:
        return "User {} has permissions: {}".format(user, user_permissions)
    else:
        return "User {} has no elevated permissions".format(user)


@hook.command("ugroups", autohelp=False)
def get_user_groups(inp, conn=None, has_permission=None, notice=None, mask=None):
    """uperms [user] -- lists all permissions given to a user, or the current user if none is given
    :type inp: str
    :type conn: core.irc.BotConnection
    :type mask: str
    """
    if inp:
        if not has_permission("permissions_users"):
            notice("Sorry, you are not allowed to use this command on another user")
            return
        user = inp.strip().lower()
    else:
        user = mask.lower()

    permission_manager = conn.permissions

    user_permissions = permission_manager.get_user_permissions(user)
    if user_permissions:
        return "User {} has permissions: {}".format(user, user_permissions)
    else:
        return "User {} has no elevated permissions".format(user)


@hook.command("deluser", permissions=["permissions_users"])
def remove_permission_user(inp, bot=None, conn=None, notice=None, reply=None):
    """deluser <user> [group] -- Removes a user from a permission group, or all permission groups if none is specified
    :type inp: str
    :type bot: core.bot.CloudBot
    :type conn: core.irc.BotConnection
    """
    split = inp.split()
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
def add_permissions_user(inp, conn=None, bot=None, notice=None, reply=None):
    """adduser <user> <group> -- Adds a user to a permission group
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    split = inp.split()
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


@hook.command(permissions=["botcontrol"], autohelp=False)
@hook.command("quit", permissions=["botcontrol"], autohelp=False)
def stop(inp, bot=None):
    """stop [reason] -- Stops the bot with [reason] as its quit message.
    :type inp: str
    :type bot: core.bot.CloudBot
    """
    if inp:
        bot.stop(reason=inp)
    else:
        bot.stop()


@hook.command(permissions=["botcontrol"], autohelp=False)
def restart(inp, bot=None):
    """restart [reason] -- Restarts the bot with [reason] as its quit message.
    :type inp: str
    :type bot: core.bot.CloudBot
    """
    if inp:
        bot.restart(reason=inp)
    else:
        bot.restart()


@hook.command(permissions=["botcontrol"])
def join(inp, conn=None, notice=None):
    """join <channel> -- Joins a given channel
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    for target in inp.split():
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to join {}...".format(target))
        conn.join(target)


@hook.command(permissions=["botcontrol"], autohelp=False)
def part(inp, conn=None, chan=None, notice=None):
    """part [channel] -- Leaves a given channel, or the current one if no channel is specified
    :type inp: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    if inp:
        targets = inp
    else:
        targets = chan
    for target in targets.split():
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to leave {}...".format(target))
        conn.part(target)


@hook.command(autohelp=False, permissions=["botcontrol"])
def cycle(inp, conn=None, chan=None, notice=None):
    """cycle <channel> -- Cycles a given channel, or the current one if no channel is specified
    :type inp: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    if inp:
        targets = inp
    else:
        targets = chan
    for target in targets.split():
        if not target.startswith("#"):
            target = "#{}".format(target)
        notice("Attempting to cycle {}...".format(target))
        conn.part(target)
        conn.join(target)


@hook.command(permissions=["botcontrol"])
def nick(inp, conn=None, notice=None):
    """nick <nick> -- Changes the bot's nickname
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    if not re.match("^[a-z0-9_|.-\]\[]*$", inp.lower()):
        notice("Invalid username '{}'".format(inp))
        return
    notice("Attempting to change nick to '{}'...".format(inp))
    conn.set_nick(inp)


@hook.command(permissions=["botcontrol"])
def raw(inp, conn=None, notice=None):
    """raw <command> -- Sends a raw IRC command
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    notice("Raw command sent.")
    conn.send(inp)


@hook.command(permissions=["botcontrol"])
def say(inp, conn=None, chan=None):
    """say [channel] <message> -- Makes the bot say <message> in [channel], or the current channel if none is specified
    :type inp: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    inp = inp.strip()
    if inp.startswith("#"):
        split = inp.split(None, 1)
        channel = split[0]
        text = split[1]
    else:
        channel = chan
        text = inp
    conn.msg(channel, text)


@hook.command(permissions=["botcontrol"])
def message(inp, conn=None):
    """message <name> <message> -- Makes the bot say <message> to <name>, <name> may be a #channel or a nickname
    :type inp: str
    :type conn: core.irc.BotConnection
    """
    split = inp.split(None, 1)
    channel = split[0]
    text = split[1]
    conn.msg(channel, text)


@hook.command("act", permissions=["botcontrol"])
@hook.command(permissions=["botcontrol"])
def me(inp, conn=None, chan=None):
    """me [channel] <action> -- Makes the bot act out <action> in a [channel], or the current channel if none is given
    :type inp: str
    :type conn: core.irc.BotConnection
    :type chan: str
    """
    inp = inp.strip()
    if inp.startswith("#"):
        split = inp.split(None, 1)
        channel = split[0]
        text = split[1]
    else:
        channel = chan
        text = inp
    conn.ctcp(channel, "ACTION", text)
