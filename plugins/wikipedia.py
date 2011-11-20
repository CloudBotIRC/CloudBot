'''Searches wikipedia and returns first sentence of article
Scaevolus 2009'''

import re

from util import hook, http


api_prefix = "http://en.wikipedia.org/w/api.php"
search_url = api_prefix + "?action=opensearch&format=xml"

paren_re = re.compile('\s*\(.*\)$')


@hook.command('w')
@hook.command
def wiki(inp):
    '''.w/.wiki <phrase> -- gets first sentence of wikipedia ''' \
    '''article on <phrase>'''

    x = http.get_xml(search_url, search=inp)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = x.findall(ns + 'Section/' + ns + 'Item')

    if items == []:
        if x.find('error') is not None:
            return 'error: %(code)s: %(info)s' % x.find('error').attrib
        else:
            return 'no results found'

    def extract(item):
        return [item.find(ns + x).text for x in
                            ('Text', 'Description', 'Url')]

    title, desc, url = extract(items[0])

    if 'may refer to' in desc:
        title, desc, url = extract(items[1])

    title = paren_re.sub('', title)

    if title.lower() not in desc.lower():
        desc = title + desc

    desc = re.sub('\s+', ' ', desc).strip()  # remove excess spaces

    if len(desc) > 300:
        desc = desc[:300] + '...'

    return '%s -- %s' % (desc, http.quote(url, ':/'))