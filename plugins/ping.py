# ping plugin by neersighted
from util import hook
import subprocess
import re
import os

ping_regex = re.compile(r"(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)")


@hook.command
def ping(inp, reply=None):
    ".ping <host> [count] -- Pings <host> [count] times."
    
    if os.name == "nt":
    return "Sorry, this command is not supported on Windows systems."

    args = inp.split(' ')
    host = args[0]

    # check for a seccond argument and set the ping count
    if len(args) > 1:
        count = int(args[1])
        if count > 20:
            count = 20
    else:
        count = 5

    count = str(count)

    host = re.sub(r'([^\s\w\.])+', '', host)

    reply("Attempting to ping %s %s times..." % (host, count))

    pingcmd = subprocess.check_output(["ping", "-c", count, host])
    if "request timed out" in pingcmd or "unknown host" in pingcmd:
        return "error: could not ping host"
    else:
        m = re.search(ping_regex, pingcmd)
        return "min: %sms, max: %sms, average: %sms, range: %sms, count: %s" \
        % (m.group(1), m.group(3), m.group(2), m.group(4), count)
