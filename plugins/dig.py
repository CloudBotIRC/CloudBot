import requests
import json

from cloudbot import hook


base_url = "http://dig.jsondns.org/IN/"

@hook.command
def dig(text):
    """.dig <domain> <recordtype> returns a list of records for the specified domain valid record types are A, NS, and MX. If a record type is not chosen A will be the default."""
    try:
        domain, rtype = text.split()
        rtype = rtype.upper()
        if rtype not in ["A", "NS", "MX"]:
            rtype = "A"
    except:
        domain = text.strip()
        rtype = "A"
    url = "http://dig.jsondns.org/IN/{}/{}".format(domain, rtype)
    r = requests.get(url)
    results = r.json()
    out = "The following records were found for {}: ".format(domain)
    if results['header']['rcode']== "NXDOMAIN":
        return "no dns record for {} was found".format(domain)
    for r in range(len(results['answer'])):
        domain = results['answer'][r]['name']
        rtype = results['answer'][r]['type']
        ttl = results['answer'][r]['ttl']
        rdata = results['answer'][r]['rdata']
        out += "name: {} type: {} ttl: {} rdata: {} | ".format(domain, rtype, ttl, rdata)
    out = out[:-2]
    return out
