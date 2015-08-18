"""
chatbot.py

Ask Cleverbot something via CloudBot! This one is way shorter!

Created By:
    - Foxlet <http://furcode.tk/>

License:
    GNU General Public License (Version 3)
"""

import urllib.parse
import hashlib
import collections
import html

import requests

from cloudbot import hook


SESSION = collections.OrderedDict()
API_URL = "http://www.cleverbot.com/webservicemin/"

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Accept-Language': 'en-us;q=0.8,en;q=0.5',
    'Pragma': 'no-cache',
    'Referer': 'http://www.cleverbot.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like '
                  'Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    'X-Moz': 'prefetch'
}

sess = requests.Session()
sess.get("http://www.cleverbot.com")

@hook.on_start()
def init_vars():
    SESSION['stimulus'] = ""
    SESSION['sessionid'] = ""
    SESSION['start'] = 'y'
    SESSION['icognoid'] = 'wsf'
    SESSION['fno'] = '0'
    SESSION['sub'] = 'Say'
    SESSION['islearning'] = '1'
    SESSION['cleanslate'] = 'false'


def cb_think(text):
    SESSION['stimulus'] = text
    payload = urllib.parse.urlencode(SESSION)
    digest = hashlib.md5(payload[9:35].encode('utf-8')).hexdigest()
    target_url = "{}&icognocheck={}".format(payload, digest)
    parsed = sess.post(API_URL, data=target_url, headers=HEADERS)
    data = parsed.text.split('\r')
    SESSION['sessionid'] = data[1]
    if parsed.status_code == 200:
        return html.unescape(str(data[0]))
    else:
	    print("CleverBot API Returned "+str(parsed.status_code))
	    return "Error: API returned "+str(parsed.status_code)


@hook.command("ask", "cleverbot", "cb")
def ask(text):
    """ <question> -- Asks Cleverbot <question> """
    return cb_think(text)
