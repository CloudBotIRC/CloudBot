from cloudbot import hook
import random

lennyface = [u'( \u0361\u00B0 \u035C\u0296 \u0361\u00B0)', u'( \u0360\u00B0 \u035F\u0296 \u0361\u00B0)', u'\u1566( \u0361\xb0 \u035c\u0296 \u0361\xb0)\u1564', u'( \u0361\u00B0 \u035C\u0296 \u0361\u00B0)', u'( \u0361~ \u035C\u0296 \u0361\u00B0)', u'( \u0361o \u035C\u0296 \u0361o)', u'\u0361\u00B0 \u035C\u0296 \u0361 -', u'( \u0361\u0361 \u00B0 \u035C \u0296 \u0361 \u00B0)\uFEFF', u'( \u0361 \u0361\u00B0 \u0361\u00B0  \u0296 \u0361\u00B0 \u0361\u00B0)', u'(\u0E07 \u0360\u00B0 \u035F\u0644\u035C \u0361\u00B0)\u0E07', u'( \u0361\u00B0 \u035C\u0296 \u0361 \u00B0)', u'( \u0361\u00B0\u256D\u035C\u0296\u256E\u0361\u00B0 )']

flennyface = [ '(    \u0361\xb0 \u035c  \u0361\xb0    )', '( \u0361\xb0                  \u035c                      \u0361\xb0 )', '(\u0e07     \u0360\xb0 \u035f   \u0361\xb0    )\u0e07', '(    \u0361\xb0_ \u0361\xb0    )', '(\ufffd    \u0361\xb0 \u035c  \u0361\xb0    )\ufffd', '(   \u25d5  \u035c  \u25d5   )', '(   \u0361~  \u035c   \u0361\xb0   )', '(    \u0360\xb0 \u035f   \u0361\xb0    )', '(   \u0ca0  \u035c  \u0ca0   )', '(    \u0ca5  \u035c  \u0ca5    )', '(    \u0361^ \u035c  \u0361^    )', '(    \u0ca5 _  \u0ca5    )', '(    \u0361\xb0 \uff0d \u0361\xb0    )', '\u2570(      \u0361\xb0  \u035c   \u0361\xb0)\u2283\u2501\u2606\u309c\u30fb\u3002\u3002\u30fb\u309c\u309c\u30fb\u3002\u3002\u30fb\u309c\u2606\u309c\u30fb\u3002\u3002\u30fb\u309c\u309c\u30fb\u3002\u3002\u30fb\u309c', '\u2534\u252c\u2534\u252c\u2534\u2524(    \u0361\xb0 \u035c  \u251c\u252c\u2534\u252c\u2534\u252c', '(    \u2310\u25a0 \u035c   \u25a0  )', '(    \u0361~ _ \u0361~    )', '@=(   \u0361\xb0 \u035c  \u0361\xb0  @ )\u2261', '(    \u0361\xb0\u06a1 \u0361\xb0    )', '(  \u2716_\u2716  )', '(\u3065    \u0361\xb0 \u035c  \u0361\xb0    )\u3065', '\u10da(   \u0361\xb0 \u035c  \u0361\xb0   \u10da)', '(    \u25c9 \u035c  \u0361\u25d4    )' ]

@hook.command(autohelp=False)
def lenny(message, conn):
    """why the shit not lennyface"""
    message(random.choice(lennyface))

@hook.command(autohelp=False)
def flenny(message):
    """flenny is watching."""
    message(random.choice(flennyface))
