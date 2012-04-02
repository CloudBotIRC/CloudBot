from util import hook
import random


@hook.command
def flip(inp, flip_count=0, say=None):
    ".flip <text> -- Flips <text> over."
    guy = unicode(random.choice(flips), 'utf8')
    inp = inp.lower()
    inp = inp[::-1]
    reps = 0
    for n in xrange(len(inp)):
        rep = character_replacements.get(inp[n])
        if rep:
            inp = inp[:n] + rep.decode('utf8') + inp[n + 1:]
            reps += 1
            if reps == flip_count:
                break
    say(guy + u" ︵ " + inp)

flips = ["(屮ಠ︵ಠ)屮",
                "( ﾉ♉︵♉ ）ﾉ",
         "(╯°□°)╯",
                "( ﾉ⊙︵⊙）ﾉ"]

character_replacements = {
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
