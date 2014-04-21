import os
from os import listdir

from util import hook, web


@hook.command(permissions=["adminonly"])
def plpaste(inp, bot=None):
    if inp in bot.commands:
        with open(os.path.join("modules", bot.commands[inp][0].__code__.co_filename.strip())) as f:
            return web.haste(f.read(), ext='py')
    elif inp + ".py" in listdir('modules/'):
        with open('modules/{}.py'.format(inp)) as f:
            return web.haste(f.read(), ext='py')
    else:
        return "Could not find specified plugin."
