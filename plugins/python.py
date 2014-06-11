from cloudbot import hook
from cloudbot.util import web


@hook.command("python", "py")
def python(text):
    """<python code> - executes <python code> using eval.appspot.com"""

    output = web.pyeval(text, pastebin=False)

    if '\n' in output:
        if 'Traceback (most recent call last):' in output:
            status = 'Error: '
        else:
            status = 'Success: '
        return status + web.paste(output)
    else:
        return output
