# # Lukeroge
from util import hook
import random

@hook.command(autohelp=False)
def coin(inp):
    ".coin [amount] -- flips some coins and shares the result."

    if inp.isdigit():
        count = int(inp)
    else:
        count = 1

    if count > 10:
        return "Maximum amount of coins is ten."

    if count > 1:
        coin = "coins"
    else:
        coin = "coin"

    msg = "You flip " + str(count) + " " + coin + " and get the following results:" 

    for i in range(count):
        flip = random.randint(0,1)
        if flip == 1:
            if i == 0:
                msg += " Heads"
            else:
                msg += ", Heads"
        else:
            if i == 0:
                msg += " Tails"
            else:
                msg += ", Tails"
		

    return msg

