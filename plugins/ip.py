from cloudbot import hook
from cloudbot.util import database, colors, web
import ipcalc

@hook.command()
def ip(text, notice):
    """ip <number>/<netmask> - Calculates the network given by the IP and Netmask"""
    text = text.strip().lower()
    network = ipcalc.Network(text)
    return "{} {} | Wildcard Mask: {} | Size of network: {} | Range: {} - {} | Reverse Lookup: {}".format(network.network(), network.netmask(), network.wildcard(), network.size(), network.host_first(), network.host_last(), network.to_reverse())

