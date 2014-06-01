from cloudbot import hook
from cloudbot.util.pyexec import eval_py


@hook.command(["python", "py"])
def python(text):
    """<python code> - executes <python code> using eval.appspot.com"""

    return eval_py(text)
