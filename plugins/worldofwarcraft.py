"""
wow.py:
Written by Zarthus <zarthus@zarth.us> May 30, 2014.
Gets data from the World of Warcraft Armoury API

Commands:
armoury, armory: Request data from the armoury API and format it into something human readable.
"""

import re

import requests

from cloudbot import hook
from cloudbot.util import web


def wow_armoury_data(link):
    """Sends the API request, and returns the data accordingly (in json if raw, nicely formatted if not)."""
    try:
        data = requests.get(link)
    except Exception as e:
        return 'Unable to fetch information for {}. Does the realm or character exist? ({})'.format(link, str(e))

    return wow_armoury_format(data, link)


def wow_armoury_format(data, link):
    """Format armoury data into a human readable string"""

    if data.status_code != 200 and data.status_code != 404:
        # The page returns 404 if the character or realm is not found.
        try:
            data.raise_for_status()
        except Exception as e:
            return 'An error occurred while trying to fetch the data. ({})'.format(str(e))

    data = data.json()

    if len(data) == 0:
        return 'Could not find any results.'

    if 'reason' in data:
        # Something went wrong (i.e. realm does not exist, character does not exist, or page not found).
        return data['reason']

    if 'name' in data:
        nice_url = link.replace('/api/wow/', '/wow/en/') + '/simple'

        try:
            return '{} is a level \x0307{}\x0F {} {} on {} with \x0307{}\x0F achievement points and \x0307{}' \
                   '\x0F honourable kills. Armoury Profile: {}' \
                .format(data['name'], data['level'], wow_get_gender(data['gender']), wow_get_class(data['class'], True),
                        data['realm'], data['achievementPoints'], data['totalHonorableKills'], web.shorten(nice_url))
        except Exception as e:
            return 'Unable to fetch information for {}. Does the realm or ' \
                   'character exist? ({})'.format(nice_url, str(e))

    return 'An unexpected error occurred.'


def wow_get_gender(gender_id):
    """Formats a gender ID to a readable gender name"""
    gender = 'unknown'

    if gender_id == 0:
        gender = 'male'
    elif gender_id == 1:
        gender = 'female'

    return gender


def wow_get_class(class_id, colours=False):
    """Formats a class ID to a readable name, data from http://eu.battle.net/api/wow/data/character/classes"""
    if colours:
        # Format their colours according to class colours.
        class_ids = {
            1: "\x0305Warrior\x0F", 2: "\x0313Paladin\x0F", 3: "\x0303Hunter\x0F", 4: "\x0308Rogue\x0F",
            5: "Priest", 6: "\x0304Death Knight\x0F", 7: "\x0310Shaman\x0F", 8: "\x0311Mage\x0F",
            9: "\x0306Warlock\x0F", 10: "\x0309Monk\x0F", 11: "\x0307Druid\x0F"
        }
    else:
        class_ids = {
            1: "Warrior", 2: "Paladin", 3: "Hunter", 4: "Rogue", 5: "Priest",
            6: "Death Knight", 7: "Shaman", 8: "Mage", 9: "Warlock", 10: "Monk",
            11: "Druid"
        }

    if class_id in class_ids:
        return class_ids[class_id]
    else:
        return 'unknown'


def wow_get_race(race_id):
    """Formats a race ID to a readable race name, data from http://eu.battle.net/api/wow/data/character/races"""
    race_ids = {
        1: "Human", 2: "Orc", 3: "Dwarf", 4: "Night Elf", 5: "Undead", 6: "Tauren", 7: "Gnome",
        8: "Troll", 9: "Goblin", 10: "Blood Elf", 11: "Draenei", 22: "Worgen",
        24: "Pandaren (neutral)", 25: "Pandaren (alliance)", 26: "Pandaren (horde)"
    }

    if race_id in race_ids:
        return race_ids[race_id]
    else:
        return 'unknown'


def wow_region_shortname(region):
    """Returns a short region name, which functions as battle.net their subdomain (i.e. eu.battle.net)"""
    valid_regions = {
        'eu': 'eu', 'europe': 'eu',
        'us': 'us',
        'sea': 'sea', 'asia': 'sea',
        'kr': 'kr', 'korea': 'kr',
        'tw': 'tw', 'taiwan': 'tw'
    }

    if region in valid_regions:
        return valid_regions[region]
    else:
        return False


@hook.command('armory', 'armoury')
def armoury(text):
    """armoury [realm] [character name] [region = EU] - Look up character and returns API data."""

    # Splits the input, builds the API url, and returns the formatted data to user.
    split_input = text.lower().split()

    if len(split_input) < 2:
        return 'armoury [realm] [character name] [region = EU] - Look up character and returns API data.'

    realm = split_input[0].replace('_', '-')
    char_name = split_input[1]

    # Sets the default region to EU if none specified.
    if len(split_input) < 3:
        region = 'eu'
    else:
        region = split_input[2]

    if not re.match(r"^[a-z]{1,3}$", region):
        return 'The region specified is not a valid region. Valid regions: eu, us, sea, kr, tw.'

    if re.match(r"^[^\d]$", char_name) or len(char_name) > 18:
        # May not contain digits, repeat the same letter three times, or contain non-word characters.
        # Special characters are permitted, such as áéíóßø.
        return 'The character name is not a valid name. Character names can only contain letters, special characters,' \
               ' and be 18 characters long.'

    if not re.match(r"^[a-z' _-]{3,32}$", realm):
        # Realm names can have spaces in them, use dashes for this.
        return 'The realm name is not a valid name. Realm names can only contain letters, dashes, and apostrophes, up' \
               ' to 32 characters'

    region_short = wow_region_shortname(region)

    if not region_short:
        return 'The region \'{}\' does not exist.'.format(region)

    link = "http://{}.battle.net/api/wow/character/{}/{}".format(region, realm, char_name)

    return wow_armoury_data(link)
