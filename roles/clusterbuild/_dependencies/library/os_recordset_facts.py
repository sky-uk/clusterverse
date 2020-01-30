#!/usr/bin/python
# Copyright (c) 2016 Hewlett-Packard Enterprise
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: os_recordset_facts
short_description: Manage OpenStack DNS recordsets
extends_documentation_fragment: openstack
version_added: "2.2"
author: "Ricardo Carrillo Cruz (@rcarrillocruz)"
description:
    - Manage OpenStack DNS recordsets. Recordsets can be created, deleted or
      updated. Only the I(records), I(description), and I(ttl) values
      can be updated.
options:
   zone_id:
     description:
        - Zone ID managing the recordset
     required: true
requirements:
    - "python >= 2.6"
    - "shade"
'''

EXAMPLES = '''
# Get facts on "056a3aad-a1cc-4e48-8c92-48054e447013" recordset
- os_recordset_facts:
    zone: 056a3aad-a1cc-4e48-8c92-48054e447013
'''

RETURN = '''
recordset:
    description: Dictionary describing the recordset.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: Unique recordset ID
            type: string
            sample: "c1c530a3-3619-46f3-b0f6-236927b2618c"
        name:
            description: Recordset name
            type: string
            sample: "www.example.net."
        zone_id:
            description: Zone id
            type: string
            sample: 9508e177-41d8-434e-962c-6fe6ca880af7
        type:
            description: Recordset type
            type: string
            sample: "A"
        description:
            description: Recordset description
            type: string
            sample: "Test description"
        ttl:
            description: Zone TTL value
            type: int
            sample: 3600
        records:
            description: Recordset records
            type: list
            sample: ['10.0.0.1']
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module


def main():
    argument_spec = openstack_full_argument_spec(
        zone_id=dict(required=True),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           **module_kwargs)

    zone_id = module.params.get('zone_id')

    shade, cloud = openstack_cloud_from_module(module, min_version='1.9.0')

    try:
        recordsets = cloud.search_recordsets(zone_id)
        module.exit_json(changed=False, recordset=recordsets)

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
