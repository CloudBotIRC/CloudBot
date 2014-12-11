import re
import requests

from cloudbot import hook


@hook.command(autohelp=False)
def kernel(reply):
    """- gets a list of linux kernel versions"""
    contents = requests.get("https://www.kernel.org/finger_banner").text
    contents = re.sub(r'The latest(\s*)', '', contents)
    contents = re.sub(r'version of the Linux kernel is:(\s*)', '- ', contents)
    lines = contents.split("\n")

    message = "Linux kernel versions: {}".format(", ".join(line for line in lines[:-1]))
    reply(message)
