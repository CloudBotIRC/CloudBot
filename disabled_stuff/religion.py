from util import hook, http


@hook.command('god')
@hook.command
def bible(inp):
    """.bible <passage> -- gets <passage> from the Bible (ESV)"""

    base_url = ('http://www.esvapi.org/v2/rest/passageQuery?key=IP&'
                'output-format=plain-text&include-heading-horizontal-lines&'
                'include-headings=false&include-passage-horizontal-lines=false&'
                'include-passage-references=false&include-short-copyright=false&'
                'include-footnotes=false&line-length=0&'
                'include-heading-horizontal-lines=false')

    text = http.get(base_url, passage=inp)

    text = ' '.join(text.split())

    if len(text) > 400:
        text = text[:text.rfind(' ', 0, 400)] + '...'

    return text


@hook.command('allah')
@hook.command
def koran(inp):  # Koran look-up plugin by Ghetto Wizard
    """.koran <chapter.verse> -- gets <chapter.verse> from the Koran"""

    url = 'http://quod.lib.umich.edu/cgi/k/koran/koran-idx?type=simple'

    results = http.get_html(url, q1=inp).xpath('//li')

    if not results:
        return 'No results for ' + inp

    return results[0].text_content()
