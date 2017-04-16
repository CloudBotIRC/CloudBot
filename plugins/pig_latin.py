#adds ay to the end of a word
pyg = 'ay'

#Orginal Hook for command
from cloudbot import hook
@hook_command("pig", "pigtran")
def pig(text, bot):

#checks if the word doesn't have any thing from the alphabet,
    if len(text) > 0 and pig.isalpha():
        #makes it lower-case
        pig = pig.lower()
        #redefines original
        word = pig
        #gets the first letter of word
        first = word[0]
        #gets any letters after the first one
        words = word[1:10]
        #translates the words
        new_word = words + first + pyg
        #prints the translation
        return new_word
    else:
        #Puts ^ around the whatever word was typed wrong
        w = "^" + pig + "^"
        #prints the error
        return "Invalid word " + w
