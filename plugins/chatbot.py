from cleverbot import Cleverbot
from cloudbot import hook

# Clone cleverbot.py from https://github.com/folz/cleverbot.py
# Then run python3 setup.py install
# At the time of this commit version 1.0.2 works but is not yet in pypi

 
cb = Cleverbot()

@hook.command("ask", "gonzo", "gonzobot", "cleverbot", "cb")
def chitchat(text):
    """chat with cleverbot.com"""
    return cb.ask(text)
