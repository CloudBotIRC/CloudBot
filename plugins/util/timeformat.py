def timeformat(seconds):
    days = seconds / 86400
    seconds -= 86400 * days
    hours = seconds / 3600
    seconds -= 3600 * hours
    minutes = seconds / 60
    seconds -= 60 * minutes
    if days != 0:
        return "%s, %02d:%02d:%02d" % (str(days) + " days" if days > 1 else str(days) + " day", hours, minutes, seconds)
    elif hours == 0 and minutes != 0:
        return "%02d:%02d" % (minutes, seconds)
    elif hours == 0 and minutes == 0:
        return "%02d" % seconds
    return "%02d:%02d:%02d" % (hours, minutes, seconds)
