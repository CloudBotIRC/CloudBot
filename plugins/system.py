import os
import re
import time
import string
import platform
import subprocess
from util import hook

def replace(text, wordDic):
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)

def checkProc(checked_stats):
        status_file = open('/proc/self/status').read()
        line_pairs = re.findall(r'^(\w+):\s*(.*)\s*$', status_file, re.M)
        status = dict(line_pairs)
        checked_stats = checked_stats.split()
        stats = '\x02, '.join(key + ': \x02' + status[key] for key in checked_stats)
        return stats


@hook.command(autohelp=False)
def system(inp):
    ".system -- Retrieves information about the host system."
    name = platform.node()
    os = platform.platform()
    python_version = platform.python_implementation() + ' ' + platform.python_version()
    arch = '-'.join(platform.architecture())
    cpu = platform.machine()
    return 'Name: \x02%s\x02, Operating System: \x02%s\x02, Python Version: \x02%s\x02, Architecture: \x02%s\x02, CPU: \x02%s\x02' % (name, os, python_version, arch, cpu)


@hook.command(autohelp=False)
def memory(inp):
    ".memory -- Displays the bot's current memory usage."
    if os.name == 'posix':
        checked_stats = 'VmRSS VmSize VmPeak VmStk VmData'
        memory = checkProc(checked_stats)
        pretty_names = {'VmRSS': 'Real Memory', 'VmSize': 'Allocated Memory', 'VmPeak': 'Peak Allocated Memory', 'VmStk': 'Stack Size', 'VmData': 'Heap Size'}
        memory = replace(memory, pretty_names)
        memory = string.replace(memory, ' kB', '')
        memory = memory.split('\x02')
        numbers = [memory[i] for i in range(len(memory)) if i % 2 == 1]
        memory = [i for i in memory if i not in numbers]
        numbers = [str(round(float(i) / 1024, 2)) + ' MB' for i in numbers]
        memory = [list(i) for i in zip(memory, numbers)]
        memory = sum(memory, [])
        memory = '\x02'.join(memory)

    elif os.name == 'nt':
        cmd = 'tasklist /FI \"PID eq %s\" /FO CSV /NH' % os.getpid()
        out = os.popen(cmd).read()
        memory = 0
        for amount in re.findall(r'([,0-9]+) K', out):
            memory += int(amount.replace(',', ''))
        memory = str(round(float(memory) / 1024, 2))
        memory = 'Memory Usage: \x02%s MB\x02' % memory
    else:
        memory = 'error: operating system not currently supported'
    return memory


@hook.command(autohelp=False)
def uptime(inp):
    ".uptime -- Shows the bot's uptime."
    up_time = subprocess.check_output('ps -eo pid,etime | grep %s | awk \'{print $2}\'' % os.getpid(), shell=True)
    up_time = 'Uptime: \x02' + up_time + '\x02'
    return up_time

@hook.command(autohelp=False)
def pid(inp):
    ".pid -- Prints the bot's PID."
    return 'PID: \x02%s\x02' % os.getpid()
