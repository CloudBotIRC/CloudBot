from util import hook
import re
import random

potatoes = ['AC Belmont', 'AC Blue Pride', 'AC Brador', 'AC Chaleur', 'AC Domino', 'AC Dubuc', 'AC Glacier Chip', 'AC Maple Gold', 'AC Novachip', 'AC Peregrine Red', 'AC Ptarmigan', 'AC Red Island', 'AC Saguenor', 'AC Stampede Russet', 'AC Sunbury', 'Abeille', 'Abnaki', 'Acadia', 'Acadia Russet', 'Accent', 'Adirondack Blue', 'Adirondack Red', 'Adora', 'Agria', 'All Blue', 'All Red', 'Alpha', 'Alta Russet', 'Alturas Russet', 'Amandine', 'Amisk', 'Andover', 'Anoka', 'Anson', 'Aquilon', 'Arran Consul', 'Asterix', 'Atlantic', 'Austrian Crescent', 'Avalanche', 'Banana', 'Bannock Russet', 'Batoche', 'BeRus', 'Belle De Fonteney', 'Belleisle', 'Bintje', 'Blossom', 'Blue Christie', 'Blue Mac', 'Brigus', 'Brise du Nord', 'Butte', 'Butterfinger', 'Caesar', 'CalWhite', 'CalRed', 'Caribe', 'Carlingford', 'Carlton', 'Carola', 'Cascade', 'Castile', 'Centennial Russet', 'Century Russet', 'Charlotte', 'Cherie', 'Cherokee', 'Cherry Red', 'Chieftain', 'Chipeta', 'Coastal Russet', 'Colorado Rose', 'Concurrent', 'Conestoga', 'Cowhorn', 'Crestone Russet', 'Crispin', 'Cupids', 'Daisy Gold', 'Dakota Pearl', 'Defender', 'Delikat', 'Denali', 'Desiree', 'Divina', 'Dundrod', 'Durango Red', 'Early Rose', 'Elba', 'Envol', 'Epicure', 'Eramosa', 'Estima', 'Eva', 'Fabula', 'Fambo', 'Fremont Russet', 'French Fingerling', 'Frontier Russet', 'Fundy', 'Garnet Chile', 'Gem Russet', 'GemStar Russet', 'Gemchip', 'German Butterball', 'Gigant', 'Goldrush', 'Granola', 'Green Mountain', 'Haida', 'Hertha', 'Hilite Russet', 'Huckleberry', 'Hunter', 'Huron', 'IdaRose', 'Innovator', 'Irish Cobbler', 'Island Sunshine', 'Ivory Crisp', 'Jacqueline Lee', 'Jemseg', 'Kanona', 'Katahdin', 'Kennebec', "Kerr's Pink", 'Keswick', 'Keuka Gold', 'Keystone Russet', 'King Edward VII', 'Kipfel', 'Klamath Russet', 'Krantz', 'LaRatte', 'Lady Rosetta', 'Latona', 'Lemhi Russet', 'Liberator', 'Lili', 'MaineChip', 'Marfona', 'Maris Bard', 'Maris Piper', 'Matilda', 'Mazama', 'McIntyre', 'Michigan Purple', 'Millenium Russet', 'Mirton Pearl', 'Modoc', 'Mondial', 'Monona', 'Morene', 'Morning Gold', 'Mouraska', 'Navan', 'Nicola', 'Nipigon', 'Niska', 'Nooksack', 'NorValley', 'Norchip', 'Nordonna', 'Norgold Russet', 'Norking Russet', 'Norland', 'Norwis', 'Obelix', 'Ozette', 'Peanut', 'Penta', 'Peribonka', 'Peruvian Purple', 'Pike', 'Pink Pearl', 'Prospect', 'Pungo', 'Purple Majesty', 'Purple Viking', 'Ranger Russet', 'Reba', 'Red Cloud', 'Red Gold', 'Red La Soda', 'Red Pontiac', 'Red Ruby', 'Red Thumb', 'Redsen', 'Rocket', 'Rose Finn Apple', 'Rose Gold', 'Roselys', 'Rote Erstling', 'Ruby Crescent', 'Russet Burbank', 'Russet Legend', 'Russet Norkotah', 'Russet Nugget', 'Russian Banana', 'Saginaw Gold', 'Sangre', 'Sant�', 'Satina', 'Saxon', 'Sebago', 'Shepody', 'Sierra', 'Silverton Russet', 'Simcoe', 'Snowden', 'Spunta', "St. John's", 'Summit Russet', 'Sunrise', 'Superior', 'Symfonia', 'Tolaas', 'Trent', 'True Blue', 'Ulla', 'Umatilla Russet', 'Valisa', 'Van Gogh', 'Viking', 'Wallowa Russet', 'Warba', 'Western Russet', 'White Rose', 'Willamette', 'Winema', 'Yellow Finn', 'Yukon Gold']


@hook.command
def potato(inp, me=None, input=None):
    ".potato <user> - Makes <user> a tasty little potato."
    inp = inp.strip()

    if not re.match("^[A-Za-z0-9_|.-\]\[]*$", inp.lower()):
        return "I cant make a tasty potato for that user!"

    potato_type = random.choice(potatoes)
    size = random.choice(['small', 'little', 'mid-sized', 'medium-sized', 'large', 'gigantic'])
    flavor = random.choice(['tasty', 'delectable', 'delicious', 'yummy', 'toothsome', 'scrumptious', 'luscious'])
    method = random.choice(['bakes', 'fries', 'boils', 'microwaves'])

    me("%s a %s %s %s potato for %s!" % (method, flavor, size, potato_type, inp))
