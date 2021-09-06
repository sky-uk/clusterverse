#!/usr/bin/python
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: ec2_instance_type_info
version_added: 1.0.0
short_description: EC2 instance type info
description:
    - List details of EC2 instance types.
    - Uses the boto describe_instance_types API
author: "Dougal Seeley (@dseeley)"
options:
  filters:
    instance_types:
      description: One or more instance types.
      type: list
      elements: str
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and filter
        value.  See U(https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instance-types.html#options)
        for possible filters. Filter names and values are case sensitive.
    required: false
    default: {}
    type: dict
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = r'''
# Note: These examples do not set authentication details,
# see the AWS Guide for details.

- name: List all instance_type in the current region.
  community.aws.ec2_instance_type_info:
  register: regional_eip_addresses

- name: List all instance_type for a VM.
  community.aws.ec2_instance_type_info:
    instance_types: ["t3a.nano", "t4g.nano"]
    filters:
      hypervisor: "nitro"
  register: r__ec2_instance_type_info

- ansible.builtin.debug:
    msg: "{{ r__ec2_instance_type_info }}"
'''

RETURN = '''
instance_types:
  description: Properties of all instances matching the instance_types and provided filters. Each element is a dict with all the information related to an instance.
  returned: on success
  type: list
  sample: [{
            "auto_recovery_supported": false,
            "bare_metal": false,
            "burstable_performance_supported": true,
            "current_generation": true,
            "dedicated_hosts_supported": false,
            "ebs_info": {
                "ebs_optimized_info": {
                    "baseline_bandwidth_in_mbps": 43,
                    "baseline_iops": 250,
                    "baseline_throughput_in_m_bps": 5.375,
                    "maximum_bandwidth_in_mbps": 2085,
                    "maximum_iops": 11800,
                    "maximum_throughput_in_m_bps": 260.625
                },
                "ebs_optimized_support": "default",
                "encryption_support": "supported",
                "nvme_support": "required"
            },
            "free_tier_eligible": false,
            "hibernation_supported": false,
            "hypervisor": "nitro",
            "instance_storage_supported": false,
            "instance_type": "t4g.nano",
            "memory_info": {
                "size_in_mi_b": 512
            },
            "network_info": {
                "default_network_card_index": 0,
                "efa_supported": false,
                "ena_support": "required",
                "ipv4_addresses_per_interface": 2,
                "ipv6_addresses_per_interface": 2,
                "ipv6_supported": true,
                "maximum_network_cards": 1,
                "maximum_network_interfaces": 2,
                "network_cards": [
                    {
                        "maximum_network_interfaces": 2,
                        "network_card_index": 0,
                        "network_performance": "Up to 5 Gigabit"
                    }
                ],
                "network_performance": "Up to 5 Gigabit"
            },
            "placement_group_info": {
                "supported_strategies": [
                    "partition",
                    "spread"
                ]
            },
            "processor_info": {
                "supported_architectures": [
                    "arm64"
                ],
                "sustained_clock_speed_in_ghz": 2.5
            },
            "supported_boot_modes": [
                "uefi"
            ],
            "supported_root_device_types": [
                "ebs"
            ],
            "supported_usage_classes": [
                "on-demand",
                "spot"
            ],
            "supported_virtualization_types": [
                "hvm"
            ],
            "v_cpu_info": {
                "default_cores": 2,
                "default_threads_per_core": 1,
                "default_v_cpus": 2,
                "valid_cores": [
                    1,
                    2
                ],
                "valid_threads_per_core": [
                    1
                ]
        }]
'''

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import (ansible_dict_to_boto3_filter_list,
                                                                     boto3_tag_list_to_ansible_dict,
                                                                     camel_dict_to_snake_dict
                                                                     )

try:
    from botocore.exceptions import (BotoCoreError, ClientError)
except ImportError:
    pass  # caught by imported AnsibleAWSModule


def get_describe_instance_types(module):
    connection = module.client('ec2')
    try:
        response = connection.describe_instance_types(InstanceTypes=module.params.get("instance_types"), Filters=ansible_dict_to_boto3_filter_list(module.params.get("filters")))
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Error retrieving InstanceTypes")

    instance_types = camel_dict_to_snake_dict(response)['instance_types']
    return instance_types


def main():
    module = AnsibleAWSModule(
        argument_spec=dict(
            instance_types=dict(default=[], type='list', elements='str', aliases=['instance_type']),
            filters=dict(type='dict', default={})
        ),
        supports_check_mode=True
    )

    module.exit_json(changed=False, instance_types=get_describe_instance_types(module))


if __name__ == '__main__':
    main()
