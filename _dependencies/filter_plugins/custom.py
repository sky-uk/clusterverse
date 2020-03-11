#!/usr/bin/env python

from ansible.utils.display import Display

display = Display()
# display.v(u"json_loads_loose - input type: %s" % type(inStr))

# Create an aggregation on aggkey within the dictarr array of dicts.  Differs from the builtin jinja2 filter 'groupby' in that it returns a dict for each aggregation, rather than putting it at array elem 0.
def dict_agg(dictarr, aggkey):
    import json
    results = {}

    display.v(u"dictarr: %s" % type(dictarr))

    if dictarr:
        for dictItem in dictarr:
            if aggkey in dictItem:
                if dictItem[aggkey] not in results:
                    results[dictItem[aggkey]] = []

                results[dictItem[aggkey]].append(dictItem)

    return json.dumps(results, indent=4)


# Lookup IP from fqdn.  If fqdn is an IP, just return it
def iplookup(fqdn):
    import re
    if re.match(r"^(?:(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])$", fqdn):
        return fqdn
    else:
        import dns.resolver
        return str(dns.resolver.query(fqdn, 'A')[0])


class FilterModule(object):
    def filters(self):
        return {
            'dict_agg': dict_agg,
            'iplookup': iplookup
        }
