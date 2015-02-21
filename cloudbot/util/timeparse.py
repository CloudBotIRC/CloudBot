"""
timeparse.py

Implements a single function, `timeparse`, which can parse various
kinds of time expressions.

Created By:
    - Will Roberts <wildwilhelm@gmail.com>

Maintainer:
    - Luke Rogers <https://github.com/lukeroge>

License:
    MIT License
    Copyright Will Roberts <wildwilhelm@gmail.com> - 1 February, 2014

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation files
    (the "Software"), to deal in the Software without restriction,
    including without limitation the rights to use, copy, modify, merge,
    publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
    BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import re

SIGN = r'(?P<sign>[+|-])?'

# YEARS      = r'(?P<years>\d+)\s*(?:ys?|yrs?.?|years?)'
# MONTHS     = r'(?P<months>\d+)\s*(?:mos?.?|mths?.?|months?)'
WEEKS = r'(?P<weeks>[\d.]+)\s*(?:w|wks?|weeks?)'
DAYS = r'(?P<days>[\d.]+)\s*(?:d|dys?|days?)'
HOURS = r'(?P<hours>[\d.]+)\s*(?:h|hrs?|hours?)'
MINS = r'(?P<mins>[\d.]+)\s*(?:m|(mins?)|(minutes?))'
SECS = r'(?P<secs>[\d.]+)\s*(?:s|secs?|seconds?)'
SEPARATORS = r'[,/]'
SEC_CLOCK = r':(?P<secs>\d{2}(?:\.\d+)?)'
MIN_CLOCK = r'(?P<mins>\d{1,2}):(?P<secs>\d{2}(?:\.\d+)?)'
HOUR_CLOCK = r'(?P<hours>\d+):(?P<mins>\d{2}):(?P<secs>\d{2}(?:\.\d+)?)'
DAY_CLOCK = (r'(?P<days>\d+):(?P<hours>\d{2}):'
             r'(?P<mins>\d{2}):(?P<secs>\d{2}(?:\.\d+)?)')

OPT = lambda x: r'(?:{x})?'.format(x=x, SEPARATORS=SEPARATORS)
OPT_SEP = lambda x: r'(?:{x}\s*(?:{SEPARATORS}\s*)?)?'.format(
    x=x, SEPARATORS=SEPARATORS)

TIME_FORMATS = [
    r'{WEEKS}\s*{DAYS}\s*{HOURS}\s*{MINS}\s*{SECS}'.format(
        # YEARS=OPT_SEP(YEARS),
        # MONTHS=OPT_SEP(MONTHS),
        WEEKS=OPT_SEP(WEEKS),
        DAYS=OPT_SEP(DAYS),
        HOURS=OPT_SEP(HOURS),
        MINS=OPT_SEP(MINS),
        SECS=OPT(SECS)),
    r'{MIN_CLOCK}'.format(
        MIN_CLOCK=MIN_CLOCK),
    r'{WEEKS}\s*{DAYS}\s*{HOUR_CLOCK}'.format(
        WEEKS=OPT_SEP(WEEKS),
        DAYS=OPT_SEP(DAYS),
        HOUR_CLOCK=HOUR_CLOCK),
    r'{DAY_CLOCK}'.format(
        DAY_CLOCK=DAY_CLOCK),
    r'{SEC_CLOCK}'.format(
        SEC_CLOCK=SEC_CLOCK),
]

MULTIPLIERS = dict([
    # ('years',  60 * 60 * 24 * 365),
    # ('months', 60 * 60 * 24 * 30),
    ('weeks', 60 * 60 * 24 * 7),
    ('days', 60 * 60 * 24),
    ('hours', 60 * 60),
    ('mins', 60),
    ('secs', 1)
])


def _interpret_as_minutes(string, mdict):
    """
    Times like "1:22" are ambiguous; do they represent minutes and seconds
    or hours and minutes?  By default, timeparse assumes the latter.  Call
    this function after parsing out a dictionary to change that assumption.
    
    >>> import pprint
    >>> pprint.pprint(_interpret_as_minutes('1:24', {'secs': '24', 'mins': '1'}))
    {'hours': '1', 'mins': '24'}
    """
    if (    string.count(':') == 1
            and '.' not in string
            and (('hours' not in mdict) or (mdict['hours'] is None))
            and (('days' not in mdict) or (mdict['days'] is None))
            and (('weeks' not in mdict) or (mdict['weeks'] is None))
    ):
        mdict['hours'] = mdict['mins']
        mdict['mins'] = mdict['secs']
        mdict.pop('secs')
        pass
    return mdict


def time_parse(string, granularity='seconds'):
    """
    Parse a time expression, returning it as a number of seconds.  If
    possible, the return value will be an `int`; if this is not
    possible, the return will be a `float`.  Returns `None` if a time
    expression cannot be parsed from the given string.

    Arguments:
    - `string`: the string value to parse

    >>> time_parse('1:24')
    84
    >>> time_parse(':22')
    22
    >>> time_parse('1 minute, 24 secs')
    84
    >>> time_parse('1m24s')
    84
    >>> time_parse('1.2 minutes')
    72
    >>> time_parse('1.2 seconds')
    1.2

    Time expressions can be signed.

    >>> time_parse('- 1 minute')
    -60
    >>> time_parse('+ 1 minute')
    60
    
    If granularity is specified as ``minutes``, then ambiguous digits following
    a colon will be interpreted as minutes; otherwise they are considered seconds.
    
    >>> time_parse('1:30')
    90
    >>> time_parse('1:30', granularity='minutes')
    5400
    """
    match = re.match(r'\s*' + SIGN + r'\s*(?P<unsigned>.*)$', string)
    sign = -1 if match.groupdict()['sign'] == '-' else 1
    string = match.groupdict()['unsigned']
    for timefmt in TIME_FORMATS:
        match = re.match(r'\s*' + timefmt + r'\s*$', string, re.I)
        if match and match.group(0).strip():
            mdict = match.groupdict()
            if granularity == 'minutes':
                mdict = _interpret_as_minutes(string, mdict)
            # if all of the fields are integer numbers
            if all(v.isdigit() for v in list(mdict.values()) if v):
                return sign * sum([MULTIPLIERS[k] * int(v, 10) for (k, v) in
                                   list(mdict.items()) if v is not None])
            # if SECS is an integer number
            elif ('secs' not in mdict or
                          mdict['secs'] is None or
                      mdict['secs'].isdigit()):
                # we will return an integer
                return (
                    sign * int(sum([MULTIPLIERS[k] * float(v) for (k, v) in
                                    list(mdict.items()) if k != 'secs' and v is not None])) +
                    (int(mdict['secs'], 10) if mdict['secs'] else 0))
            else:
                # SECS is a float, we will return a float
                return sign * sum([MULTIPLIERS[k] * float(v) for (k, v) in
                                   list(mdict.items()) if v is not None])