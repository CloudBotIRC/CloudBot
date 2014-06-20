import os

import psutil

from cloudbot import hook


@hook.command(autohelp=False)
def debug():
    # get a Process object for the bot using psutil
    process = psutil.Process(os.getpid())

    # get the data we need using the Process we got
    cpu = process.cpu_percent()
    thread = len(process.threads())
    mem = process.get_memory_info()[0] / float(2 ** 20)

    return "CPU Usage: \x02{:.2f}%\x02, Memory Usage: \x02{:.2f} MB\x02," \
           " Threads: \x02{}\x02".format(cpu, mem, thread)

