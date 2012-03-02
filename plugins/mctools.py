from util import hook, http
import string

@hook.command(autohelp=False)
def mcstatus(inp, bot=None):
    ".mcstatus -- Checks the status of Minecraft's login servers."
    username = bot.config.get("api_keys", {}).get("mc_user", None)
    password = bot.config.get("api_keys", {}).get("mc_pass", None)
    if password is None:
        return "error: no login set"

    login = http.get("https://login.minecraft.net/?user="+username+"&password="+password+"&version=13")
    if username.lower() in login.lower():
        return "Minecraft login servers appear to be online!"
    else:
        return "Minecraft login servers appear to be offline!"

@hook.command
def mclogin(inp, say=None):
    ".mclogin <username> <password> -- Attempts to log in to Minecrat with <username> and <password> (This is NOT logged)."
    inp = inp.split(" ")
    username = inp[0]
    password = inp[1]
    say("Attempting to log in using " + username)
    login = http.get("https://login.minecraft.net/?user=" + username + "&password=" + password + "&version=13")
    if username.lower() in login.lower():
        return "I logged in with " + username
    else:
        return "I couldn't log in using " + username + ", either the password is wrong or minecraft login servers are down!"

@hook.command
def mcpaid(inp):
    ".mcpaid <username> -- Checks if <username> has a premium Minecraft account."
    login = http.get("http://www.minecraft.net/haspaid.jsp?user=" + inp)
    if "true" in login:
        return "The account \'" + inp + "\' is a premium Minecraft account!"
    else:
        return "The account \'" + inp + "\' is not a premium Minecraft account!"
