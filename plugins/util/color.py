# Colors. Plugin by blha303, color/control id info from http://stackoverflow.com/a/13382032

colors = {'white': '0', 'black': '1', 'darkblue': '2', 'darkgreen': '3',
          'red': '4', 'darkred': '5', 'darkviolet': '6', 'orange': '7',
          'yellow': '8', 'lightgreen': '9', 'cyan': '10', 'lightcyan': '11',
          'blue': '12', 'violet': '13', 'darkgray': '14', 'lightgray': '15'}

control = {'bold': '\x02', 'color': '\x03', 'italic': '\x09',
           'strikethrough': '\x13', 'reset': '\x0f', 'underline': '\x15',
           'underline2': '\x1f', 'reverse': '\x16'}


def color(color):
    return control['color'] + colors[color]

def bold():
    return control['bold']

def italic():
    return control['italic']

def strike():
    return control['strikethrough']

def reset():
    return control['reset']

def underline(other=False):
    if other:
        return control['underline2']
    else:
        return control['underline']

def reverse():
    return control['reverse']
