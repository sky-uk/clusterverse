# devops-ansible-template
This project provides a template Ansible playbook to create (cloud) infrastructure. 


## Variables to suit your project

### group_vars:
#### all.yml:
```
clusterid: aws_eu_west_1          # Must be an index into cluster_vars in cluster_vars.yml
buildenv:                         # Must be an index into cluster_vars[clusterid].host_vars in cluster_vars.yml
clustername_prefix: "test"        # Gives a customised name for identification purposes
```

#### cluster_vars.yml:
```
cluster_vars:
  aws_eu_west_1:
    type: aws
    image: "ami-8fd760f6"  #Ubuntu
    region: "eu-west-1"
    assign_public_ip: "no"
    dns_zone: "{{cluster_name}}.{{buildenv}}.example.com"
    dns_zone_external: "{{cluster_name}}.{{buildenv}}.example.com"
    dev:
      host_vars:
        # application role (eg: etcd, nginx):{ number of instances, availability zones, type of instances}  example testdb: {count_per_az: 1, az: ["a", "b", "c"], flavor: t2.medium } #
        test: {count_per_az: 1, az: ["a", "b"], flavor: t2.micro}
      aws_access_key:
      aws_secret_key:
      vpc_name: "dev"
      vpc_subnet_name_prefix: "dev-infrastructure-subnet"
      key_name: "dev-key"
      security_groups: ['dev-private-sg']
      sg_rules:
        - proto: "tcp"
          ports: [80,443]
          cidr_ip: 10.0.0.0/8
        - proto: all
          group_name:
            - "dev-private-sg"
```

## Prerequisites
### AWS

- AWS account with IAM rights to create EC2 VMs + Security Groups in the chosen VPC/Subnets
- Already created VPCs subnet ID
- Already created Subnets IDs

### Other

- Infoblox access and credentials
- Internal DNS zone delegated to the Infoblox instance (eg. example.com)

### Localhost

- ansible 2.4.x
- python 2.7
- pip:
  - aws-cli
  - boto3

In order to access credentials encrypted by Ansible-Vault, the `VAULT_PASSORD` environment variable needs to be added to your ~/.bashrc (or exported at runtime):
```
export VAULT_PASSORD=password
```

## Invocation
ansible-playbook -b -u ubuntu --private-key=<rsa key> cluster.yml -e buildenv=prod

### Extra variables:
+ `-e buildenv=<environment>`  -  dev/ stage/ prod supported
+ `-e clean=true` - Deletes all existing VMs and security groups before creating

### Tags
- clean: Deletes all VMs and security groups (also needs `-e clean=true` on command line) 
- create: Creates only EC2 VMs, based on the host_vars values in group_vars/all/cluster.yml  
- config: Updates packages, sets hostname, adds hosts to DNS


## Warning

This is a work in progress project and not production ready (yet)
