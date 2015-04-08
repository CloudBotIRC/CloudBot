from cloudbot import hook
import random

lennyface = [u'( \u0361\u00B0 \u035C\u0296 \u0361\u00B0)', u'( \u0360\u00B0 \u035F\u0296 \u0361\u00B0)', u'\u1566( \u0361\xb0 \u035c\u0296 \u0361\xb0)\u1564', u'( \u0361\u00B0 \u035C\u0296 \u0361\u00B0)', u'( \u0361~ \u035C\u0296 \u0361\u00B0)', u'( \u0361o \u035C\u0296 \u0361o)', u'\u0361\u00B0 \u035C\u0296 \u0361 -', u'( \u0361\u0361 \u00B0 \u035C \u0296 \u0361 \u00B0)\uFEFF', u'( \u0361 \u0361\u00B0 \u0361\u00B0  \u0296 \u0361\u00B0 \u0361\u00B0)', u'(\u0E07 \u0360\u00B0 \u035F\u0644\u035C \u0361\u00B0)\u0E07', u'( \u0361\u00B0 \u035C\u0296 \u0361 \u00B0)', u'( \u0361\u00B0\u256D\u035C\u0296\u256E\u0361\u00B0 )']

@hook.command(autohelp=False)
def lenny(message, conn):
    """why the shit not lennyface"""
    message(random.choice(lennyface))
