# # Lukeroge
from util import hook
import random

@hook.command(autohelp=False)
def coin(inp):
    ".coin - Flips a coin and shares the result."

    flip = random.randint(0,1)
    if flip == 1:
        sidename = "heads"
    else:
        sidename = "tails"
		
    message = "You flip a coin and it lands on " + sidename + "!"


    return message

@hook.command(autohelp=False)
def coins(inp):
    ".coins - Flips two coins and shares the results."

    flip2 = random.randint(0,1)
    if flip2 == 1:
        sidename2 = "heads"
    else:
        sidename2 = "tails"
    flip = random.randint(0,1)
    if flip == 1:
        sidename = "heads"
    else:
        sidename = "tails"
		
    message = "You flip two coins. You get a " + sidename + ", and a " + sidename2 + "!"


    return message
