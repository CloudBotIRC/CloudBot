def timeformat(seconds):
    if seconds < 60:
        timestamp = str(seconds) + "s"
    elif seconds >= 60 and seconds < 3600:
        timestamp = "%s:%s" % (seconds/60, seconds%60)
    elif seconds >= 3600 and seconds < 86400:
        hours = seconds / 3600
        seconds = 3600*hours
        timestamp = "%s:%s:%s" % (hours, seconds/60, seconds%60)
    elif seconds >= 86400:
        days = seconds / 86400
        seconds = 86400*days
        hours = seconds / 3600
        seconds = 3600*hours
        timestamp = "%s days, %s:%s:%s" % (days, hours, seconds/60, seconds%60)
    return timestamp
