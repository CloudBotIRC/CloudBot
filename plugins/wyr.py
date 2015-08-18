"""
wyr.py

A plugin that uses the RRRather.com API to return random "Would you rather" questions.

Created By:
    - Foxlet <http://furcode.co/>
    - Luke Rogers <https://github.com/lukeroge>

Special Thanks:
    - http://www.rrrather.com/ for adding extra features to their API to make this command possible

License:
    BSD 3-Clause License
"""

import requests

from cloudbot import hook

API_URL = "http://www.rrrather.com/botapi"
FILTERED_TAGS = ()


def get_wyr(headers):
    """ Gets a entry from the RRRather API and cleans up the data """
    r = requests.get(url=API_URL, headers=headers)
    data = r.json()

    # clean up text
    data['title'] = data['title'].strip().capitalize().rstrip('.?,:')
    data['choicea'] = data['choicea'].strip().lower().rstrip('.?,!').lstrip('.')
    data['choiceb'] = data['choiceb'].strip().lower().rstrip('.?,!').lstrip('.')

    if data['tags']:
        data['tags'] = data['tags'].lower().split(',')
    else:
        data['tags'] = []

    if data['nsfw']:
        data['tags'].append('nsfw')

    return data


@hook.command("wyr", "wouldyourather", autohelp=False)
def wyr(bot):
    """ -- What would you rather do? """
    headers = {"User-Agent": bot.user_agent}

    # keep trying to get entries until we find one that is not filtered
    while True:
        data = get_wyr(headers)

        if [i for i in FILTERED_TAGS if i in data['tags']]:
            continue
        else:
            break

    # get a list of all the words in the answers
    text = data['choicea'].split() + data['choiceb'].split()
    text = [word for word in text if word != "a"]

    title_text = data['title'].split()

    dupl_count = 0
    for word in title_text:
        dupl_count += text.count(word)

    data['title'] = data['title'].replace(" u ", " you ")

    # detect if the answers are also in the question
    # if so, replace question with a generic one
    if dupl_count / len(text) >= 0.6:
        data['title'] = "Would you rather"

    return "{title}... {choicea} \x02OR\x02 {choiceb}? - {link}".format(**data)
