from util import hook, http, web
import re

steamcalc_url = "http://steamcalculator.com/id/{}/{}"
count_re = re.compile(r"Found (.*?) Games with a value of ")
region = "us" # can be "us", "eu" or "uk"


@hook.command
def steamcalc(inp):
    if " " in inp:
        return "Invalid Steam ID"

    url = steamcalc_url.format(http.quote_plus(inp), region)

    try:
        page = http.get_html(url)
    except Exception as e:
        return "Could not get Steam game listing: {}".format(e)

    try:
        count = page.xpath("//div[@id='rightdetail']/text()")[0]
        number = count_re.findall(count)[0]

        value = page.xpath("//div[@id='rightdetail']/h1/text()")[0]
    except IndexError:
        return "Could not get Steam game listing."

    try:
        short_url = web.isgd(url)
    except web.ShortenError as e:
        short_url = url

    return u"Found {} games with a value of {}! - {}".format(number, value, short_url)
