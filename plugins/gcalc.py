from util import hook, http


@hook.command("math")
@hook.command
def calc(inp):
    "calc <term> -- Calculate <term> with Google Calc."

    soup = http.get_soup('http://www.google.com/search', q=inp)

    result = soup.find('h2', {'class': 'r'})
    if not result:
        return "Could not calculate '%s'" % inp

    return result.contents[0]
