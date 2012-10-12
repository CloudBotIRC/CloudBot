from util import hook, http, web


@hook.command(autohelp=False)
def fact(inp, say=False, nick=False):
    "fact -- Gets a random fact from OMGFACTS."

    attempts = 0

    # all of this is because omgfacts is fail
    while True:
        try:
            soup = http.get_soup('http://www.omg-facts.com/random')
        except:
            if attempts > 2:
                return "Could not find a fact!"
            else:
                attempts += 1
                continue

        response = soup.find('a', {'class': 'surprise'})
        link = response['href']
        fact = ''.join(response.find(text=True))

        if fact:
            fact = fact.strip()
            break
        else:
            if attempts > 2:
                return "Could not find a fact!"
            else:
                attempts += 1
                continue

    try:
        url = web.isgd(link)
    except (web.ShortenError, http.HTTPError):
        url = link

    return "%s - %s" % (fact, url)
