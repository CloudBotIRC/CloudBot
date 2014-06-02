# Plugin by GhettoWizard and Scaevolus

import re

import requests
from lxml import html

from cloudbot import hook


def format_output(h, definition, show_examples):
    """
    :type h: lxml.etree._Element._Element
    :type definition: tuple
    """
    result = '{}: '.format(h.xpath('//dt[@class="title-word"]/a/text()')[0])

    correction = h.xpath('//span[@class="correct-word"]/text()')
    if correction:
        result = 'Definition for "{}": '.format(correction[0])

    sections = []
    for section in definition:
        if section.attrib['class'] == 'article':
            sections += [[section.text_content() + ': ']]
        elif section.attrib['class'] == 'example':
            if show_examples:
                sections[-1][-1] += ' ' + section.text_content()
        else:
            sections[-1] += [section.text_content()]

    for article in sections:
        result += article[0]
        if len(article) > 2:
            result += ' '.join('{}. {}'.format(n + 1, section)
                               for n, section in enumerate(article[1:]))
        else:
            result += article[1] + ' '

    synonyms = h.xpath('//dd[@class="synonyms"]')
    if synonyms:
        result += synonyms[0].text_content()

    result = re.sub(r'\s+', ' ', result)
    result = re.sub('\xb0', '', result)
    return result


@hook.command(["dictionary", "define"])
def define(text):
    """<word> - fetches definition of <word>
    :type text: str
    """

    url = 'http://ninjawords.com/'

    response = requests.get(url + text)
    if response.status_code != requests.codes.ok:
        return "Error reaching ninjawords.com: {}".format(response.status_code)

    h = html.fromstring(response.text)

    definition = h.xpath('//dd[@class="article"] | '
                         '//div[@class="definition"] |'
                         '//div[@class="example"]')

    if not definition:
        return 'No results for ' + text + ' :('

    result = format_output(h, definition, True)
    if len(result) > 450:
        result = format_output(h, definition, False)

    if len(result) > 450:
        result = result[:result.rfind(' ', 0, 450)]
        result = re.sub(r'[^A-Za-z]+\.?$', '', result) + ' ...'

    return result


@hook.command(["e", "etymology"])
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
