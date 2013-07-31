from util import hook, http, text
import re

api_url = "http://minecraftwiki.net/api.php?action=opensearch"
mc_url = "http://minecraftwiki.net/wiki/"


@hook.command
def mcwiki(inp):
    "mcwiki <phrase> -- Gets the first paragraph of" \
    " the Minecraft Wiki article on <phrase>."

    j = http.get_json(api_url, search=inp)

    if not j[1]:
        return "No results found."
    article_name = j[1][0].replace(' ', '_').encode('utf8')

    url = mc_url + http.quote(article_name, '')
    page = http.get_html(url)

    for p in page.xpath('//div[@class="mw-content-ltr"]/p'):
        if p.text_content():
            summary = " ".join(p.text_content().splitlines())
            summary = re.sub("\[\d+\]", "", summary)
            summary = text.truncate_str(summary, 250)
            return "%s :: \x02%s\x02" % (summary, url)

    return "Unknown Error."
