#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.2',
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
'''

from ansible.plugins.callback import CallbackBase
from ansible.context import CLIARGS
from ansible.cli import CLI

import sys

HAS_MODULES = True


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'cli_facts'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__(*args, **kwargs)
        self._cliargs = CLIARGS
        self._argv = sys.argv

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

    def v2_playbook_on_play_start(self, play):
        variable_manager = play.get_variable_manager()

        # We cannot put 'localhost' in get_hosts(pattern=['all', 'localhost']) call, because of PR 58400, described below.
        hosts = variable_manager._inventory.get_hosts(pattern=['all'], ignore_restrictions=True)
        if variable_manager._inventory.localhost: hosts.append(variable_manager._inventory.localhost)
        for host in hosts:
            # Ansible 2.9 (https://github.com/ansible/ansible/pull/58400) changed the 'host' type in ansible/vars/manager.py::set_host_variable() from type <class 'ansible.inventory.host.Host'> to type string.
            if CLI.version_info()['major'] >= 2 and CLI.version_info()['minor'] >= 9:
                host = str(host)
            variable_manager.set_host_variable(host, "cliargs", dict(self._cliargs))
            variable_manager.set_host_variable(host, "argv", self._argv)
