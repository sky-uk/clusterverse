#!/usr/bin/python
# -*- coding: utf-8 -*-

# https://github.com/dseeley/gce_hosts
#
# Copyright (C) 2017 Dougal Seeley
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#


DOCUMENTATION = '''
---
module: gce_hosts
version_added: "2.0"
short_description: get hosts in gce
description:
    - This module lists hosts within a project in gce
options:
  instance_pattern:
    description:
      - A pattern of GCE instance names to match
  zone:
    description:
      - The zone of the disk specified by source.
    default: us-central1-a
  service_account_email:
    description:
      - Service account email.
  credentials_file:
    description:
      - Path to the JSON credentials file associated with the service account email.
  project_id:
    description:
      - Your GCE project ID.
requirements:
    - python >= 2.6
    - apache-libcloud >= 0.17.0
'''

EXAMPLES = '''
- name: get hosts
  gce_hosts:
    instance_pattern: "web-severs-.*"
    service_account_email: "dev@null.com"
    credentials_file: "my_creds.json"
    project_id: "my_project"
    zone: "europe-west1-d"
  register: gce_host_instances
'''

import re
import traceback

try:
    from libcloud.common.google import GoogleBaseError, QuotaExceededError, ResourceExistsError, ResourceNotFoundError, InvalidRequestError

    HAS_LIBCLOUD = True
except ImportError:
    HAS_LIBCLOUD = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.gce import gce_connect


def main():
    module = AnsibleModule(
        argument_spec=dict(
            instance_pattern=dict(type='str'),
            zone=dict(type='str', default='us-central1-a'),
            service_account_email=dict(type='str'),
            credentials_file=dict(type='path'),
            project_id=dict(type='str')
        )
    )

    instance_pattern = module.params.get('instance_pattern')
    zone = module.params.get('zone')

    if not HAS_LIBCLOUD:
        module.fail_json(msg='libcloud with GCE support (0.17.0+) required for this module')

    gce = gce_connect(module)

    matching_nodes = []
    try:
        instances = gce.list_nodes(ex_zone=zone)
        if instance_pattern:
            if not instances:
                module.exit_json(changed=False, zone=zone, instances=[])
            try:
                p = re.compile(instance_pattern)
                matching_nodes = [i for i in instances if p.search(i.name) is not None]
            except re.error as e:
                module.fail_json(changed=False, msg='Regex failure %s: %s' % (instance_pattern, e))
        else:
            matching_nodes = instances
    except GoogleBaseError as e:
        module.fail_json(changed=False, msg=str(e), exception=traceback.format_exc())

    instance_pattern_matches = []
    for node in matching_nodes:
        instance_pattern_matches.append({'name': node.name, 'public_ips': node.public_ips, 'private_ips': node.private_ips, 'state': node.state})

    module.exit_json(changed=False, instance_pattern=instance_pattern, zone=zone, instances=instance_pattern_matches, raw=str(matching_nodes))


if __name__ == '__main__':
    main()
