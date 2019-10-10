#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: cli_facts
short_description: Expose the system ARGV and CLI arguments as facts in plays.
version_added: "2.8"
author: "Dougal Seeley"
description:
    - Expose the system ARGV and CLI arguments as facts in plays.  Two new facts are added: argv and cliargs.
options:
requirements:
    - "python >= 3"
'''

from ansible.context import CLIARGS
from ansible.plugins.callback import CallbackBase

import sys

HAS_MODULES = True


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'cli_facts'

    def __init__(self):
        self._cliargs = CLIARGS
        self._argv = sys.argv

    def v2_playbook_on_play_start(self, play):
        variable_manager = play.get_variable_manager()
        variable_manager.set_host_variable(variable_manager._inventory.localhost, "cliargs", self._cliargs)
        variable_manager.set_host_variable(variable_manager._inventory.localhost, "argv", self._argv)
        hosts = variable_manager._inventory.get_hosts()
        for host in hosts:
            variable_manager.set_host_variable(host, "cliargs", self._cliargs)
            variable_manager.set_host_variable(host, "argv", self._argv)
