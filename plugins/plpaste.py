import os
from util import hook, web
from os import listdir


@hook.command(permissions=["adminonly"])
def plpaste(inp, bot=None):
    if inp in bot.commands:
        with open(os.path.join("plugins", bot.commands[inp][0].__code__.co_filename.strip())) as f:
            return web.haste(f.read(), ext='py')
    elif inp + ".py" in listdir('plugins/'):
        with open('plugins/{}.py'.format(inp)) as f:
            return web.haste(f.read(), ext='py')
    else:
        return "Could not find specified plugin."
