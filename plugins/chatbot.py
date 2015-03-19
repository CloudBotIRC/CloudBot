"""
chatbot.py

Ask Cleverbot something via CloudBot! This one is way shorter!

Created By:
    - Foxlet <http://furcode.tk/>

License:
    GNU General Public License (Version 3)
"""

from cloudbot import hook
import requests
import urllib.parse
import hashlib
import collections
import html

SESSION = collections.OrderedDict()
API_URL = "http://www.cleverbot.com/webservicemin/"

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
    print(target_url)
    parsed = requests.post(API_URL, data=target_url)
    data = parsed.text.split('\r')
    SESSION['sessionid'] = data[1]
    return html.unescape(data[0])

@hook.command("ask", "cleverbot", "cb")
def ask(text):
    """ <question> -- Asks Cleverbot <question> """
    return cb_think(text)