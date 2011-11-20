import re

from util import hook, http


re_lineends = re.compile(r'[\r\n]*')


@hook.command
def python(inp):
    ".python <prog> -- executes python code <prog>"

    inp = inp.replace("~n", "\n")

    res = http.get("http://eval.appspot.com/eval", statement=inp).splitlines()
	

    if len(res) == 0:
        return
    res[0] = re_lineends.split(res[0])[0]
    if not res[0] == 'Traceback (most recent call last):':
        return res[0].decode('utf8', 'ignore')
    else:
        return res[-1].decode('utf8', 'ignore')
