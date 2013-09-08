from util import hook, web


@hook.command(adminonly=True)
def plpaste(inp):
    if "/" in inp and inp.split("/")[0] != "util":
        return "Invalid input"
    try:
        with open("plugins/%s.py" % inp) as f:
            return web.haste(f.read(), ext='py')
    except IOError:
        return "Plugin not found (must be in plugins folder)"
