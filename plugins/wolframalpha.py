import re

from util import hook, http


@hook.command('wa')
@hook.command
def wolframalpha(inp, bot=None):
    ".wa/.wolframalpha <query> -- computes <query> using Wolfram Alpha"

    api_key = bot.config.get("api_keys", {}).get("wolframalpha", None)
    if api_key is None:
        return "error: no api key set"

    url = 'http://api.wolframalpha.com/v2/query?format=plaintext'

    result = http.get_xml(url, input=inp, appid=api_key)

    pod_texts = []
    for pod in result.xpath("//pod"):
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
            pod_texts.append(title + ': ' + '|'.join(results))

    ret = '. '.join(pod_texts)

    if not pod_texts:
        return 'no results'

    ret = re.sub(r'\\(.)', r'\1', ret)

    def unicode_sub(match):
        return unichr(int(match.group(1), 16))

    ret = re.sub(r'\\:([0-9a-z]{4})', unicode_sub, ret)

    if len(ret) > 430:
        ret = ret[:ret.rfind(' ', 0, 430)]
        ret = re.sub(r'\W+$', '', ret) + '...'

    if not ret:
        return 'no results'

    return ret
