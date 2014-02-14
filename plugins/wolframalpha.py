import re

from util import hook, http, text, web


@hook.command('math')
@hook.command('calc')
@hook.command('wa')
@hook.command
def wolframalpha(inp, bot=None):
    """wa <query> -- Computes <query> using Wolfram Alpha."""
    api_key = bot.config.get("api_keys", {}).get("wolframalpha", None)

    if not api_key:
        return "error: missing api key"

    url = 'http://api.wolframalpha.com/v2/query?format=plaintext'

    result = http.get_xml(url, input=inp, appid=api_key)

    # get the URL for a user to view this query in a browser
    query_url = "http://www.wolframalpha.com/input/?i=" + \
                http.quote_plus(inp.encode('utf-8'))
    short_url = web.try_isgd(query_url)

    pod_texts = []
    for pod in result.xpath("//pod[@primary='true']"):
        title = pod.attrib['title']
        if pod.attrib['id'] == 'Input':
            continue

        results = []
        for subpod in pod.xpath('subpod/plaintext/text()'):
            subpod = subpod.strip().replace('\\n', '; ')
            subpod = re.sub(r'\s+', ' ', subpod)
            if subpod:
                results.append(subpod)
        if results:
            pod_texts.append(title + u': ' + u', '.join(results))

    ret = u' - '.join(pod_texts)

    if not pod_texts:
        return 'No results.'

    ret = re.sub(r'\\(.)', r'\1', ret)

    def unicode_sub(match):
        return unichr(int(match.group(1), 16))

    ret = re.sub(r'\\:([0-9a-z]{4})', unicode_sub, ret)

    ret = text.truncate_str(ret, 250)

    if not ret:
        return 'No results.'

    return u"{} - {}".format(ret, short_url)
