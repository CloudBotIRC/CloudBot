from util import hook


@hook.command
def dbtest(db):
    print(db)