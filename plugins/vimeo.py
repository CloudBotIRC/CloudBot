from util import hook, http


@hook.regex(r'vimeo.com/([0-9]+)')
def vimeo_url(match):
    info = http.get_json('http://vimeo.com/api/v2/video/%s.json'
                         % match.group(1))

    if info:
        return ("\x02%(title)s\x02 - length \x02%(duration)ss\x02 - "
                "\x02%(stats_number_of_likes)s\x02 likes - "
                "\x02%(stats_number_of_plays)s\x02 plays - "
                "\x02%(user_name)s\x02 on \x02%(upload_date)s\x02"
                % info[0])
