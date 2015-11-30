import random

from cloudbot import hook


@hook.command("lurve","luff", "luv")
def lurve(text, nick, message):
	""""loves all over <user>"""
	target = text.strip()
	
	
	loving = [ nick + " wraps arms around " + target + " and clings forever", nick + " cuddles " + target +" in the fluffiest blanket ever", nick + " lays their head on the lap of " + target + " and goes to sleep, dreaming da best sweet dreams ", nick + " caresses " + target + "'s hair", nick + " caresses " + target + "'s cheek", nick + " plants a shy kiss on " + target + "'s cheek", nick + " gives " + target + " a BIIIIIIIIG hug!!!", nick + " lovingly tackles " + target + " into a pit of the softest pillows ever", nick + " cheers happily for " + target + "!!", nick + " pulls " + target + " back into bed for more cuddles ♥~", nick + " snuggles " + target + " for Netflix and chili popcorn", nick + " happily kisses " + target + " on the cheek", nick + " shares a milkshake with " + target]
	
	message(random.choice(loving))
	
	