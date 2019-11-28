# clusterverse
This project provides an Ansible playbook to provision (cloud) infrastructure.

## Requirements
Ansible >= 2.6.2 is required (v2.4.0, 2.4.2, 2.5.1, 2.5.3 contain [bug](https://github.com/ansible/ansible/issues/33433), [bug](https://github.com/ansible/ansible/pull/38302), [bug](https://github.com/ansible/ansible/issues/38656) that cause a failures)

## Variables specific to your project

### group_vars:
#### all.yml:
```
clusterid:                        # Must be a folder under `group_vars` containing cluster_vars.yml and app_vars.yml
buildenv:                         # Must be an index into cluster_vars.hosttype_vars in cluster_vars.yml
app_class: "test"                 # The class of application - applies to the fqdn
clustername_prefix: "qwerty"      # Gives a customised name for identification purposes (it is part of cluster_name, and identifies load balancers etc in cloud environments)
dns_tld_external: "example.com"   # Top-level domain (above the level defined per clusterid)
```

#### cluster_vars.yml:
```
group_vars/<clusterid>/cluster_vars.yml:
  <buildenv>:
    ...
    hosttype_vars:
      <hosttype>: {...}
```

#### app_vars.yml:
```
group_vars/<clusterid>/app_vars.yml:
app_var1: {...}
app_var2: {...}
```

## Prerequisites
### AWS
- AWS account with IAM rights to create EC2 VMs + Security Groups in the chosen VPC/Subnets
- Already created VPCs
- Already created Subnets

### GCP
- Create a gcloud account.
- Create a service account in `IAM & Admin` / `Service Accounts`.  Download the json file locally.  This file is used in the `GCP_CREDENTIALS` environment variable that is read in `group_vars/all/clusters.yml`.  You need to export this variable (e.g. `export GCP_CREDENTIALS=/home/<user>/src/gcp.json`).
- Add your public key to `Compute Engine` / `Metadata/ SSH Keys`.  Add a username to the end of the key - this is used as your login username for this certificate.  Your private key should either be passwordless, or you need some password caching agent running.
- You need to edit your "Google Compute Engine API / In-use IP addresses" to at least 16.  This is found in `IAM & Admin` / `Quotas`
- Google Cloud SDK need to be installed to run gcloud command-line (e.g. to enable delete protection)

### Openstack
- Put the following OS parameters in your ~/.bash_profile:
````
export OS_AUTH_URL=
export OS_TENANT_ID=
export OS_TENANT_NAME=
export OS_PROJECT_NAME=
export OS_REGION_NAME=
export OS_USERNAME=
export OS_PASSWORD=
````


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

### Credentials
Credentials are encrypted inline in the playbooks using ansible-vault.  
+ Where they are specific to a VPC environment (e.g. dev/stage etc), they are encrypted with environment-specific password, which should be exported in the environment variable: `VAULT_PASSWORD_BUILDENV`

```
export VAULT_PASSWORD_BUILDENV=<'dev/stage/prod' password>
```


## Invocation examples
### Per-cloud:
#### AWS:
```
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py 
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=sandbox -e clusterid=vtp_aws_euw1 --vault-id=sandbox@.vaultpass-client.py --tags=clusterbuild_clean -e clean=true -e release_version=v1.0.1
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



### Extra variables:
+ `-e app_name=<nginx>` - Gives a customised name for identification purposes if not defined in `group_vars/all.yml` (eg. - nginx, couchbase)
+ `-e app_class=<proxy>` - Specify the class of application if not defined in `group_vars/all.yml` (eg. - proxy, database)
+ `-e buildenv=<environment>`  -  dev/ stage/ prod supported
+ `-e clusterid=<vtp_aws_euw1>` - specify the clusterid: must be one of the clusters in `cluster_vars.yml`
+ `-e dns_tld_external="example.com"` - specify the external DNS TLD if not defined in `group_vars/all.yml`
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
+ `-e canary=['start', 'finish', 'none']`  -  Specify whether to start or finish a canary deploy, or 'none' deploy
+ `-e myhosttypes="master,slave"`- In redeployment you can define which host type you like to redeploy. If not defined it will redeploy all host types

