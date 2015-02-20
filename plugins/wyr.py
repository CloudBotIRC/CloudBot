import requests

from cloudbot import hook

API_URL = "http://www.rrrather.com/botapi"


@hook.command("wyr", "wouldyourather")
def wyr(bot):
    headers = {"User-Agent": bot.user_agent}

    r = requests.get(url=API_URL, headers=headers)
    data = r.json()

    # decrapify text
    title = data['title'].strip().capitalize().rstrip('.?,')
    choice1 = data['choicea'].strip().lower().rstrip('.?,!').lstrip('.')
    choice2 = data['choiceb'].strip().lower().rstrip('.?,!').lstrip('.')
    link = data['link']

    # get all the words in the answers
    text = choice1.split() + choice2.split()
    text = [word for word in text if word != "a"]

    title_text = title.split()

    print(str(title_text))
    print(str(text))

    dupl_count = 0

    for word in title_text:
        dupl_count += text.count(word)

    print(str(dupl_count / len(text)))

    title = title.replace(" u ", " you ")

    # detect if the answers are also in the question
    # if so, replace question with a generic one
    if dupl_count / len(text) >= 0.6:
        title = "Would you rather"

    return "{}... {} \x02OR\x02 {}? - {}".format(title, choice1, choice2, link)
