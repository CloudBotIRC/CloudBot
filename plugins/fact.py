from cloudbot import hook, http, web


@hook.command(autohelp=False)
def fact():
    """- gets a random fact from OMGFACTS"""

    attempts = 0

    # all of this is because omgfacts is fail
    while True:
        try:
            soup = http.get_soup('http://www.omg-facts.com/random')
        except (http.HTTPError, http.URLError):
            if attempts > 2:
                return "Could not find a fact!"
            else:
                attempts += 1
                continue

        response = soup.find('a', {'class': 'surprise'})
        link = response['href']
        fact_data = ''.join(response.find(text=True))

        if fact_data:
            fact_data = fact_data.strip()
            break
        else:
            if attempts > 2:
                return "Could not find a fact!"
            else:
                attempts += 1
                continue

    url = web.try_shorten(link)

    return "{} - {}".format(fact_data, url)
