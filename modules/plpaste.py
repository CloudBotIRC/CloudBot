from os import listdir

from util import hook, web


@hook.command(permissions=["adminonly"])
def plpaste(text, bot):
    """
    :type text: str
    :type bot: core.bot.CloudBot
    """
    if text in bot.plugin_manager.commands:
        file_path = bot.plugin_manager.commands[text].module.file_path
        with open(file_path) as f:
            return web.haste(f.read(), ext='py')
    elif text + ".py" in listdir('modules/'):
        with open('modules/{}.py'.format(text)) as f:
            return web.haste(f.read(), ext='py')
    else:
        return "Could not find specified plugin."
