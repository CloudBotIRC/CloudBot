import random

from cloudbot import hook


@hook.command("lurve","luff", "luv")
def lurve(text, nick, message):
	"""lurves all over <user>"""
	target = text.strip()

	# Use {N} to represent the person's nickname who is performing the action
	# Use {T} to represent the person's nickname who is the target of the action
	loving = [
		"{N} wraps arms around {T} and clings forever",
		"{N} cuddles {T} in the fluffiest blanket ever",
		"{N} lays their head on the lap of {T} and goes to sleep, dreaming da best sweet dreams",
		"{N} caresses {T}'s hair",
		"{N} caresses {T}'s cheek",
		"{N} plants a shy kiss on {T}'s cheek",
		"{N} gives {T} a BIIIIIIIIG hug!!!",
		"{N} lovingly tackles {T} into a pit of the softest pillows ever",
		"{N} cheers happily for {T}!!",
		"{N} pulls {T} back into bed for more cuddles ♥~",
		"{N} snuggles {T} for Netflix and chili popcorn",
		"{N} happily kisses {T} on the cheek",
		"{N} shares a milkshake with {T}"
	];

	out = "{}".format(random.choice(loving))
	out = out.replace("{N}", nick)
	out = out.replace("{T}", target)

	message(out)
