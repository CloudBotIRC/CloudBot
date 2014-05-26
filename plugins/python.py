from cloudbot import hook
from cloudbot.util.pyexec import eval_py


@hook.command
def python(text):
    """python <prog> -- Executes <prog> as Python code."""

    return eval_py(text)
