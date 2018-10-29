# clusterverse
This project provides an Ansible playbook to provision (cloud) infrastructure.

## Requirements
Ansible >= 2.6.2 is required (v2.4.0, 2.4.2, 2.5.1, 2.5.3 contain [bug](https://github.com/ansible/ansible/issues/33433), [bug](https://github.com/ansible/ansible/pull/38302), [bug](https://github.com/ansible/ansible/issues/38656) that cause a failures)

## Variables specific to your project

### group_vars:
#### all.yml:
```
clusterid:                        # Must be an index into cluster_vars in cluster_vars.yml
buildenv:                         # Must be an index into cluster_vars[clusterid].host_vars in cluster_vars.yml
app_class: "test"                 # The class of application - applies to the fqdn
clustername_prefix: "qwerty"      # Gives a customised name for identification purposes (it is part of cluster_name, and identifies load balancers etc in cloud environments)
dns_tld_external: "example.com" # Top-level domain (above the level defined per clusterid)
```

#### cluster_vars.yml:
```
cluster_vars:
  aws_eu_west_1:
    type: aws
#    image: "ami-3548444c"            #CentOS Linux 7 x86_64 HVM EBS ENA 1805_01-b7ee8a69-ee97-4a49-9e68-afaee216db2e-ami-77ec9308.4
#    image: "ami-00b36349b3dba2ec3"  #ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20181012
    image: "ami-0aebeb281fdee5054"  #ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20181012
    region: "eu-west-1"
    assign_public_ip: "no"
    dns_zone_internal: "eu-west-1.compute.internal"
    dns_zone_external: "{%- if dns_tld_external -%}  aws_euw1.{{app_class}}.{{buildenv}}.{{dns_tld_external}}  {%- endif -%}"
    dns_server: "nsupdate"    # Specify DNS server. nsupdate, infoblox or openstack (on openstack) supported.  If empty string is specified, no DNS will be added.
    instance_profile_name: "vpc_lock_{{buildenv}}"
    secgroups_existing: []
    secgroup_new:
      - proto: "tcp"
        ports: [22]
        cidr_ip: 10.0.0.0/8
        rule_desc: "SSH Access"
      - proto: "tcp"
        ports: ["{{prometheus_node_exporter_port}}"]
        group_name: ["{{buildenv}}-private-sg"]
        rule_desc: "Prometheus instances attached to {{buildenv}}-private-sg can access the exporter port(s)."
      - proto: all
        group_name: ["{{cluster_name}}-sg"]
        rule_desc: "Access from all VMs attached to the {{ cluster_name }}-sg group"
    dev:
      host_vars:
        test: {count_per_az: 1, az: ["a", "b"], flavor: t3.micro, ephemeral_volumes: [{"device_name": "/dev/sdb", mountpoint: "/dev/xvdb", "volume_type": "gp2", "volume_size": 2, "delete_on_termination": true}]}
      aws_access_key:
      aws_secret_key:
      vpc_name: "{{buildenv}}"
      vpc_subnet_name_prefix: "{{buildenv}}-infrastructure-subnet"
      key_name: "{{buildenv}}-key"
      termination_protection: "yes"
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

### Openstack
- Put the following OS parameters in your ~/.bash_profile:
````
export OS_AUTH_URL=
export OS_TENANT_ID=
export OS_TENANT_NAME=
export OS_PROJECT_NAME=
export OS_REGION_NAME=
export OS_USERNAME="<youruser>"
export OS_PASSWORD='<yourpass>'
````


### Other
- Infoblox access and credentials
- Internal DNS zone delegated to the Infoblox instance (eg. example.com)

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
+ Where they are generic the are exported via `VAULT_PASSWORD_ALL`

```
export VAULT_PASSORD_ALL=<'all' password>
export VAULT_PASSORD_BUILDENV=<'dev/stage/prod' password>
```


## Invocation
#### AWS:
```
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=dev -e clusterid=aws_eu_west_1 --tags=clusterbuild_clean -e clean=true
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=dev -e clusterid=aws_eu_west_1 -e clean=true -e skip_package_upgrade=true
```
#### GCP:
```
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=dev -e clusterid=gce_eu_west1 --tags=clusterbuild_clean -e clean=true
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e buildenv=dev -e clusterid=gce_eu_west1 -e clean=true -e skip_package_upgrade=true
```
#### Openstack:
```
ansible-playbook -u centos --private-key=/home/<user>/.ssh/<rsa_key> cluster.yml -e buildenv=dev -e clusterid=m25_lsd_slo --tags=clusterbuild_clean -e clean=true
ansible-playbook -u centos --private-key=/home/<user>/.ssh/<rsa_key> cluster.yml -e buildenv=dev -e clusterid=m25_lsd_slo -e clean=true -e skip_package_upgrade=true
```



### Extra variables:
+ `-e buildenv=<environment>`  -  dev/ stage/ prod supported
+ `-e clusterid=<aws_eu_west_1>` - specify the clusterid: must be one of the clusters in `cluster_vars.yml`
+ `-e dns_tld_external="example.com"` - specify the external DNS TLD if not defined in `group_vars/all.yml`
+ `-e clean=true` - Deletes all existing VMs and security groups before creating
+ `-e skip_package_upgrade=true` - Does not upgrade the OS packages (saves a lot of time during debugging)
+ `-e reboot_on_package_upgrade=true` - After updating packages, performs a reboot on all nodes.
+ `-e prometheus_node_exporter_install=false` - Does not install the prometheus node_exporter
+ `-e static_journal=true` - Creates /var/log/journal directory, which will keep a permanent record of journald logs in systemd machines (normally ephemeral)
+ `-e filebeat_install=false` - Does not install filebeat
+ `-e myhosttypes="bind-master,bind-slave"`- In redeployment you can define which host type you like to redeploy. If not defined it will redeploy all host types

### Tags
- clusterbuild_clean: Deletes all VMs and security groups (also needs `-e clean=true` on command line)
- clusterbuild_create: Creates only EC2 VMs, based on the host_vars values in group_vars/all/cluster.yml  
- clusterbuild_config: Updates packages, sets hostname, adds hosts to DNS


---

# redeploy.yml
+ This playbook enables a basic rolling redeployment of the cluster - e.g. if it is desired to upgrade each node without downtime.
  + This assumes a resilient deployment (it can tolerate one node being removed from the cluster).
+ For each node in the cluster, delete it, then run the main cluster.yml, which forces the missing node to be redeployed.  Run with the same parameters as for the main playbook.

### Extra variables:
+ `-e canary=['start', 'finish', 'none']`  -  Specify whether to start or finish a canary deploy, or 'none' deploy
