
from util import hook
from util.web import isgd
from urllib import quote_plus


@hook.command('gfy')
@hook.command
def lmgtfy(inp, bot=None):
    "lmgtfy [phrase] - Posts a google link for the specified phrase"

    url = "http://lmgtfy.com/?q=%s" % quote_plus(inp)
    return isgd(url, api_user, api_key)