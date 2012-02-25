from util import http, hook

api_root = 'http://api.rottentomatoes.com/api/public/v1.0/'
movie_search_url = api_root+'movies.json?q=%s&apikey=%s'
movie_info_url = api_root+'movies/%s.json?apikey=%s'
movie_reviews_url = api_root+'movies/%s/reviews.json?apikey=%s&review_type=all'

response = u"%s - critics: \x02%d%%\x02 (%d\u2191%d\u2193) audience: \x02%d%%\x02 - %s"


@hook.command('rt')
def rottentomatoes(inp, bot=None):
    '.rt <title> -- gets ratings for <title> from Rotten Tomatoes'

    api_key = bot.config.get("api_keys", {}).get("rottentomatoes", None)
    if not api_key:
        return None

    title = inp.strip()

    results = http.get_json(movie_search_url % (http.quote_plus(title), api_key))
    if results['total'] > 0:
        movie = results['movies'][0]
        title = movie['title']
        id = movie['id']
        critics_score = movie['ratings']['critics_score']
        audience_score = movie['ratings']['audience_score']
        url = movie['links']['alternate']

        if critics_score != -1:
            reviews = http.get_json(movie_reviews_url%(id, api_key))
            review_count = reviews['total']

            fresh = critics_score * review_count / 100
            rotten = review_count - fresh

            return response % (title, critics_score, fresh, rotten, audience_score, url)
