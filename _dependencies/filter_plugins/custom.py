#!/usr/bin/env python

from ansible.utils.display import Display
from ansible import constants as C
from ansible.module_utils._text import to_native, to_text
from ansible.template import AnsibleUndefined

display = Display()


# Create an aggregation on aggkeys (which may be a nested key) within the dictarr array of dicts.  Differs from the builtin jinja2 filter 'groupby' in that it returns a dict for each aggregation, rather than putting it at array elem 0.
def dict_agg(dictarr, *aggkeys):
    import json
    results = {}

    if dictarr:
        for dictItem in dictarr:
            newDictItem = dictItem
            for aggkey in aggkeys:
                if aggkey in newDictItem:
                    newDictItem = newDictItem[aggkey]
                else:
                    newDictItem = None
                    break
            if newDictItem:
                if newDictItem not in results:
                    results[newDictItem] = []

                results[newDictItem].append(dictItem)

    return json.dumps(results, indent=4)


# Lookup IP from fqdn.  If fqdn is an IP, just return it
def iplookup(fqdn):
    import re
    if re.match(r"^(?:(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])$", fqdn):
        return fqdn
    else:
        import dns.resolver
        return to_text(dns.resolver.query(fqdn, 'A')[0])


# Return extra_vars string from a dict of extra variables
def extravars_from_dict(extravars_dict):
    import json
    if type(extravars_dict) is dict:
        return " ".join(["-e " + k + "='" + json.dumps(v, separators=(',', ':')) + "'" for k, v in extravars_dict.items()])
    else:
        if type(extravars_dict) != AnsibleUndefined:
            display.warning(u"extravars_from_dict - WARNING: could not parse extravars as dict")
        return ""


class FilterModule(object):
    def filters(self):
        return {
            'dict_agg': dict_agg,
            'iplookup': iplookup,
            'extravars_from_dict': extravars_from_dict
        }