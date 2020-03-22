# clusterverse-example  &nbsp; [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) ![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)
This is an example of a deployment of [clusterverse](https://github.com/sky-uk/clusterverse) - _the full-lifecycle cloud infrastructure cluster management project, using Ansible._

_**Please refer to the full [README.md](https://github.com/sky-uk/clusterverse/blob/master/README.md) in the main  [clusterverse](https://github.com/sky-uk/clusterverse) repository.**_ 

## Contributing
Contributions are welcome and encouraged.  Please see [CONTRIBUTING.md](https://github.com/sky-uk/clusterverse/blob/master/CONTRIBUTING.md) for details.

## Requirements
+ Ansible >= 2.9
+ Python >= 2.7


## Usage
This example depends on the [clusterverse](https://github.com/sky-uk/clusterverse) role.  It can be collected automatically using `ansible-galaxy`, or you could reference it using git sub-branches.  This example uses `ansible-galaxy`.  

To import the [clusterverse](https://github.com/sky-uk/clusterverse) role into the current directory:
+ `ansible-galaxy install -r requirements.yml`


### Cluster Variables
One of the mandatory command-line variables is `clusterid`, which defines the name of the directory under `group_vars`, from which variable files will be imported.

#### group_vars/\<clusterid\>/cluster_vars.yml:
```
app_name: "nginx"                 # The name of the application cluster (e.g. 'couchbase', 'nginx'); becomes part of cluster_name.
app_class: "webserver"            # The class of application (e.g. 'database', 'webserver'); becomes part of the fqdn

cluster_vars:
  region: ""
  image: ""
  ...
  <buildenv>:
    hosttype_vars:
      <hosttype>: {...}
    ...
```

Variables defined in here override defaults in `roles/clusterverse/_dependencies/defaults/main.yml`, and can be overriden by defining them on the command-line.

#### group_vars/\<clusterid\>/app_vars.yml:
Contains your application-specific variables

---
## Invocation examples: _deploy_, _scale_, _repair_
The `cluster.yml` sub-role immutably deploys a cluster from the config defined above.  If it is run again it will do nothing.  If the cluster_vars are changed (e.g. add a host), the cluster will reflect the new variables (e.g. a new host will be added to the cluster).

### AWS:
```
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_ -e release_version=v1.0.1
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py -e clean=_all_
```
### GCP:
```
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_gce_euw1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_gce_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterverse_clean -e clean=_all_ -e release_version=v1.0.
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_gce_euw1 --vault-id=sandbox@.vaultpass-client.py -e clean=_all_
```

### Mandatory command-line variables:
+ `-e clusterid=<vtp_aws_euw1>` - A directory named `clusterid` must be present in `group_vars`.  Holds the parameters that define the cluster; enables a multi-tenanted repository.
+ `-e buildenv=<sandbox>` - The environment (dev, stage, etc), which must be an attribute of `cluster_vars` defined in `group_vars/<clusterid>/cluster_vars.yml`

### Optional extra variables:
+ `-e app_name=<nginx>` - Normally defined in `group_vars/<clusterid>/cluster_vars.yml`.  The name of the application cluster (e.g. 'couchbase', 'nginx'); becomes part of cluster_name
+ `-e app_class=<proxy>` - Normally defined in `group_vars/<clusterid>/cluster_vars.yml`.  The class of application (e.g. 'database', 'webserver'); becomes part of the fqdn
+ `-e release_version=<v1.0.1>` - Identifies the application version that is being deployed.
+ `-e dns_tld_external=<test.example.com>` - Normally defined in `group_vars/<clusterid>/cluster_vars.yml`.
+ `-e clean=[current|retiring|redeployfail|_all_]` - Deletes VMs in `lifecycle_state`, or `_all_`, as well as networking and security groups
+ `-e do_package_upgrade=true` - Upgrade the OS packages (not good for determinism)
+ `-e reboot_on_package_upgrade=true` - After updating packages, performs a reboot on all nodes.
+ `-e prometheus_node_exporter_install=false` - Does not install the prometheus node_exporter
+ `-e static_journal=true` - Creates /var/log/journal directory, which will keep a permanent record of journald logs in systemd machines (normally ephemeral)
+ `-e filebeat_install=false` - Does not install filebeat
+ `-e create_gce_network=true` - Create GCP network and subnetwork (probably needed if creating from scratch and using public network)

### Tags
+ `clusterverse_clean`: Deletes all VMs and security groups (also needs `-e clean=[current|retiring|redeployfail|_all_]` on command line)
+ `clusterverse_create`: Creates only EC2 VMs, based on the hosttype_vars values in group_vars/all/cluster.yml
+ `clusterverse_config`: Updates packages, sets hostname, adds hosts to DNS


---

## Invocation examples: _redeploy_
The `redeploy.yml` sub-role will completely redeploy the cluster; this is useful for example to upgrade the underlying operating system version.

### AWS:
```
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> redeploy.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py -e canary=none
```
### GCP:
```
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> redeploy.yml -e buildenv=sandbox -e clusterid=vtp_gce_euw1 --vault-id=sandbox@.vaultpass-client.py -e canary=none
```

### Mandatory command-line variables:
+ `-e clusterid=<vtp_aws_euw1>` - A directory named `clusterid` must be present in `group_vars`.  Holds the parameters that define the cluster; enables a multi-tenanted repository.
+ `-e buildenv=<sandbox>` - The environment (dev, stage, etc), which must be an attribute of `cluster_vars` defined in `group_vars/<clusterid>/cluster_vars.yml`
+ `-e canary=['start', 'finish', 'none', 'tidy']` - Specify whether to start or finish a canary deploy, or 'none' deploy

### Extra variables:
+ `-e redeploy_scheme=<subrole_name>` - The scheme corresponds to one defined in `roles/clusterverse/redeploy`
+ `-e canary_tidy_on_success=[true|false]` - Whether to run the tidy (remove the replaced VMs and DNS) on successful redeploy 
+ `-e myhosttypes="master,slave"`- In redeployment you can define which host type you like to redeploy. If not defined it will redeploy all host types
