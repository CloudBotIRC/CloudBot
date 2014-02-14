import datetime

from util import hook, http, timesince


@hook.command("scene")
@hook.command
def pre(inp):
    """pre <query> -- searches scene releases using orlydb.com"""

    try:
        h = http.get_html("http://orlydb.com/", q=inp)
    except http.HTTPError as e:
        return 'Unable to fetch results: {}'.format(e)

    results = h.xpath("//div[@id='releases']/div/span[@class='release']/..")

    if not results:
        return "No results found."

    result = results[0]

    date = result.xpath("span[@class='timestamp']/text()")[0]
    section = result.xpath("span[@class='section']//text()")[0]
    name = result.xpath("span[@class='release']/text()")[0]

    # parse date/time
    date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_string = date.strftime("%d %b %Y")
    since = timesince.timesince(date)

    size = result.xpath("span[@class='inforight']//text()")
    if size:
        size = ' - ' + size[0].split()[0]
    else:
        size = ''

    return '{} - {}{} - {} ({} ago)'.format(section, name, size, date_string, since)
