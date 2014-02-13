from util import hook, http, web


@hook.command(autohelp=False)
def fact(inp):
    """fact -- Gets a random fact from OMGFACTS."""

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

    url = web.try_isgd(link)

    return "{} - {}".format(fact_data, url)
