import os
import re
import platform
from util import hook


def replace(text, wordDic):
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)

@hook.command("memory", autohelp=False)
@hook.command(autohelp=False)
def mem(inp):
    ".mem -- Display the bot's current memory usage."
    if os.name == 'posix':
        status_file = open("/proc/%d/status" % os.getpid()).read()
        line_pairs = re.findall(r"^(\w+):\s*(.*)\s*$", status_file, re.M)
        status = dict(line_pairs)
        checked_stats = 'VmRSS VmSize VmPeak VmStk'.split()
        stats = '\x02, '.join(key + ': \x02' + status[key] for key in checked_stats)
        pretty_names = {'VmRSS': 'Real Memory', 'VmSize': 'Allocated Memory', 'VmPeak': 'Peak Allocated Memory', 'VmStk': 'Stack Size'}
        stats = replace(stats, pretty_names)
        return stats
    elif os.name == 'nt':
        cmd = "tasklist /FI \"PID eq %s\" /FO CSV /NH" % os.getpid()
        out = os.popen(cmd).read()

        total = 0
        for amount in re.findall(r'([,0-9]+) K', out):
            total += int(amount.replace(',', ''))

        return '\x02Memory Usage: %s kB\x02' % total

    return mem.__doc__

@hook.command("system", autohelp=False)
@hook.command(autohelp=False)
def sys(inp):
    ".sys -- Retrieves information about the host system."
    python_version = platform.python_version()
    os = platform.platform(aliased=True)
    cpu = platform.machine()
    return "Platform: %s, Python Version: %s, CPU: %s" % (os, python_version, cpu)
