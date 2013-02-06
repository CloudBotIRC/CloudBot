from util import hook, web, text


@hook.command
def answer(inp):
    ".answer <query> -- find the answer to a question on Yahoo! Answers"

    query = "SELECT Subject, ChosenAnswer, Link FROM answers.search WHERE query=@query LIMIT 1"
    result = web.query(query, {"query": inp.strip()}).one()

    short_url = web.isgd(result["Link"])
    answer = text.truncate_str(result["ChosenAnswer"], 80)

    return u"\x02{}\x02 {} - {}".format(result["Subject"], answer, short_url)