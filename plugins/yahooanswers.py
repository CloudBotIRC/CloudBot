from cloudbot import hook
from cloudbot.util import web, formatting


@hook.command()
def answer(text):
    """answer <query> -- find the answer to a question on Yahoo! Answers"""

    query = "SELECT Subject, ChosenAnswer, Link FROM answers.search WHERE query=@query LIMIT 1"
    result = web.query(query, {"query": text.strip()}).one()

    short_url = web.try_shorten(result["Link"])

    # we split the answer and .join() it to remove newlines/extra spaces
    answer_text = formatting.truncate_str(' '.join(result["ChosenAnswer"].split()), 80)

    return '\x02{}\x02 "{}" - {}'.format(result["Subject"], answer_text, short_url)
