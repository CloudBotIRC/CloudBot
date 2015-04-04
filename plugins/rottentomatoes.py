import requests

from cloudbot import hook
from cloudbot.util import web

api_root = 'http://api.rottentomatoes.com/api/public/v1.0/'
movie_search_url = api_root + 'movies.json'
movie_reviews_url = api_root + 'movies/{}/reviews.json'


@hook.command('rottentomatoes', 'rt')
def rotten_tomatoes(text, bot):
    """rt <title> -- gets ratings for <title> from Rotten Tomatoes"""
    api_key = bot.config.get("api_keys", {}).get("rottentomatoes", None)
    if not api_key:
        return "No Rotten Tomatoes API key set."

    title = text.strip()
    params = {
        'q': title,
        'apikey': api_key
    }

    request = requests.get(movie_search_url, params=params)
    if request.status_code != requests.codes.ok:
        return "Error searching: {}".format(request.status_code)

    results = request.json()
    if results['total'] == 0:
        return 'No results.'

    movie = results['movies'][0]
    title = movie['title']
    movie_id = movie['id']
    critics_score = movie['ratings']['critics_score']
    audience_score = movie['ratings']['audience_score']
    url = web.try_shorten(movie['links']['alternate'])

    if critics_score == -1:
        return "\x02{}\x02 - Critics Rating: \x02No Reviews\x02, " \
               "Audience Rating: \x02{}%\x02 - {}".format(title, audience_score, url)

    review_params = {
        'review_type': 'all',
        'apikey': api_key
    }

    review_request = requests.get(movie_reviews_url.format(movie_id), params=review_params)
    if review_request.status_code != requests.codes.ok:
        return "Error searching: {}".format(review_request.status_code)

    reviews = review_request.json()
    review_count = reviews['total']

    fresh = int(critics_score * review_count / 100)
    rotten = review_count - fresh

    return "\x02{}\x02 - Critics Rating: \x02{}%\x02 ({} liked, {} disliked), " \
           "Audience Rating: \x02{}%\x02 - {}".format(title, critics_score, fresh, rotten, audience_score, url)
