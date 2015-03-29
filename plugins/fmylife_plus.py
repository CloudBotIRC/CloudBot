import requests

from cloudbot import hook

API_BASE = "http://api.fmylife.com/view/{}"

API_SEARCH = API_BASE.format("search")
API_RANDOM = API_BASE.format("random")
API_ID = API_BASE.format("{}/nocomment")


def get_random():
    pass


def get_by_id(id):
    pass


def get_by_search(query):
    pass


def format_fml(fml):
    pass


@hook.on_start()
def load_key(bot):
    global api_key
    api_key = bot.config.get("api_keys", {}).get("fmylife", None)


@hook.command("fmylife", "fml")
def fmylife(text):
    """ """
    if not api_key:
        return "This command requires an API key from fmylife.com."

    if text:
        if text.isdigit():
            pass
            # get_by_id
        else:
            pass
            # get_by_search
    else:
        pass
        # get_random

    # format_fml