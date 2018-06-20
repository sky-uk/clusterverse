# devops-ansible-template
This project provides a template Ansible playbook to create (cloud) infrastructure. 

## Requirements
Ansible >=2.5.3 is required on the localhost (v2.4.0, 2.4.2, 2.5.1, 2.5.3 contain [bug](https://github.com/ansible/ansible/issues/33433), [bug](https://github.com/ansible/ansible/pull/38302), [bug](https://github.com/ansible/ansible/issues/38656) that cause a failures)

## Variables to suit your project

### group_vars:
#### all.yml:
```
clusterid: aws_eu_west_1          # Must be an index into cluster_vars in cluster_vars.yml
buildenv:                         # Must be an index into cluster_vars[clusterid].host_vars in cluster_vars.yml
app_class: "test"                 # The class of application - applies to the fqdn
clustername_prefix: "qwerty"      # Gives a customised name for identification purposes (it is part of cluster_name, and identifies load balancers etc in cloud environments) 
dns_tld_external: "example.com"   # Top-level domain (above the level defined per clusterid)
```

#### cluster_vars.yml:
```
  aws_eu_west_1:
    type: aws
#    image: "ami-3548444c" #Centos 7 (1805_1)
#    image: "ami-8fd760f6"  #Ubuntu 16.04
    image: "ami-0b91bd72"  #Ubuntu 18.04
    region: "eu-west-1"
    assign_public_ip: "no"
    dns_zone_internal: "eu-west-1.compute.internal"
    dns_zone_external: "{%- if dns_tld_external -%}  aws_euw1.{{app_class}}.{{buildenv}}.{{dns_tld_external}}  {%- endif -%}"
    dns_server: "infoblox"    # Specify DNS server. infoblox or openstack (on openstack) supported.  If empty string is specified, no DNS will be added.
    dev:
      host_vars:
        test: {count_per_az: 1, az: ["a", "b"], flavor: t2.micro, ephemeral_volumes: [{"device_name": "/dev/sdb", "volume_type": "gp2", "volume_size": 2, "delete_on_termination": true}]}
      aws_access_key:
      aws_secret_key:
      vpc_name: "dev"
      vpc_subnet_name_prefix: "dev-infrastructure-subnet"
      key_name: "dev-key"
      termination_protection: "yes"
      secgroups_existing: []
      secgroup_new:
        - proto: "tcp"
          ports: [22]
          cidr_ip: 10.0.0.0/8
          rule_desc: "SSH Access"
        - proto: "tcp"
          ports: ["{{prometheus_node_exporter_port}}"]
          group_name: ["dev-private-sg"]
          rule_desc: "Prometheus instances attached to dev-private-sg can access the exporter port(s)."
        - proto: all
          group_name: ["{{ cluster_name }}-sg"]
          rule_desc: "Access from all VMs attached to the {{ cluster_name }}-sg group"
```

## Prerequisites
### AWS
- AWS account with IAM rights to create EC2 VMs + Security Groups in the chosen VPC/Subnets
- Already created VPCs subnet ID
- Already created Subnets IDs

### GCP
- Create a gloud account.
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
- ansible 2.4.x
- python 2.7
- pip:
  - aws-cli
  - boto3

Dependencies can be managed via Pipenv:
```bash
pipenv install
```
Will create a Python virtual environment with dependencies specified in the Pipfile

To active it, simply enter:
```bash
pipenv shell
```


In order to access credentials encrypted by Ansible-Vault, the `VAULT_PASSORD` environment variable needs to be added to your ~/.bashrc (or exported at runtime):
```
export VAULT_PASSORD=password
```

## Invocation
#### AWS:
```
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml --tags=clusterbuild_clean -e clean=true -e buildenv=dev -e clusterid=aws_eu_west_1
ansible-playbook -u ubuntu --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e clean=true -e buildenv=dev -e clusterid=aws_eu_west_1 -e skip_package_upgrade=true
```
#### GCP:
```
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml --tags=clusterbuild_clean -e clean=true -e buildenv=dev -e  -e clusterid=gce_eu_west1
ansible-playbook -u <username> --private-key=/home/<user>/.ssh/<rsa key> cluster.yml -e clean=true -e buildenv=dev -e clusterid=gce_eu_west1 -e skip_package_upgrade=true
```
#### Openstack:
```
ansible-playbook -u centos --private-key=/home/<user>/.ssh/<rsa_key> cluster.yml --tags=clusterbuild_clean -e clean=true -e buildenv=dev -e clusterid=m25_lsd_slo
ansible-playbook -u centos --private-key=/home/<user>/.ssh/<rsa_key> cluster.yml -e clean=true -e buildenv=dev -e clusterid=m25_lsd_slo -e skip_package_upgrade=true
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
### Tags
- clusterbuild_clean: Deletes all VMs and security groups (also needs `-e clean=true` on command line) 
- clusterbuild_create: Creates only EC2 VMs, based on the host_vars values in group_vars/all/cluster.yml  
- clusterbuild_config: Updates packages, sets hostname, adds hosts to DNS


---

# redeploy.yml
This playbook enables a basic rolling redeployment of the cluster - e.g. if it is desired to upgrade each node without downtime (assumes a resilient deployment).
For each node in the cluster, delete it, then run the main cluster.yml, which forces the missing node to be redeployed.  Run with the same parameters as for the main playbook.
