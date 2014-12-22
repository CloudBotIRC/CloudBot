""" web.py - web services and more """

import requests

# Constants

default_link_service = 'qx.lc'
default_paste_service = 'qx.lc'

# Shortening / pasting

# Public API


def shorten(url, custom=None, service=default_link_service):
    impl = link_services[service]
    return impl.shorten(url, custom)


def try_shorten(url, custom=None, service=default_link_service):
    impl = link_services[service]
    return impl.try_shorten(url, custom)


def expand(url, service=None):
    if service:
        impl = link_services[service]
    else:
        impl = None
        for name in link_services:
            if name in url:
                impl = link_services[name]
                break

        if impl is None:
            impl = LinkService()

    return impl.expand(url)


def paste(data, ext='txt', service=default_paste_service):
    impl = paste_services[service]
    return impl.paste(data, ext)


class ServiceError(Exception):
    def __init__(self, message, request):
        self.message = message
        self.request = request

    def __str__(self):
        return '[HTTP {}] {}'.format(self.request.status_code, self.message)


class LinkService:
    def shorten(self, url, custom=None):
        return url

    def try_shorten(self, url, custom=None):
        try:
            return self.shorten(url, custom)
        except ServiceError:
            return url

    def expand(self, url):
        r = requests.get(url, allow_redirects=False)

        if 'location' in r.headers:
            return r.headers['location']
        else:
            raise ServiceError('That URL does not exist', r)


class PasteService:
    def paste(self, data, ext):
        raise NotImplementedError

# Internal Implementations

link_services = {}
paste_services = {}


def _link_service(name):
    def _decorate(impl):
        link_services[name] = impl()

    return _decorate


def _paste_service(name):
    def _decorate(impl):
        paste_services[name] = impl()

    return _decorate


@_link_service("qx.lc")
class QxlcLinkService(LinkService):
    def shorten(self, url, custom=None):
        # qx.lc doesn't support custom urls, so ignore custom
        server = "http://qx.lc"
        r = requests.post("{}/api/shorten".format(server), data={"url": url})

        if r.status_code != 200:
            raise ServiceError(r.text, r)
        else:
            return r.text


@_paste_service("qx.lc")
class QxlcPasteService(PasteService):
    def paste(self, text, ext):
        r = requests.post("http://qx.lc/api/paste", data={"paste": text})
        url = r.text

        if r.status_code != 200:
            return r.text  # this is the error text
        else:
            if ext is not None:
                return "{}.{}".format(url, ext)
            else:
                return url
