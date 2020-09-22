from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.2',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
cars: cli_facts
short_description: Expose the system ARGV and CLI arguments as facts in plays.
version_added: "2.8"
author: "Dougal Seeley"
description:
    - Expose the system ARGV and CLI arguments as facts in plays.  Two new facts are added: argv and cliargs.
options:
requirements:
'''

from ansible.plugins.vars import BaseVarsPlugin
from ansible.context import CLIARGS
import sys


class VarsModule(BaseVarsPlugin):
    REQUIRES_WHITELIST = False

    def get_vars(self, loader, path, entities, cache=True):
        super(VarsModule, self).get_vars(loader, path, entities)
        return {"cliargs": dict(CLIARGS), "argv": sys.argv}
