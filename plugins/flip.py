import random

from cloudbot import hook
from cloudbot.util import formatting

USE_FLIPPERS = False

replacements = {
    'a': 'ɐ',
    'b': 'q',
    'c': 'ɔ',
    'd': 'p',
    'e': 'ǝ',
    'f': 'ɟ',
    'g': 'b',
    'h': 'ɥ',
    'i': 'ı',
    'j': 'ظ',
    'k': 'ʞ',
    'l': 'ן',
    'm': 'ɯ',
    'n': 'u',
    'o': 'o',
    'p': 'd',
    'q': 'b',
    'r': 'ɹ',
    's': 's',
    't': 'ʇ',
    'u': 'n',
    'v': 'ʌ',
    'w': 'ʍ',
    'x': 'x',
    'y': 'ʎ',
    'z': 'z',
    '?': '¿',
    '.': '˙',
    '/': '\\',
    '\\': '/',
    '(': ')',
    ')': '(',
    '<': '>',
    '>': '<',
    '[': ']',
    ']': '[',
    '{': '}',
    '}': '{',
    '\'': ',',
    '_': '‾'}

flippers = ["( ﾉ⊙︵⊙）ﾉ", "(╯°□°）╯", "( ﾉ♉︵♉ ）ﾉ"]

@hook.command
def flip(text, message, reply):
    """<text> -- Flips <text> over."""
    if USE_FLIPPERS:
        message(random.choice(flippers) + " ︵ " + formatting.multi_replace(text[::-1], replacements))
    else:
        reply(formatting.multi_replace(text[::-1], replacements))


@hook.command
def table(text, message):
    """<text> -- (╯°□°）╯︵ <ʇxǝʇ>"""
    message(random.choice(flippers) + " ︵ " + formatting.multi_replace(text[::-1], replacements))


