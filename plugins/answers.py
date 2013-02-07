from util import hook, web, text


@hook.command
def answer(inp):
    ".answer <query> -- find the answer to a question on Yahoo! Answers"

    query = "SELECT Subject, ChosenAnswer, Link FROM answers.search WHERE query=@query LIMIT 1"
    result = web.query(query, {"query": inp.strip()}).one()

    short_url = web.isgd(result["Link"])

    # we split the answer and .join() it to remove newlines/extra spaces
    answer = text.truncate_str(' '.join(result["ChosenAnswer"].split()), 80)

    return u'\x02{}\x02 "{}" - {}'.format(result["Subject"], answer, short_url)