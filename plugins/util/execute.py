import http, web
import json, urllib2, sys


def eval_py(code, paste_multiline=True):
    while True:
        output = http.get("http://eval.appspot.com/eval", statement=code).rstrip('\n')
        if output:
            break
        else:
            pass

    if "Traceback (most recent call last):" in output:
        status = "Python error: "
    else:
        status = "Code executed sucessfully: "
        
    if "\n" in output and paste_multiline:
        return status + web.haste(output)
    else:
        return output