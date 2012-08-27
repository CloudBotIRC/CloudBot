from util import hook
from util.web import bitly
from urllib import quote_plus


@hook.command('gfy')
@hook.command
def lmgtfy(inp, bot=None):
    "lmgtfy [phrase] - Posts a google link for the specified phrase"
    api_user = bot.config.get("api_keys", {}).get("bitly_user", None)
    api_key = bot.config.get("api_keys", {}).get("bitly_api", None)
    if api_key is None:
        return "error: no api key set"

    url = "http://lmgtfy.com/?q=%s" % quote_plus(inp)
    return bitly(url, api_user, api_key)