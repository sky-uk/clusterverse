# Copyright 2020 Dougal Seeley <github@dougalseeley.com>

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
---
module: deprecate_str
version_added: 1.0.0
description:
    - Print a deprecation warning to the console on demand
authors:
    - Dougal Seeley <github@dougalseeley.com>
'''

EXAMPLES = '''
- deprecate_str:
    msg: "asdf is deprecated"
    version: "9.8"
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(argument_spec={"msg": {"type": "str", "default": "Deprecate, world"}, "version": {"type": "str", 'default': None}})

    module.deprecate(msg=module.params['msg'], version=module.params['version'])

    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
