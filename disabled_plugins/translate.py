import htmlentitydefs
import re

from util import hook, http

########### from http://effbot.org/zone/re-sub.htm#unescape-html #############


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is

    return re.sub("&#?\w+;", fixup, text)

##############################################################################


def goog_trans(text, slang, tlang):
    url = 'http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&key=ABQIAAAAGjLiqTxkFw7F24ITXc4bNRS04yDz5pgaUTdxja2Sk3UoWlae7xTXom3fBzER6Upo8jfzcTtvz-8ebQ'
    parsed = http.get_json(url, q=text, langpair=(slang + '|' + tlang))
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error with the translation server: %d: %s' % (
                parsed['responseStatus'], parsed['responseDetails']))
    if not slang:
        return unescape('(%(detectedSourceLanguage)s) %(translatedText)s' %
                (parsed['responseData']))
    return unescape(parsed['responseData']['translatedText'])


def match_language(fragment):
    fragment = fragment.lower()
    for short, _ in lang_pairs:
        if fragment in short.lower().split():
            return short.split()[0]

    for short, full in lang_pairs:
        if fragment in full.lower():
            return short.split()[0]

    return None


@hook.command
def translate(inp):
    '.translate [source language [target language]] <sentence> -- translates' \
    ' <sentence> from source language (default autodetect) to target' \
    ' language (default English) using Google Translate'
    return "Due to Google deprecating the translation API, this command is no longer available :("

    args = inp.split(' ', 2)

    try:
        if len(args) >= 2:
            sl = match_language(args[0])
            if not sl:
                return goog_trans(inp, '', 'en')
            if len(args) >= 3:
                tl = match_language(args[1])
                if not tl:
                    if sl == 'en':
                        return 'unable to determine desired target language'
                    return goog_trans(args[1] + ' ' + args[2], sl, 'en')
                return goog_trans(args[2], sl, tl)
        return goog_trans(inp, '', 'en')
    except IOError, e:
        return e


languages = 'ja fr de ko ru zh'.split()
language_pairs = zip(languages[:-1], languages[1:])


def babel_gen(inp):
    for language in languages:
        inp = inp.encode('utf8')
        trans = goog_trans(inp, 'en', language).encode('utf8')
        inp = goog_trans(trans, language, 'en')
        yield language, trans, inp


@hook.command
def babel(inp):
    ".babel <sentence> -- translates <sentence> through multiple languages"
    return "Due to Google deprecating the translation API, this command is no longer available :("

    try:
        return list(babel_gen(inp))[-1][2]
    except IOError, e:
        return e


@hook.command
def babelext(inp):
    ".babelext <sentence> -- like .babel, but with more detailed output"

    return "Due to Google deprecating the translation API, this command is no longer available :("

    try:
        babels = list(babel_gen(inp))
    except IOError, e:
        return e

    out = u''
    for lang, trans, text in babels:
        out += '%s:"%s", ' % (lang, text.decode('utf8'))

    out += 'en:"' + babels[-1][2].decode('utf8') + '"'

    if len(out) > 300:
        out = out[:150] + ' ... ' + out[-150:]

    return out


lang_pairs = [
    ("no", "Norwegian"),
    ("it", "Italian"),
    ("ht", "Haitian Creole"),
    ("af", "Afrikaans"),
    ("sq", "Albanian"),
    ("ar", "Arabic"),
    ("hy", "Armenian"),
    ("az", "Azerbaijani"),
    ("eu", "Basque"),
    ("be", "Belarusian"),
    ("bg", "Bulgarian"),
    ("ca", "Catalan"),
    ("zh-CN zh", "Chinese"),
    ("hr", "Croatian"),
    ("cs", "Czech"),
    ("da", "Danish"),
    ("nl", "Dutch"),
    ("en", "English"),
    ("et", "Estonian"),
    ("tl", "Filipino"),
    ("fi", "Finnish"),
    ("fr", "French"),
    ("gl", "Galician"),
    ("ka", "Georgian"),
    ("de", "German"),
    ("el", "Greek"),
    ("ht", "Haitian Creole"),
    ("iw", "Hebrew"),
    ("hi", "Hindi"),
    ("hu", "Hungarian"),
    ("is", "Icelandic"),
    ("id", "Indonesian"),
    ("ga", "Irish"),
    ("it", "Italian"),
    ("ja jp jpn", "Japanese"),
    ("ko", "Korean"),
    ("lv", "Latvian"),
    ("lt", "Lithuanian"),
    ("mk", "Macedonian"),
    ("ms", "Malay"),
    ("mt", "Maltese"),
    ("no", "Norwegian"),
    ("fa", "Persian"),
    ("pl", "Polish"),
    ("pt", "Portuguese"),
    ("ro", "Romanian"),
    ("ru", "Russian"),
    ("sr", "Serbian"),
    ("sk", "Slovak"),
    ("sl", "Slovenian"),
    ("es", "Spanish"),
    ("sw", "Swahili"),
    ("sv", "Swedish"),
    ("th", "Thai"),
    ("tr", "Turkish"),
    ("uk", "Ukrainian"),
    ("ur", "Urdu"),
    ("vi", "Vietnamese"),
    ("cy", "Welsh"),
    ("yi", "Yiddish")
]
