from util import text

def format_time(seconds, count=3, accuracy=6, simple=False):
    if simple:
        periods = [
                ('c', 60 * 60 * 24 * 365 * 100),
                ('de', 60 * 60 * 24 * 365 * 10),
                ('y', 60 * 60 * 24 * 365),
                ('m', 60 * 60 * 24 * 30),
                ('d', 60 * 60 * 24),
                ('h', 60 * 60),
                ('m', 60),
                ('s', 1)
                ]
    else:
        periods = [
                (('century', 'centuries'), 60 * 60 * 24 * 365 * 100),
                (('decade', 'decades'), 60 * 60 * 24 * 365 * 10),
                (('year', 'years'), 60 * 60 * 24 * 365),
                (('month', 'months'), 60 * 60 * 24 * 30),
                (('day', 'days'), 60 * 60 * 24),
                (('hour', 'hours'), 60 * 60),
                (('minute', 'minutes'), 60),
                (('second', 'seconds'), 1)
                ]

    periods = periods[-accuracy:]

    strings = []
    i = 0
    for period_name, period_seconds in periods:
        if i < count:
            if seconds > period_seconds:
                    period_value, seconds = divmod(seconds, period_seconds)
                    i += 1
                    if simple:
                        strings.append("{}{}".format(period_value, period_name))
                    else:
                        if period_value == 1:
                            strings.append("{} {}".format(period_value, period_name[0]))
                        else:
                            strings.append("{} {}".format(period_value, period_name[1]))
        else:
            break

    if simple:
        return " ".join(strings)
    else:
        return text.get_text_list(strings, "and")