import http, web


def eval_py(code, paste_multiline=True):
    attempts = 0

    while True:
        try:
            output = http.get("http://eval.appspot.com/eval", statement=code).rstrip('\n')
        except http.HTTPError:
            if attempts > 2:
                return "Failed to execute code."
            else:
                attempts += 1
                continue
        break

    if "Traceback (most recent call last):" in output:
        status = "Python error: "
    else:
        status = "Code executed sucessfully: "

    if "\n" in output and paste_multiline:
        return status + web.haste(output)
    else:
        return output
