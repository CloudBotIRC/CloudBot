from util import hook


@hook.command
def dbtest(inp, db=None):
    print(db)