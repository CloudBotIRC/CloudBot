from cloudbot import hook
from cloudbot.util import web


@hook.command
def python(text):
    """python <input> -- Executes <input> as Python code."""

    output = web.pyeval(text, pastebin=False)

    if '\n' in output:
        if 'Traceback (most recent call last):' in output:
            status = 'Error: '
        else:
            status = 'Success: '
        return status + web.paste(output)
    else:
        return output