import requests

from cloudbot import hook

headers = {'User-Agent': 'CloudBot/dev 1.0 - CloudBot Refresh by lukeroge'}

@hook.command
def wyr(text, message):
    url = "http://www.rrrather.com/botapi"

    r = requests.get(url, headers=headers)
    data = r.json()
    title = data['title'].strip().capitalize()
    title = title.rstrip('.?')
    choice1 = data['choicea'].strip().lower()
    choice1 = choice1.rstrip('.?')
    choice2 = data['choiceb'].strip().lower()
    choice2 = choice2.rstrip('.?')
    link = data['link']

    text = "{} {}".format(choice1, choice2).split()
    text = [ word for word in text if word != "a" ]

    title_text = title.split()

    #message(str(title_text))
    #message(str(text))

    dupl_count = 0

    for word in title_text:
        dupl_count += text.count(word)

    #message(str(dupl_count / len(text)))

    if title.lower() == "would u rather":
        title = "Would you rather"

    if dupl_count / len(text) >= 0.6:
        title = "Would you rather"
    else:
        pass

    return "{}... {} \x02OR\x02 {}? - {}".format(title, choice1, choice2, link)