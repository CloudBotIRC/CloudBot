"""
chatbot.py

Ask Cleverbot something via CloudBot!

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

SESSION = collections.OrderedDict()
API_URL = "http://www.cleverbot.com/webservicemin/"

@hook.onload()
def init_vars():
    SESSION['stimulus'] = ""
    SESSION['start'] = 'y'
    SESSION['icognoid'] = 'wsf'
    SESSION['fno'] = '0'
    SESSION['sub'] = 'Say'
    SESSION['islearning'] = '1'
    SESSION['cleanslate'] = 'false'

@hook.command()
def cb_think(text):
    SESSION['stimulus'] = text
    payload = urllib.parse.urlencode(SESSION)
    digest = hashlib.md5(payload[9:35].encode('utf-8')).hexdigest()
    target_url = "{}&icognocheck={}".format(payload, digest)
    print(target_url)
    parsed = requests.post(API_URL, data=target_url)
    data = parsed.text.split('\r')
    print(data)