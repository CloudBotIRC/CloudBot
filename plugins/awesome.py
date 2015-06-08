import codecs
import json
import os
import random
import asyncio
import re

from cloudbot import hook
from cloudbot.util import textgen

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)

def is_valid(target):
	""" Checks if a string is a valid IRC nick. """
	if nick_re.match(target):
		return True
	else:
		return False

def is_self(conn, target):
	""" Checks if a string is "****self" or contains conn.name. """
	if re.search("(^..?.?.?self|{})".format(re.escape(conn.nick)), target, re.I):
		return True
	else:
		return False

@hook.on_start()
def load_attacks(bot):
	"""
	:type bot: cloudbot.bot.CloudBot
	"""
	global awesome
	
	with codecs.open(os.path.join(bot.data_dir, "awesome.txt"), encoding="utf-8") as f:
		awesome = [line.strip() for line in f.readlines() if not line.startswith("//")]

@asyncio.coroutine
@hook.command
def awesome(text, conn, nick, message):
	"""<user> - says awesome stuff about <user>"""
	target = text.strip()
	
	if target == "":
		target = user
	
	if not is_valid(target):
		return "I can't attack that."
	if is_self(conn, target):
		# user is trying to make the bot attack itself!
		target = nick
	
	joke = random.choice(jokes)
	
	message(joke.replace("%s", target))
