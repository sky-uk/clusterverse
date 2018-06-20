#!/usr/bin/env python

import json

# Create an aggregation on aggkey within the dictarr array of dicts.  Differs from the builtin jinja2 filter 'groupby' in that it returns a dict for each aggregation, rather than putting it at array elem 0.
def dict_agg(dictarr, aggkey):
    results = {}

    for dictItem in dictarr:
        if dictItem[aggkey] not in results:
            results[dictItem[aggkey]] = []

        results[dictItem[aggkey]].append(dictItem)

    return json.dumps(results, indent=4)


class FilterModule(object):
    def filters(self):
        return {
            'dict_agg': dict_agg
        }
