############################ 
#                          #
#                          #
#       Vault 108          #
#       01.10.2017         #
#                          #
#                          #
############################
import random

from cloudbot import hook


@hook.command("soup")
def soup(text, nick, message):
        """Gives a user some soup"""
        target = text.strip()


        soup = [
                "{N} hands {T} A Hot bowl of Ajiaco ",
                "{N} hands {T} A Hot bowl of Avgolemono ",
                "{N} hands {T} A Hot bowl of Borscht ",
                "{N} hands {T} A Hot bowl of Beef noodle soup",
                "{N} hands {T} A Hot bowl of Beer soup",
                "{N} hands {T} A Hot bowl of Birds nest soup",
                "{N} hands {T} A Hot bowl of Chicken noodle soup",
                "{N} hands {T} A Hot bowl of Caldo verde ",
                "{N} hands {T} A Hot bowl of Cazuela",
                "{N} hands {T} A Hot bowl of Chicken Noodle Soup",
                "{N} hands {T} A Hot bowl of Cock-a-leekie",
                "{N} hands {T} A Hot bowl of Fufu and Egusi soup",
                "{N} hands {T} A Hot bowl of Gomguk ",
                "{N} hands {T} A Hot bowl of Goulash soup ",
                "{N} hands {T} A Hot bowl of Gumbo",
                "{N} hands {T} A Hot bowl of Hot and sour soup ",
                "{N} hands {T} A Hot bowl of Kharcho",
                "{N} hands {T} A Hot bowl of Kimchi Guk ",
                "{N} hands {T} A Hot bowl of Lagman",
                "{N} hands {T} A Hot bowl of Leek soup",
                "{N} hands {T} A Hot bowl of Lentil soup",
                "{N} hands {T} A Hot bowl of Matzah ball soup",
                "{N} hands {T} A Hot bowl of Menudo",
                "{N} hands {T} A Hot bowl of Minestrone",
                "{N} hands {T} A Hot bowl of Miyeok guk",
                "{N} hands {T} A Hot bowl of Milligatawny",
                "{N} hands {T} A Hot bowl of Barley soup",
                "{N} hands {T} A Hot bowl of Nettle soup",
                "{N} hands {T} A Hot bowl of Oxtail soup",
                "{N} hands {T} A Hot bowl of Pozole soup",
                "{N} hands {T} A Hot bowl of Pumpkin soup",
                "{N} hands {T} A Hot bowl of Samgyetang soup",
                "{N} hands {T} A Hot bowl of Snert soup",
                "{N} hands {T} A Hot bowl of Corn chowder",
                "{N} hands {T} A Hot bowl of French onion soup",
                "{N} hands {T} A Hot bowl of Lobster stew",
                "{N} hands {T} A Hot bowl of Miso soup",
                "{N} hands {T} A Hot bowl of She-crab soup ",
                "{N} hands {T} A Hot bowl of Tomato Soup ",
                "{N} hands {T} A Hot bowl of Tteokguk soup",
                "{N} hands {T} A Hot bowl of Winter mellon soup",
                "{N} hands {T} A Hot bowl of Crab Gaxpacho soup ",
                "{N} hands {T} A Hot bowl of Salmorejo soup",
                "{N} hands {T} A Hot bowl of Tarator soup",
                "{N} hands {T} A Hot bowl of New England clam chowder "
                
            ];

        out = "{}".format(random.choice(soup))
        out = out.replace("{N}", nick)
        out = out.replace("{T}", target)

        message(out)
