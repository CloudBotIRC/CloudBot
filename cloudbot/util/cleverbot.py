#!/usr/bin/env python
"""
cleverbot.py - jenni's Cleverbot API module
Copyright 2013 Michael Yanovich (yanovich.net)
Copyright 2013 Manishrw (github.com/manishrw)
Licensed under the Eiffel Forum License 2.

Ported to Python 3 by foxlet. (furcode.tk)

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/

This library lets you open chat session with cleverbot (www.cleverbot.com)
"""

import urllib.request
import urllib.error
import urllib.parse
import hashlib
import re


class ServerFullError(Exception):
    pass


ReplyFlagsRE = re.compile('<INPUT NAME=(.+?) TYPE=(.+?) VALUE="(.*?)">',
                          re.IGNORECASE | re.MULTILINE)


class Session():
    key_list = ['stimulus', 'start', 'sessionid', 'vText8', 'vText7', 'vText6',
                'vText5', 'vText4', 'vText3', 'vText2', 'icognoid',
                'icognocheck', 'prevref', 'emotionaloutput', 'emotionalhistory',
                'asbotname', 'ttsvoice', 'typing', 'lineref', 'fno', 'sub',
                'islearning', 'cleanslate']

    headers = dict()
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0)'
    headers['User-Agent'] += ' Gecko/20130101 Firefox/26.0'
    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;'
    headers['Accept'] += 'q=0.9,*/*;q=0.8'
    headers['Accept-Language'] = 'en-us;q=0.8,en;q=0.5'
    headers['X-Moz'] = 'prefetch'
    headers['Accept-Charset'] = 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
    headers['Referer'] = 'http://www.cleverbot.com'
    headers['Cache-Control'] = 'no-cache, no-cache'
    headers['Pragma'] = 'no-cache'

    def __init__(self):
        self.arg_list = ['', 'y', '', '', '', '', '', '', '', '', 'wsf', '',
                         '', '', '', '', '', '', '', '0', 'Say', '1', 'false']
        self.message_list = list()

    def send(self):
        data = encode(self.key_list, self.arg_list)
        digest_txt = data[9:35]
        new_hash = hashlib.md5(digest_txt).hexdigest()
        self.arg_list[self.key_list.index('icognocheck')] = new_hash
        data = encode(self.key_list, self.arg_list)
        req = urllib.request.Request('http://www.cleverbot.com/webservicemin',
                                     data, self.headers)
        f = urllib.request.urlopen(req)
        reply = f.read()
        return reply

    def ask(self, q):
        self.arg_list[self.key_list.index('stimulus')] = q
        if self.message_list:
            self.arg_list[self.key_list.index('lineref')] = '!0' + str(len(
                self.message_list) / 2)
        asw = self.send()
        self.message_list.append(q)
        answer = parse_answers(asw.decode('UTF-8'))
        for k, v in answer.items():
            try:
                self.arg_list[self.key_list.index(k)] = v
            except ValueError:
                pass
        self.arg_list[self.key_list.index('emotionaloutput')] = str()
        text = answer['ttsText']
        self.message_list.append(text)
        return text


def parse_answers(text):
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


def encode(key_list, arg_list):
    text = str()
    for i in range(len(key_list)):
        k = key_list[i]
        v = quote(arg_list[i])
        text += '&' + k + '=' + v
    text = text[1:]
    return text.encode('UTF-8')


always_safe = ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789' '_.-')


def quote(s, safe='/'):
    safe += always_safe
    safe_map = dict()
    for i in range(256):
        c = chr(i)
        safe_map[c] = (c in safe) and c or ('%%%02X' % i)
    try:
        res = list(map(safe_map.__getitem__, s))
    except:
        return ''
    return ''.join(res)
