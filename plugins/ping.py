# ping plugin by neersighted
from util import hook
import subprocess
import re


@hook.command
def ping(inp):
    ".ping <host> [count] -- Pings <host> [count] times."

    args = inp.split(' ')
    host = args[0]

    if len(args) > 1:
        count = args[1]
        count = int(count)
        if count > 20:
            count = 20
    else:
        count = 5

    count = str(count)

    pingcmd = subprocess.check_output("ping -c "\
                                    + count + " " + host, shell=True)
    if 'request timed out' in pingcmd or 'unknown host' in pingcmd:
        return "error: could not ping host"
    else:
        m = re.search(r"rtt min/avg/max/mdev = "\
            "(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)", pingcmd)
        return "min: %sms, max: %sms, average: %sms, range: %sms, count: %s"\
        % (m.group(1), m.group(2), m.group(3), m.group(4), count)
