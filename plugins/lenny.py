from cloudbot import hook

@hook.command(autohelp=False)
def lenny(text, message):
    """why the shit not lennyface"""
    message(u'(\u0361\xb0 \u035c\u0296 \u0361\xb0)')
