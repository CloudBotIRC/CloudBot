""" formatting.py - handy functions for formatting text """


def capitalize_first(line):
    """ capitalises the first letter of words
        (keeps other letters intact)
    """
    return ' '.join([s[0].upper() + s[1:] for s in line.split(' ')])
