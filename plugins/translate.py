# BING translation plugin by Lukeroge and neersighted
from util import hook
from util import http
import re 
import htmlentitydefs
import mygengo

gengo = mygengo.MyGengo(
    public_key='PlwtF1CZ2tu27IdX_SXNxTFmfN0j|_-pJ^Rf({O-oLl--r^QM4FygRdt^jusSSDE',
    private_key='wlXpL=SU[#JpPu[dQaf$v{S3@rg[=95$$TA(k$sb3_6~B_zDKkTbd4#hXxaorIae',
    sandbox=False,
)

def gengo_translate(text, source, target):
    try:
        translation = gengo.postTranslationJob(job={
            'type': 'text',
            'slug': 'Translating '+source+' to '+target+' with the myGengo API',
            'body_src': text, 
            'lc_src': source,
            'lc_tgt': target,
            'tier': 'machine',
        })
        translated = translation['response']['job']['body_tgt']
        return u"(%s > %s) %s" % (source, target, translated)
    except mygengo.MyGengoError:
        return "error: could not translate"

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
    ".translate <source language> <target language> <sentence> -- Translates <sentence> from <source language> to <target language> using MyGengo."
    args = inp.split(' ')
    sl = match_language(args[0])
    tl = match_language(args[1])
    txt = unicode(" ".join(args[2:]))
    if sl and tl:
        return unicode(gengo_translate(txt, sl, tl))
    else:
        return "error: translate could not reliably determine one or both languages"

languages = 'ja fr de ko ru zh'.split()
language_pairs = zip(languages[:-1], languages[1:])
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
    ("cs cz", "Czech"),
    ("da dk", "Danish"),
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
