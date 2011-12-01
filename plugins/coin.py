# # Lukeroge
from util import hook
import random

## NOTES:
## Need to make a function to return a number of flips

# this produces a string full of comma seperated coin flips - should output this as a list
def flip_list(count):
    out = ""
    for i in range(count):
        flip = random.randint(0,1)
        if flip == 1:
            if i == 0:
                out += "Heads"
            else:
                out += ", Heads"
        else:
            if i == 0:
                out += "Tails"
            else:
                out += ", Tails"
    return out

# this doesn't work (yet)
def flip_simple(count):
    out = ""
    heads = 0
    tails = 0
    for i in range(count):
        flip = random.randint(0,1)
        if flip == 1:
            heads = heads + 1
        else:
            tails = tails + 1
    return msg

@hook.command(autohelp=False)
def coin(inp):
    ".coin [amount] -- flips some coins and shares the result."
    
    # checking for valid input. if valid input [count=inp], if invalid [return error], if no input [count=1]
    if inp.isdigit():
        count = int(inp)
    else:
        if inp:
            return "Invalid Input :("
        else:
            count = 1
 
    # depending on the count, we use three different methods to get the output
    if count <= 10 and count > 1:
        msg = "You flip " + str(count) + " coins and get the following results: " + flip_list(count)
        return msg
    elif count == 1:
        flip = random.randint(0,1)
        if flip == 1:
            return "You flip a coin and get heads."
        else:
            return "You flip a coin and get tails."
    else:
        return "Amounts over ten are not yet implemented"

