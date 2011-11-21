from util import hook
import urllib

@hook.command(autohelp=False)
def mcstatus(inp, bot=None):
    ".mcstatus - Attempts to log in to minecraft"
    username = bot.config["api_keys"]["mc_user"]
    password = bot.config["api_keys"]["mc_pass"]
    login = urllib.urlopen("https://login.minecraft.net/?user="+username+"&password="+password+"&&version=13").read()
    if username in login:
        return "Attempting to connect to Minecraft login servers... Login servers appear to be online!"
    else:
        return "Attempting to connect to Minecraft login servers... Login servers appear to be offline :("

@hook.command
def mclogin(inp, say=None):
    ".mclogin <username> <password> - Attempts to log in to minecraft using the provided username and password, this is NOT logged."
    inp = inp.split(" ")
    username = inp[0]
    password = inp[1]
    say("Attempting to log in using " + username)
    login = urllib.urlopen("https://login.minecraft.net/?user=" + username + "&password=" + password + "&&version=13").read()
    if username in login:
        return "I logged in with " + username
    else:
        return "I couldn't log in using " + username + ", either the password changed or minecraft auth is down :O"

@hook.command
def haspaid(inp):
    ".haspaid <username> - Checks if a user has a premium Minecraft account"
    login = urllib.urlopen("http://www.minecraft.net/haspaid.jsp?user=" + inp).read()
    if "true" in login:
        return "The user " + inp + " has a premium Minecraft account."
    else:
        return "The user " + inp + " either has not paid or is an unused nickname."

