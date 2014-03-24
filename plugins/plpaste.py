from util import hook, web
from os import listdir


@hook.command(adminonly=True)
def plpaste(inp, bot=None):
    if inp in bot.commands:
        with open(bot.commands[inp][0].func_code.co_filename.strip()) as f:
            return web.haste(f.read(), ext='py')
    elif inp + ".py" in listdir('plugins/'):
        with open('plugins/{}.py'.format(inp)) as f:
            return web.haste(f.read(), ext='py')
    else:
        return "Could not find specified plugin."
