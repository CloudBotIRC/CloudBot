"""
timeformat.py

Contains functions to format time periods. Based on code from the Django project and CloudBot contributors.

The licensing for this module isn't solid, because I started working on this module before I had a proper
system for tracking code licences. If your code is in this file and you have any queries, contact me by
email at <lukeroge@gmail.com>!

Maintainer:
    - Luke Rogers <https://github.com/lukeroge>

License:
    BSD license

    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice,
           this list of conditions and the following disclaimer.

        2. Redistributions in binary form must reproduce the above copyright
           notice, this list of conditions and the following disclaimer in the
           documentation and/or other materials provided with the distribution.

        3. Neither the name of Django nor the names of its contributors may be used
           to endorse or promote products derived from this software without
           specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import datetime

from cloudbot.util import formatting


def time_since(d, now=None, count=2, accuracy=6, simple=False):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes". If d occurs after now,
    then "0 minutes" is returned.
    This function has a number of optional arguments that can be combined:

    SIMPLE: displays the time in a simple format
    >> timesince(SECONDS)
    1 hour, 2 minutes and 34 seconds
    >> timesince(SECONDS, simple=True)
    1h 2m 34s

    COUNT: how many periods should be shown (default 3)
    >> timesince(SECONDS)
    147 years, 9 months and 8 weeks
    >> timesince(SECONDS, count=6)
    147 years, 9 months, 7 weeks, 18 hours, 12 minutes and 34 seconds
    """

    # Convert int or float (unix epoch) to datetime.datetime for comparison
    if isinstance(d, int) or isinstance(d, float):
        d = datetime.datetime.fromtimestamp(d)

    if isinstance(now, int) or isinstance(now, float):
        now = datetime.datetime.fromtimestamp(now)

    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now()

    # ignore microsecond part of 'd' since we removed it from 'now'
    delta = now - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds

    if since <= 0:
        # d is in the future compared to now, stop processing.
        return '0 ' + 'minutes'

    # pass the number in seconds on to format_time to make the output string
    return format_time(since, count, accuracy, simple)

# compatibility
timesince = time_since


def time_until(d, now=None, count=2, accuracy=6, simple=False):
    """
    Like timesince, but returns a string measuring the time until
    the given time.
    """
    if not now:
        now = datetime.datetime.now()
    return time_since(now, d, count, accuracy, simple)


# compatibility
timeuntil = time_until


def format_time(seconds, count=3, accuracy=6, simple=False):
    """
    Takes a length of time in seconds and returns a string describing that length of time.
    This function has a number of optional arguments that can be combined:

    SIMPLE: displays the time in a simple format
    >> format_time(SECONDS)
    1 hour, 2 minutes and 34 seconds
    >> format_time(SECONDS, simple=True)
    1h 2m 34s

    COUNT: how many periods should be shown (default 3)
    >> format_time(SECONDS)
    147 years, 9 months and 8 weeks
    >> format_time(SECONDS, count=6)
    147 years, 9 months, 7 weeks, 18 hours, 12 minutes and 34 seconds
    """

    if simple:
        periods = [
            ('c', 60 * 60 * 24 * 365 * 100),
            ('de', 60 * 60 * 24 * 365 * 10),
            ('y', 60 * 60 * 24 * 365),
            ('mo', 60 * 60 * 24 * 30),
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
        return formatting.get_text_list(strings, "and")
