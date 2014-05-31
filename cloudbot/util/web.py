""" web.py - web services and more """

import requests

class ShortenError(Exception):
    def __init__(self, message, request):
        self.message = message
        self.request = request

    def __str__(self):
        return "[HTTP {}] {}".format(self.request.status_code, self.message)
        
class Shortener:
    def shorten(self, url, custom=None):
        return url
    
    def try_shorten(self, url, custom=None):
        try:
            return self.shorten(url, custom)
        except ShortenError as e:
            return url

class Isgd(Shortener):
    def shorten(self, url, custom=None):
        p = {'url': url, 'shorturl': custom, 'format': 'json'}
        r = requests.get('http://is.gd/create.php', params=p)
        
        j = r.json()
        if 'shorturl' in j:
            return j['shorturl']
        else:
            raise ShortenError(j['errormessage'], r)
        
class Gitio(Shortener):
    def shorten(self, url, custom=None):
        p = {'url': url, 'code': custom}
        r = requests.post('http://git.io', data=p)

        if r.status_code == requests.codes.created:
            s = r.headers['location']
            if custom and not custom in s:
                raise ShortenError("That URL is already in use.", r)
            else:
                return s
        else:
            raise ShortenError("Unknown Error", r)

def haste(data, ext='txt', server='http://hastebin.com'):
    r = requests.post(server + '/documents', data=data)
    j = r.json()

    return "{}/{}.{}".format(server, j['key'], ext)
