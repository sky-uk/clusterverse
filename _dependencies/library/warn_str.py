# Copyright 2021 Dougal Seeley <github@dougalseeley.com>
# BSD 3-Clause License

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
---
module: warn_str
version_added: 1.0.0
description:
    - Print a deprecation warning to the console on demand
authors:
    - Dougal Seeley <github@dougalseeley.com>
'''

EXAMPLES = '''
- warn_str:
    msg: "asdf is not really a word"
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(argument_spec={"msg": {"type": "str", "default": "Warn, world"}})

    module.warn(module.params['msg'])

    module.exit_json(changed=False)


if __name__ == '__main__':
    main()
