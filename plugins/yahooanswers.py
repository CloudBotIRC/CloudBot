from util import hook, web, text


@hook.command
def answer(inp):
    """answer <query> -- find the answer to a question on Yahoo! Answers"""

    query = "SELECT Subject, ChosenAnswer, Link FROM answers.search WHERE query=@query LIMIT 1"
    result = web.query(query, {"query": inp.strip()}).one()

    short_url = web.try_isgd(result["Link"])

    # we split the answer and .join() it to remove newlines/extra spaces
    answer_text = text.truncate_str(' '.join(result["ChosenAnswer"].split()), 80)

    return u'\x02{}\x02 "{}" - {}'.format(result["Subject"], answer_text, short_url)
