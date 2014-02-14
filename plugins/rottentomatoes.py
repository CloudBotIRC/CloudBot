from util import http, hook

api_root = 'http://api.rottentomatoes.com/api/public/v1.0/'
movie_search_url = api_root + 'movies.json'
movie_reviews_url = api_root + 'movies/%s/reviews.json'


@hook.command('rt')
def rottentomatoes(inp, bot=None):
    """rt <title> -- gets ratings for <title> from Rotten Tomatoes"""

    api_key = bot.config.get("api_keys", {}).get("rottentomatoes", None)
    if not api_key:
        return "error: no api key set"

    title = inp.strip()

    results = http.get_json(movie_search_url, q=title, apikey=api_key)
    if results['total'] == 0:
        return 'No results.'

    movie = results['movies'][0]
    title = movie['title']
    movie_id = movie['id']
    critics_score = movie['ratings']['critics_score']
    audience_score = movie['ratings']['audience_score']
    url = movie['links']['alternate']

    if critics_score == -1:
        return

    reviews = http.get_json(movie_reviews_url % movie_id, apikey=api_key, review_type='all')
    review_count = reviews['total']

    fresh = critics_score * review_count / 100
    rotten = review_count - fresh

    return u"{} - Critics Rating: \x02{}%\x02 ({} liked, {} disliked) " \
           "Audience Rating: \x02{}%\x02 - {}".format(title, critics_score, fresh, rotten, audience_score, url)
