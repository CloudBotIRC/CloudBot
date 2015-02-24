import requests
import json

from cloudbot import hook


@hook.command
def dig(text):
    """.dig <domain> <recordtype> returns a list of records for the specified domain valid record types are A, NS, TXT, and MX. If a record type is not chosen A will be the default."""
    try:
        domain, rtype = text.split()
        rtype = rtype.upper()
        if rtype not in ["A", "NS", "MX", "TXT"]:
            rtype = "A"
    except:
        domain = text.strip()
        rtype = "A"
    url = "http://dig.jsondns.org/IN/{}/{}".format(domain, rtype)
    r = requests.get(url)
    results = r.json()
    out = "The following records were found for {}: ".format(domain)
    if results['header']['rcode'] == "NXDOMAIN" or not results['header']['answer']:
        return "no dns record for {} was found".format(domain)
    out = "The following records were found for {}: ".format(domain)
    for r in range(len(results['answer'])):
        domain = results['answer'][r]['name']
        rtype = results['answer'][r]['type']
        ttl = results['answer'][r]['ttl']
        if rtype == "MX":
            rdata = results['answer'][r]['rdata'][1]
        else:
            rdata = results['answer'][r]['rdata']
        out += "name: \x02{}\x02 type: \x02{}\x02 ttl: \x02{}\x02 rdata: \x02{}\x02 | ".format(
            domain, rtype, ttl, rdata)
    out = out[:-2]
    return out
