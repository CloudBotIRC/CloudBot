import requests

from cloudbot import hook


max_length = 100


def goog_trans(api_key, text, source, target):
    url = 'https://www.googleapis.com/language/translate/v2'

    if len(text) > max_length:
        return "This command only supports input of less then 100 characters."

    params = {
        'q': text,
        'key': api_key,
        'target': target,
        'format': 'text'
    }

    if source:
        params['source'] = source

    request = requests.get(url, params=params)
    parsed = request.json()

    if parsed.get('error'):
        if parsed['error']['code'] == 403:
            return "The Translate API is off in the Google Developers Console."
        else:
            return "Google API error."

    if not source:
        return '(%(detectedSourceLanguage)s) %(translatedText)s' % (parsed['data']['translations'][0])
    return '%(translatedText)s' % parsed['data']['translations'][0]


def match_language(fragment):
    fragment = fragment.lower()
    for short, _ in lang_pairs:
        if fragment in short.lower().split():
            return short.split()[0]

    for short, full in lang_pairs:
        if fragment in full.lower():
            return short.split()[0]

    return None


@hook.command()
def translate(text, bot):
    """[source language [target language]] <sentence> - translates <sentence> from source language (default autodetect)
     to target language (default English) using Google Translate"""

    api_key = bot.config.get("api_keys", {}).get("google_dev_key", None)
    if not api_key:
        return "This command requires a Google Developers Console API key."

    args = text.split(' ', 2)

    try:
        if len(args) >= 2:
            sl = match_language(args[0])
            if not sl:
                return goog_trans(api_key, text, '', 'en')
            if len(args) == 2:
                return goog_trans(api_key, args[1], sl, 'en')
            if len(args) >= 3:
                tl = match_language(args[1])
                if not tl:
                    if sl == 'en':
                        return 'unable to determine desired target language'
                    return goog_trans(api_key, args[1] + ' ' + args[2], sl, 'en')
                return goog_trans(api_key, args[2], sl, tl)
        return goog_trans(api_key, text, '', 'en')
    except IOError as e:
        return e


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
