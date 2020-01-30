# clusterverse
This project provides an Ansible playbook to provision (cloud) infrastructure.

## Requirements
Ansible >= 2.9

## Variables specific to your project

### group_vars:
#### group_vars/\<clusterid\>/cluster_vars.yml:
```
buildenv: ""                      # The environment (dev, stage, etc), which must be an attribute of cluster_vars
release_version: ""               # Identifies the application version that is being deployed (optional)
app_name: "nginx"                 # The name of the application cluster (e.g. 'couchbase', 'nginx'); becomes part of cluster_name.
app_class: "webserver"            # The class of application (e.g. 'database', 'webserver'); becomes part of the fqdn

cluster_vars:
  <buildenv>:
    ...
    hosttype_vars:
      <hosttype>: {...}
```

#### app_vars.yml:
Contains your application-specific variables

## Prerequisites
### AWS
- AWS account with IAM rights to create EC2 VMs + Security Groups in the chosen VPC/Subnets
- Already created VPCs
- Already created Subnets

### GCP
- Create a gcloud account.
- Create a service account in `IAM & Admin` / `Service Accounts`.  Download the json file locally.  This file is used in the `GCP_CREDENTIALS` environment variable that is read in `group_vars/all/clusters.yml`.  You need to export this variable (e.g. `export GCP_CREDENTIALS=/home/<user>/src/gcp.json`).
- Google Cloud SDK need to be installed to run gcloud command-line (e.g. to enable delete protection) - this is handled by `pipenv install`

### Openstack
Put the following OS parameters in your ~/.bash_profile:
```
export OS_AUTH_URL=
export OS_TENANT_ID=
export OS_TENANT_NAME=
export OS_PROJECT_NAME=
export OS_REGION_NAME=
export OS_USERNAME=
export OS_PASSWORD=
```


### DNS
- DNS zone delegated to the Bind instance
or
- Infoblox access and credentials
- DNS zone delegated to the Infoblox instance

### Localhost
Dependencies are managed via Pipenv:
```bash
pipenv install
```
Will create a Python virtual environment with dependencies specified in the Pipfile

To active it, simply enter:
```bash
pipenv shell
```
or run all ansible-playbook commands by prepending `pipenv run`

### Credentials
Credentials can be encrypted inline in the playbooks using [ansible-vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html).
+ Because multiple environments are supported, it is recommended to use [vault-ids](https://docs.ansible.com/ansible/latest/user_guide/vault.html#multiple-vault-passwords), and have credentials per environment (e.g. to help avoid accidentally running a deploy on prod).
+ There is a small script (`.vaultpass-client.py`) that returns a password stored in an environment variable (`VAULT_PASSWORD_BUILDENV`) to ansible.  This is particularly useful for running under Jenkins.
  + `export VAULT_PASSWORD_BUILDENV=<'dev/stage/prod' password>`
+ To encrypt (export `VAULT_PASSWORD_BUILDENV` first):
  + `ansible-vault encrypt_string --vault-id=sandbox@.vaultpass-client.py --encrypt-vault-id=sandbox`
+ To decrypt, either run the playbook with the correct `VAULT_PASSWORD_BUILDENV` and just `debug: msg=` the variable, or:
  + `echo '$ANSIBLE_VAULT;1.2;AES256;sandbox`
  `86338616...33630313034' | ansible-vault decrypt --vault-id=sandbox@.vaultpass-client.py`  + or, to decrypt using a non-exported password:
  + `echo '$ANSIBLE_VAULT;1.2;AES256;sandbox`
  `86338616...33630313034' | ansible-vault decrypt --ask-vault-pass`


## Invocation examples
### Per-cloud:
#### AWS:
```
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterbuild_clean -e clean=true -e release_version=v1.0.1
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py -e clean=true -e skip_package_upgrade=true -e release_version=v1.0.1
```
#### GCP:
```
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_gce_euw1 --vault-id=sandbox@.vaultpass-client.py
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_gce_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterbuild_clean -e clean=true
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_gce_euw1 --vault-id=sandbox@.vaultpass-client.py -e clean=true -e skip_package_upgrade=true
```
#### Openstack:
```
ansible-playbook -u centos --private-key=/home/<user>/.ssh/<rsa_key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_lsd_slo --vault-id=sandbox@.vaultpass-client.py
ansible-playbook -u centos --private-key=/home/<user>/.ssh/<rsa_key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_lsd_slo --vault-id=sandbox@.vaultpass-client.py --tags=clusterbuild_clean -e clean=true
ansible-playbook -u centos --private-key=/home/<user>/.ssh/<rsa_key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_lsd_slo --vault-id=sandbox@.vaultpass-client.py -e clean=true -e skip_package_upgrade=true
```



### Mandatory command-line variables:
+ `-e clusterid=<vtp_aws_euw1>` - A directory named `clusterid` must be present in `group_vars`.  Holds the parameters that define the cluster; enables a multi-tenanted repository.
+ `-e buildenv=<sandbox>` - The environment (dev, stage, etc), which must be an attribute of `cluster_vars` defined in `group_vars/<clusterid>/cluster_vars.yml`

### Optional extra variables:
+ `-e app_name=<nginx>` - Normally defined in `group_vars/<clusterid>/cluster_vars.yml`.  The name of the application cluster (e.g. 'couchbase', 'nginx'); becomes part of cluster_name
+ `-e app_class=<proxy>` - Normally defined in `group_vars/<clusterid>/cluster_vars.yml`.  The class of application (e.g. 'database', 'webserver'); becomes part of the fqdn
+ `-e release_version=<v1.0.1>` - Identifies the application version that is being deployed.
+ `-e dns_tld_external=<test.example.com>` - Normally defined in `group_vars/<clusterid>/cluster_vars.yml`.
+ `-e clean=true` - Deletes all existing VMs and security groups before creating
+ `-e skip_package_upgrade=true` - Does not upgrade the OS packages (saves a lot of time during debugging)
+ `-e reboot_on_package_upgrade=true` - After updating packages, performs a reboot on all nodes.
+ `-e prometheus_node_exporter_install=false` - Does not install the prometheus node_exporter
+ `-e static_journal=true` - Creates /var/log/journal directory, which will keep a permanent record of journald logs in systemd machines (normally ephemeral)
+ `-e filebeat_install=false` - Does not install filebeat
+ `-e create_gce_network=true` - Create GCP network and subnetwork (probably needed if creating from scratch and using public network)

### Tags
- clusterbuild_clean: Deletes all VMs and security groups (also needs `-e clean=true` on command line)
- clusterbuild_create: Creates only EC2 VMs, based on the hosttype_vars values in group_vars/all/cluster.yml
- clusterbuild_config: Updates packages, sets hostname, adds hosts to DNS


---

# redeploy.yml
+ This playbook enables a basic rolling redeployment of the cluster - e.g. if it is desired to upgrade each node without downtime.
  + This assumes a resilient deployment (it can tolerate one node being removed from the cluster).
+ For each node in the cluster, delete it, then run the main cluster.yml, which forces the missing node to be redeployed.  Run with the same parameters as for the main playbook.

### Extra variables:
+ `-e canary=['start', 'finish', 'none']` -  Specify whether to start or finish a canary deploy, or 'none' deploy
+ `-e myhosttypes="master,slave"`- In redeployment you can define which host type you like to redeploy. If not defined it will redeploy all host types