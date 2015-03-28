import random

from cloudbot import hook
from cloudbot.util import formatting

USE_FLIPPERS = True

replacements = {
    'a': 'ɐ',
    'b': 'q',
    'c': 'ɔ',
    'd': 'p',
    'e': 'ǝ',
    'f': 'ɟ',
    'g': 'ƃ',
    'h': 'ɥ',
    'i': 'ᴉ',
    'j': 'ɾ',
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
    ',': '\'',
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

# append an inverted form of replacements to itself, so flipping works both ways
replacements.update(dict((v, k) for k, v in replacements.items()))

flippers = ["( ﾉ⊙︵⊙）ﾉ", "(╯°□°）╯", "( ﾉ♉︵♉ ）ﾉ"]

@hook.command
def flip(text, reply, message):
    """<text> -- Flips <text> over."""
    if USE_FLIPPERS:
        if text in ['table','tables']:
             message(random.choice(flippers) + " ︵ " + "\u253B\u2501\u253B")
        else:
             message(random.choice(flippers) + " ︵ " + formatting.multi_replace(text[::-1], replacements))
    else:
        reply(formatting.multi_replace(text[::-1], replacements))


@hook.command
def table(text, message):
    """<text> -- (╯°□°）╯︵ <ʇxǝʇ>"""
    message(random.choice(flippers) + " ︵ " + formatting.multi_replace(text[::-1].lower(), replacements))
