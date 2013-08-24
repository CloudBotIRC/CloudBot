from util import hook, http, timeformat


@hook.regex(r'vimeo.com/([0-9]+)')
def vimeo_url(match):
    "vimeo <url> -- returns information on the Vimeo video at <url>"
    info = http.get_json('http://vimeo.com/api/v2/video/%s.json' % match.group(1))

    if info:
        info = info[0]
        return ("\x02{title}\x02 - length \x02{duration}\x02 - "
                "\x02{likes}\x02 likes - "
                "\x02{plays}\x02 plays - "
                "\x02{username}\x02 on \x02{uploaddate}\x02".format(
                    title=info["title"],
                    duration=timeformat.timeformat(info["duration"]),
                    likes=info["stats_number_of_likes"],
                    plays=info["stats_number_of_plays"],
                    username=info["user_name"],
                    uploaddate=info["upload_date"])
               )
