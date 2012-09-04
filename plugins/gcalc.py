from util import hook, http


@hook.command("math")
@hook.command
def calc(inp):
    "calc <term> -- Calculate <term> with Google Calc."

    soup = http.get_soup('http://www.google.com/search', q=inp)

    response = soup.find('h2', {'class': 'r'})
    if response is None:
        return "Could not calculate '%s'" % inp

    return http.unescape(response.contents[0])
