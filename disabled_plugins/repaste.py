from util import hook, http

import urllib
import random
import urllib2
import htmlentitydefs
import re

re_htmlent = re.compile("&(" + "|".join(htmlentitydefs.name2codepoint.keys()) + ");")
re_numeric = re.compile(r'&#(x?)([a-fA-F0-9]+);')


def db_init(db):
    db.execute("create table if not exists repaste(chan, manual, primary key(chan))")
    db.commit()


def decode_html(text):
    text = re.sub(re_htmlent,
                   lambda m: unichr(htmlentitydefs.name2codepoint[m.group(1)]),
                   text)

    text = re.sub(re_numeric,
                  lambda m: unichr(int(m.group(2), 16 if m.group(1) else 10)),
                  text)
    return text


def scrape_mibpaste(url):
    if not url.startswith("http"):
        url = "http://" + url
    pagesource = http.get(url)
    rawpaste = re.search(r'(?s)(?<=<body>\n).+(?=<hr>)', pagesource).group(0)
    filterbr = rawpaste.replace("<br />", "")
    unescaped = decode_html(filterbr)
    stripped = unescaped.strip()

    return stripped


def scrape_pastebin(url):
    id = re.search(r'(?:www\.)?pastebin.com/([a-zA-Z0-9]+)$', url).group(1)
    rawurl = "http://pastebin.com/raw.php?i=" + id
    text = http.get(rawurl)

    return text


autorepastes = {}


#@hook.regex('(pastebin\.com)(/[^ ]+)')
@hook.regex('(mibpaste\.com)(/[^ ]+)')
def autorepaste(inp, input=None, notice=None, db=None, chan=None, nick=None):
    db_init(db)
    manual = db.execute("select manual from repaste where chan=?", (chan, )).fetchone()
    if manual and len(manual) and manual[0]:
        return
    url = inp.group(1) + inp.group(2)
    urllib.unquote(url)
    if url in autorepastes:
        out = autorepastes[url]
        notice("In the future, please use a less awful pastebin (e.g. pastebin.com)")
    else:
        out = repaste("http://" + url, input, db, False)
        autorepastes[url] = out
        notice("In the future, please use a less awful pastebin (e.g. pastebin.com) instead of %s." % inp.group(1))
    input.say("%s (repasted for %s)" % (out, nick))


scrapers = {
    r'mibpaste\.com': scrape_mibpaste,
    r'pastebin\.com': scrape_pastebin
}


def scrape(url):
    for pat, scraper in scrapers.iteritems():
        print "matching " + repr(pat) + " " + url
        if re.search(pat, url):
            break
    else:
        return None

    return scraper(url)


def paste_sprunge(text, syntax=None, user=None):
    data = urllib.urlencode({"sprunge": text})
    url = urllib2.urlopen("http://sprunge.us/", data).read().strip()

    if syntax:
        url += "?" + syntax

    return url


def paste_ubuntu(text, user=None, syntax='text'):
    data = urllib.urlencode({"poster": user,
                             "syntax": syntax,
                             "content": text})

    return urllib2.urlopen("http://paste.ubuntu.com/", data).url


def paste_gist(text, user=None, syntax=None, description=None):
    data = {
        'file_contents[gistfile1]': text,
        'action_button': "private"
    }

    if description:
        data['description'] = description

    if syntax:
        data['file_ext[gistfile1]'] = "." + syntax

    req = urllib2.urlopen('https://gist.github.com/gists', urllib.urlencode(data).encode('utf8'))
    return req.url


def paste_strictfp(text, user=None, syntax="plain"):
    data = urllib.urlencode(dict(
        language=syntax,
        paste=text,
        private="private",
        submit="Paste"))
    req = urllib2.urlopen("http://paste.strictfp.com/", data)
    return req.url


pasters = dict(
    ubuntu=paste_ubuntu,
    sprunge=paste_sprunge,
    gist=paste_gist,
    strictfp=paste_strictfp
)


@hook.command
def repaste(inp, input=None, db=None, isManual=True):
    ".repaste mode|list|[provider] [syntax] <pastebinurl> -- Reuploads mibpaste to [provider]."

    parts = inp.split()
    db_init(db)
    if parts[0] == 'list':
        return " ".join(pasters.keys())

    paster = paste_gist
    args = {}

    if not parts[0].startswith("http"):
        p = parts[0].lower()

        if p in pasters:
            paster = pasters[p]
            parts = parts[1:]

    if not parts[0].startswith("http"):
        p = parts[0].lower()
        parts = parts[1:]

        args["syntax"] = p

    if len(parts) > 1:
        return "PEBKAC"

    args["user"] = input.user

    url = parts[0]

    scraped = scrape(url)

    if not scraped:
        return "No scraper for given url"

    args["text"] = scraped
    pasted = paster(**args)

    return pasted
