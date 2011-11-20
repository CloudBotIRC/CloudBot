from util import hook
import re

@hook.regex(r'^(H|h)ello mau5bot')
def response_hello(inp, say=None, nick=None):
    say("Hello " + nick + "!")

@hook.regex(r'^(H|h)i mau5bot')
def response_hi(inp, say=None, nick=None):
    say("Hi " + nick + "!")

@hook.regex(r'^(H|h)eya mau5bot')
def response_heya(inp, say=None, nick=None):
    say("Heya " + nick + "!")

@hook.regex(r'^(S|s)up mau5bot')
def response_sup(inp, say=None, nick=None):
    say("Sup " + nick + "!")

@hook.regex(r'^((I|i) love( you,?)?|ilu) mau5bot')
def response_love(inp, say=None, nick=None):
    say("I love you too, " + nick)

@hook.regex(r'^((I|i) hate( you,?)?|ihu) mau5bot')
def response_hate(inp, say=None):
    say(";(")