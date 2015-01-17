import re

import requests
from lxml import html

from cloudbot import hook

speedtest_re = re.compile(r'.*://www.speedtest.net/my-result/([0-9]+)?.*', re.I)
base_url = "http://www.speedtest.net/my-result/{}"


@hook.regex(speedtest_re)
def speedtest_url(match):
    test_id = match.group(1)
    url = base_url.format(test_id)

    request = requests.get(url)
    request.raise_for_status()
    data = html.fromstring(request.text)

    download = data.xpath('//div[@class="share-speed share-download"]/p')[0].text_content().strip()
    upload = data.xpath('//div[@class="share-speed share-upload"]/p')[0].text_content().strip()

    ping = data.xpath('//div[@class="share-data share-ping"]/p')[0].text_content().strip()
    isp = data.xpath('//div[@class="share-data share-isp"]/p')[0].text_content().strip().title()

    return "\x02{}\x02 - Download: \x02{}\x02, Upload: \x02{}\x02, Ping: \x02{}\x02".format(isp, download, upload, ping)
