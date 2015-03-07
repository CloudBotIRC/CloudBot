# Plugin by GhettoWizard and Scaevolus

import re
from lxml import html

import requests

from cloudbot import hook

@hook.command("e", "etymology")
def etymology(text):
    """<word> - retrieves the etymology of <word>
    :type text: str
    """

    url = 'http://www.etymonline.com/index.php'

    response = requests.get(url, params={"term": text})
    if response.status_code != requests.codes.ok:
        return "Error reaching etymonline.com: {}".format(response.status_code)

    h = html.fromstring(response.text)

    etym = h.xpath('//dl')

    if not etym:
        return 'No etymology found for {} :('.format(text)

    etym = etym[0].text_content()

    etym = ' '.join(etym.split())

    if len(etym) > 400:
        etym = etym[:etym.rfind(' ', 0, 400)] + ' ...'

    return etym
