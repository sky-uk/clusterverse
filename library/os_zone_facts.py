#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_zone_facts
short_description: Interrogate OpenStack DNS zones
extends_documentation_fragment: openstack
version_added: "2.5"
author: "Dougal Seeley"
description:
    - Get info on OpenStack DNS zones.
options:
   name:
     description:
        - Zone name
     required: true
requirements:
    - "python >= 2.6"
    - "shade"
'''

EXAMPLES = '''
# Get the facts for a zone named "example.net" (note the extra .) 
- os_zone_facts:
    auth_type: password
    auth:
      auth_url: "http://192.168.0.1:5000/v2.0"
      tenant_id: "99999999999999999999999999999999"
      tenant_name: "ASDF"
      project_name: "ASDF"
      username: "{{os_username}}"
      password: "{{os_password}}"
    name: "example.net."
'''

RETURN = '''
zone:
    description: Dictionary describing the zone.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: Unique zone ID
            type: string
            sample: "c1c530a3-3619-46f3-b0f6-236927b2618c"
        name:
            description: Zone name
            type: string
            sample: "example.net."
        type:
            description: Zone type
            type: string
            sample: "PRIMARY"
        email:
            description: Zone owner email
            type: string
            sample: "test@example.net"
        description:
            description: Zone description
            type: string
            sample: "Test description"
        ttl:
            description: Zone TTL value
            type: int
            sample: 3600
        masters:
            description: Zone master nameservers
            type: list
            sample: []
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(required=True),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           **module_kwargs)

    name = module.params.get('name')

    shade, cloud = openstack_cloud_from_module(module, min_version='1.8.0')
    try:
        zone = cloud.get_zone(name)

        module.exit_json(changed=False, zone=zone)

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
