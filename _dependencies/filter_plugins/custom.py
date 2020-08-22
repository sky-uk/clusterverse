#!/usr/bin/env python

from ansible.utils.display import Display

display = Display()
# display.v(u"json_loads_loose - input type: %s" % type(inStr))

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
        return str(dns.resolver.query(fqdn, 'A')[0])

# Returns a json object from a loosely defined string (e.g. encoded using single quotes instead of double), or an object containing "AnsibleUnsafeText"
def json_loads_loose(inStr):
    import re, json

    display.vvv(u"json_loads_loose - input type: %s" % type(inStr))
    if type(inStr) is dict or type(inStr) is list:
        json_object = json.loads((str(json.dumps(inStr))).encode('utf-8'))
    else:
        try:
            json_object = json.loads(inStr)
        except (ValueError, AttributeError) as e:
            try:
                json_object = json.loads(str(re.sub(r'\'(.*?)\'([,:}])', r'"\1"\2', inStr).replace(': True', ': "True"').replace(': False', ': "False"')).encode('utf-8'))
            except (ValueError, AttributeError) as e:
                display.v(u"json_loads_loose - WARNING: could not parse attribute string as json: %s" % inStr)
                return inStr
    return json_object


class FilterModule(object):
    def filters(self):
        return {
            'dict_agg': dict_agg,
            'iplookup': iplookup,
            'json_loads_loose': json_loads_loose
        }
