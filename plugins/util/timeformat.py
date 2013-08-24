def timeformat(seconds):
    days = seconds / 86400
    seconds -= 86400 * days
    hours = seconds / 3600
    seconds -= 3600 * hours
    minutes = seconds / 60
    seconds -= 60 * minutes
    if days != 0:
        return "%sd %sh %sm %ss" % (days, hours, minutes, seconds)
    elif hours == 0 and minutes != 0:
        return "%sm %ss" % (minutes, seconds)
    elif hours == 0 and minutes == 0:
        return "%ss" % seconds
    return "%sh %sm %ss" % (hours, minutes, seconds)
