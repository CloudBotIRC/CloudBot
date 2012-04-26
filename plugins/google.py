import random
from util import hook, http

from util.text import truncate_words


def api_get(kind, query):
    """Use the RESTful Google Search API"""
    url = 'http://ajax.googleapis.com/ajax/services/search/%s?' \
          'v=1.0&safe=moderate'
    return http.get_json(url % kind, q=query)


@hook.command('image')
@hook.command('gis')
@hook.command
def googleimage(inp):
    ".gis <query> -- Returns first Google Image result for <query>."

    parsed = api_get('images', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for images: %d: %s' % ( \
                      parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'no images found'
    return random.choice(parsed['responseData']['results'][:10]) \
                        ['unescapedUrl']


@hook.command('search')
@hook.command('g')
@hook.command
def google(inp):
    ".google <query> -- Returns first google search result for <query>."

    parsed = api_get('web', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for pages: %d: %s' % (
                      parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'No results found.'

    result = parsed['responseData']['results'][0]

    title = http.unescape(result['titleNoFormatting'])
    content = http.unescape(result['content'])

    if not content:
        content = "No description available."
    else:
        content = http.html.fromstring(content).text_content()

    out = '%s -- \x02%s\x02: "%s"' % (result['unescapedUrl'], title, content)

    return truncate_words(out, 300)