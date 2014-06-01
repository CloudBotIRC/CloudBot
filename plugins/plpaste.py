from os import listdir

from cloudbot import hook, web


@hook.command(permissions=["adminonly"])
def plpaste(text, bot):
    """
    :type text: str
    :type bot: core.bot.CloudBot
    """
    if text in bot.plugin_manager.commands:
        file_path = bot.plugin_manager.commands[text].plugin.file_path
        with open(file_path) as f:
            return web.paste(f.read(), 'py')
    elif text + ".py" in listdir('plugins/'):
        with open('plugins/{}.py'.format(text)) as f:
            return web.paste(f.read(), 'py')
    else:
        return "Could not find specified plugin."
