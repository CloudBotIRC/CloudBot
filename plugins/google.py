import random

from util import hook, http, text


def api_get(kind, query):
    """Use the RESTful Google Search API"""
    url = 'http://ajax.googleapis.com/ajax/services/search/%s?' \
          'v=1.0&safe=moderate'
    return http.get_json(url % kind, q=query)


@hook.command('image')
@hook.command('gis')
@hook.command
def googleimage(inp):
    """gis <query> -- Returns first Google Image result for <query>."""

    parsed = api_get('images', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for images: {}: {}'.format(parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'no images found'
    return random.choice(parsed['responseData']['results'][:10])['unescapedUrl']


@hook.command('search')
@hook.command('g')
@hook.command
def google(inp):
    """google <query> -- Returns first google search result for <query>."""

    parsed = api_get('web', inp)
    if not 200 <= parsed['responseStatus'] < 300:
        raise IOError('error searching for pages: {}: {}'.format(parsed['responseStatus'], ''))
    if not parsed['responseData']['results']:
        return 'No results found.'

    result = parsed['responseData']['results'][0]

    title = http.unescape(result['titleNoFormatting'])
    title = text.truncate_str(title, 60)
    content = http.unescape(result['content'])

    if not content:
        content = "No description available."
    else:
        content = http.html.fromstring(content).text_content()
        content = text.truncate_str(content, 150)

    return u'{} -- \x02{}\x02: "{}"'.format(result['unescapedUrl'], title, content)
