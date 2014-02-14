from util import hook, http


@hook.command
def domainr(inp):
    """domainr <domain> - Use domain.nr's API to search for a domain, and similar domains."""
    try:
        data = http.get_json('http://domai.nr/api/json/search?q=' + inp)
    except (http.URLError, http.HTTPError) as e:
        return "Unable to get data for some reason. Try again later."
    if data['query'] == "":
        return "An error occurred: {status} - {message}".format(**data['error'])
    domains = ""
    for domain in data['results']:
        domains += ("\x034" if domain['availability'] == "taken" else (
                    "\x033" if domain['availability'] == "available" else "\x031")) + domain['domain'] + "\x0f" + domain[
                    'path'] + ", "
    return "Domains: " + domains
