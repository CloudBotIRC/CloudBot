import time

from cloudbot import hook


@hook.command(autohelp=False)
def beats(text):
    """beats -- Gets the current time in .beats (Swatch Internet Time). """

    if text.lower() == "wut":
        return "Instead of hours and minutes, the mean solar day is divided " \
               "up into 1000 parts called \".beats\". Each .beat lasts 1 minute and" \
               " 26.4 seconds. Times are notated as a 3-digit number out of 1000 af" \
               "ter midnight. So, @248 would indicate a time 248 .beats after midni" \
               "ght representing 248/1000 of a day, just over 5 hours and 57 minute" \
               "s. There are no timezones."
    elif text.lower() == "guide":
        return "1 day = 1000 .beats, 1 hour = 41.666 .beats, 1 min = 0.6944 .beats, 1 second = 0.01157 .beats"

    t = time.gmtime()
    h, m, s = t.tm_hour, t.tm_min, t.tm_sec

    utc = 3600 * h + 60 * m + s
    bmt = utc + 3600  # Biel Mean Time (BMT)

    beat = bmt / 86.4

    if beat > 1000:
        beat -= 1000

    return "Swatch Internet Time: @%06.2f" % beat
