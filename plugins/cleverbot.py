# from jessi bot
import urllib2
import hashlib
import re
import unicodedata
from util import hook

# these are just parts required
# TODO: Merge them.

arglist = ['', 'y', '', '', '', '', '', '', '', '', 'wsf', '',
           '', '', '', '', '', '', '', '0', 'Say', '1', 'false']

always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')

headers = {'X-Moz': 'prefetch', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1)Gecko/20100101 Firefox/7.0',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Referer': 'http://www.cleverbot.com',
           'Pragma': 'no-cache', 'Cache-Control': 'no-cache, no-cache', 'Accept-Language': 'en-us;q=0.8,en;q=0.5'}

keylist = ['stimulus', 'start', 'sessionid', 'vText8', 'vText7', 'vText6',
           'vText5', 'vText4', 'vText3', 'vText2', 'icognoid',
           'icognocheck', 'prevref', 'emotionaloutput', 'emotionalhistory',
           'asbotname', 'ttsvoice', 'typing', 'lineref', 'fno', 'sub',
           'islearning', 'cleanslate']

MsgList = list()


def quote(s, safe='/'):  # quote('abc def') -> 'abc%20def'
    s = s.encode('utf-8')
    s = s.decode('utf-8')
    print "s= " + s
    print "safe= " + safe
    safe += always_safe
    safe_map = dict()
    for i in range(256):
        c = chr(i)
        safe_map[c] = (c in safe) and c or ('%%%02X' % i)
    try:
        res = map(safe_map.__getitem__, s)
    except:
        print "blank"
        return ''
    print "res= " + ''.join(res)
    return ''.join(res)


def encode(keylist, arglist):
    text = str()
    for i in range(len(keylist)):
        k = keylist[i]
        v = quote(arglist[i])
        text += '&' + k + '=' + v
    text = text[1:]
    return text


def Send():
    data = encode(keylist, arglist)
    digest_txt = data[9:29]
    new_hash = hashlib.md5(digest_txt).hexdigest()
    arglist[keylist.index('icognocheck')] = new_hash
    data = encode(keylist, arglist)
    req = urllib2.Request('http://www.cleverbot.com/webservicemin',
                          data, headers)
    f = urllib2.urlopen(req)
    reply = f.read()
    return reply


def parseAnswers(text):
    d = dict()
    keys = ['text', 'sessionid', 'logurl', 'vText8', 'vText7', 'vText6',
            'vText5', 'vText4', 'vText3', 'vText2', 'prevref', 'foo',
            'emotionalhistory', 'ttsLocMP3', 'ttsLocTXT', 'ttsLocTXT3',
            'ttsText', 'lineRef', 'lineURL', 'linePOST', 'lineChoices',
            'lineChoicesAbbrev', 'typingData', 'divert']
    values = text.split('\r')
    i = 0
    for key in keys:
        d[key] = values[i]
        i += 1
    return d


def ask(inp):
    arglist[keylist.index('stimulus')] = inp
    if MsgList:
        arglist[keylist.index('lineref')] = '!0' + str(len(
            MsgList) / 2)
    asw = Send()
    MsgList.append(inp)
    answer = parseAnswers(asw)
    for k, v in answer.iteritems():
        try:
            arglist[keylist.index(k)] = v
        except ValueError:
            pass
    arglist[keylist.index('emotionaloutput')] = str()
    text = answer['ttsText']
    MsgList.append(text)
    return text


@hook.command("cb")
def cleverbot(inp, reply=None):
    reply(ask(inp))


''' # TODO: add in command to control extra verbose per channel
@hook.event('PRIVMSG')
def cbevent(inp, reply=None):
    reply(ask(inp))

@hook.command("cbver", permissions=['cleverbot'])
def cleverbotverbose(inp, notice=None):
    if on in input
'''
