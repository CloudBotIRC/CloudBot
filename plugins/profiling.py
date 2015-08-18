import asyncio
import os
import signal
import threading
import traceback
import sys

PYMPLER_ENABLED = False

if PYMPLER_ENABLED:
    try:
        import pympler
        import pympler.muppy
        import pympler.summary
        import pympler.tracker
    except ImportError:
        pympler = None
else:
    pympler = None
try:
    import objgraph
except ImportError:
    objgraph = None

from cloudbot import hook
from cloudbot.util import web


def get_name(thread_id):
    current_thread = threading.current_thread()
    if thread_id == current_thread._ident:
        is_current = True
        thread = current_thread
    else:
        is_current = False
        thread = threading._active.get(thread_id)

    if thread is not None:
        if thread.name is not None:
            name = thread.name
        else:
            name = "Unnamed thread"
    else:
        name = "Unknown thread"

    name = "{} ({})".format(name, thread_id)
    if is_current:
        name += " - Current thread"

    return name


def get_thread_dump():
    code = []
    threads = [(get_name(thread_id), traceback.extract_stack(stack))
               for thread_id, stack in sys._current_frames().items()]
    for thread_name, stack in threads:
        code.append("# {}".format(thread_name))
        for filename, line_num, name, line in stack:
            code.append("{}:{} - {}".format(filename, line_num, name))
            if line:
                code.append("    {}".format(line.strip()))
        code.append("")  # new line
    return web.paste("\n".join(code), ext='txt')


@asyncio.coroutine
@hook.command("threaddump", autohelp=False, permissions=["botcontrol"])
def threaddump_command():
    return get_thread_dump()


@hook.command("objtypes", autohelp=False, permissions=["botcontrol"])
def show_types():
    if objgraph is None:
        return "objgraph not installed"
    objgraph.show_most_common_types(limit=20)
    return "Printed to console"


@hook.command("objgrowth", autohelp=False, permissions=["botcontrol"])
def show_growth():
    if objgraph is None:
        return "objgraph not installed"
    objgraph.show_growth(limit=10)
    return "Printed to console"


@hook.command("pymsummary", autohelp=False, permissions=["botcontrol"])
def pympler_summary():
    if pympler is None:
        return "pympler not installed / not enabled"
    all_objects = pympler.muppy.get_objects()
    summ = pympler.summary.summarize(all_objects)
    pympler.summary.print_(summ)
    return "Printed to console"


@hook.on_start()
def create_tracker():
    if pympler is None:
        return
    global tr
    tr = pympler.tracker.SummaryTracker()


@hook.command("pymdiff", autohelp=False, permissions=["botcontrol"])
def pympler_diff():
    if pympler is None:
        return "pympler not installed / not enabled"
    tr.print_diff()
    return "Printed to console"

# # Provide an easy way to get a threaddump, by using SIGUSR1 (only on POSIX systems)
if os.name == "posix":
    def debug():
        print(get_thread_dump())

    signal.signal(signal.SIGUSR1, debug)  # Register handler
