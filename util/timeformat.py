from util import text

def format_time(seconds, count=3, accuracy=6, simple=False):
    """
    Takes a length of time in seconds and returns a string describing that length of time.
    This function has a number of optional arguments that can be combined:

    SIMPLE: displays the time in a simple format
    >>> format_time(SECONDS)
    1 hour, 2 minutes and 34 seconds
    >>> format_time(SECONDS, simple=True)
    1h 2m 34s

    COUNT: how many periods should be shown (default 3)
    >>> format_time(SECONDS)
    147 years, 9 months and 8 weeks
    >>> format_time(SECONDS, count=6)
    147 years, 9 months, 7 weeks, 18 hours, 12 minutes and 34 seconds
    """

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