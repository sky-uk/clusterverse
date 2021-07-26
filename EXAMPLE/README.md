# clusterverse-example  &nbsp; [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) ![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)
This is an example of a deployment of [clusterverse](https://github.com/sky-uk/clusterverse) - _the full-lifecycle cloud infrastructure cluster management project, using Ansible._

_**Please refer to the full [README.md](https://github.com/sky-uk/clusterverse/blob/master/README.md) in the main [clusterverse](https://github.com/sky-uk/clusterverse) repository.**_ 

## Contributing
Contributions are welcome and encouraged.  Please see [CONTRIBUTING.md](https://github.com/sky-uk/clusterverse/blob/master/CONTRIBUTING.md) for details.

## Requirements
+ Ansible >= 2.9
+ Python >= 2.7


---
## Invocation examples: _deploy_, _scale_, _repair_
The `cluster.yml` sub-role immutably deploys a cluster from the config defined above.  If it is run again it will do nothing.  If the cluster_vars are changed (e.g. add a host), the cluster will reflect the new variables (e.g. a new host will be added to the cluster).

### AWS:
```
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=aws -e region=eu-west-1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=aws -e region=eu-west-1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_aws_euw1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_aws_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```
### GCP:
```
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=gcp -e region=europe-west1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=gcp -e region=europe-west1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_gcp_euw1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=test_gcp_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```
### ESXi (free):
```
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=esxifree -e region=homelab --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=esxifree -e region=homelab --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```
### Azure:
```
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=azure -e region=westeurope --vault-id=sandbox@.vaultpass-client.py
ansible-playbook cluster.yml -e buildenv=sandbox -e clusterid=testid -e cloud_type=azure -e region=westeurope --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_
```

### Mandatory command-line variables:
+ `-e buildenv=<sandbox>` - The environment (dev, stage, etc), which must be an attribute of `cluster_vars` (i.e. `{{cluster_vars[build_env]}}`)

### Optional extra variables:
+ `-e app_name=<nginx>` - Normally defined in `/cluster_defs/`.  The name of the application cluster (e.g. 'couchbase', 'nginx'); becomes part of cluster_name
+ `-e app_class=<proxy>` - Normally defined in `/cluster_defs/`.  The class of application (e.g. 'database', 'webserver'); becomes part of the fqdn
+ `-e release_version=<v1.0.1>` - Identifies the application version that is being deployed.
+ `-e clean=[current|retiring|redeployfail|_all_]` - Deletes VMs in `lifecycle_state`, or `_all_`, as well as networking and security groups
+ `-e pkgupdate=[always|onCreate]` - Upgrade the OS packages (not good for determinism).  `onCreate` only upgrades when creating the VM for the first time.
+ `-e reboot_on_package_upgrade=true` - After updating packages, performs a reboot on all nodes.
+ `-e prometheus_node_exporter_install=false` - Does not install the prometheus node_exporter
+ `-e static_journal=true` - Creates /var/log/journal directory, which will keep a permanent record of journald logs in systemd machines (normally ephemeral)
+ `-e filebeat_install=false` - Does not install filebeat
+ `-e metricbeat_install=false` - Does not install metricbeat
+ `-e wait_for_dns=false` - Does not wait for DNS resolution
+ `-e create_gcp_network=true` - Create GCP network and subnetwork (probably needed if creating from scratch and using public network)
+ `-e delete_gcp_network_on_clean=true` - Delete GCP network and subnetwork when run with `-e clean=_all_`
+ `-e debug_nested_log_output=true` - Show the log output from nested calls to embedded Ansible playbooks (i.e. when redeploying)
+ `-e cluster_vars_override='{"sandbox":{"hosttype_vars":{"sys":{"vms_by_az":{"b":1,"c":1,"d":0}}}}}'` - Ability to override cluster_vars dictionary elements from the command line.  NOTE: there must be NO SPACES in this string.

### Tags
+ `clusterverse_clean`: Deletes all VMs and security groups (also needs `-e clean=[current|retiring|redeployfail|_all_]` on command line)
+ `clusterverse_create`: Creates only EC2 VMs, based on the hosttype_vars values in `/cluster_defs/`
+ `clusterverse_config`: Updates packages, sets hostname, adds hosts to DNS


---

## Invocation examples: _redeploy_
The `redeploy.yml` sub-role will completely redeploy the cluster; this is useful for example to upgrade the underlying operating system version, or changing the disk sizes.

### AWS:
```
ansible-playbook redeploy.yml -e buildenv=sandbox -e cloud_type=aws -e region=eu-west-1 -e clusterid=test --vault-id=sandbox@.vaultpass-client.py -e canary=none
ansible-playbook redeploy.yml -e buildenv=sandbox -e clusterid=test_aws_euw1 --vault-id=sandbox@.vaultpass-client.py -e canary=none
```
### GCP:
```
ansible-playbook redeploy.yml -e buildenv=sandbox -e clusterid=test -e cloud_type=gcp -e region=europe-west1 --vault-id=sandbox@.vaultpass-client.py -e canary=none
ansible-playbook redeploy.yml -e buildenv=sandbox -e clusterid=test_aws_euw1 --vault-id=sandbox@.vaultpass-client.py -e canary=none
```
### Azure:
```
ansible-playbook redeploy.yml -e buildenv=sandbox -e clusterid=test -e cloud_type=azure -e region=westeurope --vault-id=sandbox@.vaultpass-client.py -e canary=none
```

### Mandatory command-line variables:
+ `-e buildenv=<sandbox>` - The environment (dev, stage, etc), which must be an attribute of `cluster_vars` defined in `group_vars/<clusterid>/cluster_vars.yml`
+ `-e canary=['start', 'finish', 'none', 'tidy']` - Specify whether to start or finish a canary deploy, or 'none' deploy

### Extra variables:
+ `-e redeploy_scheme=<subrole_name>` - The scheme corresponds to one defined in `roles/clusterverse/redeploy`
+ `-e canary_tidy_on_success=[true|false]` - Whether to run the tidy (remove the replaced VMs and DNS) on successful redeploy 
+ `-e myhosttypes="master,slave"`- In redeployment you can define which host type you like to redeploy. If not defined it will redeploy all host types
