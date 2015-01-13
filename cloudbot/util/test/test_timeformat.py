from cloudbot.util.timeformat import format_time, timesince, timeuntil


def test_format_time():
    # basic
    assert format_time(120000) == "1 day, 9 hours and 20 minutes"
    assert format_time(120000, simple=True) == "1d 9h 20m"
    # count
    assert format_time(1200003, count=4) == "13 days, 21 hours, 20 minutes and 3 seconds"
    assert format_time(1200000, count=4) == "13 days, 21 hours and 20 minutes"
    assert format_time(1200000, count=2) == "13 days and 21 hours"