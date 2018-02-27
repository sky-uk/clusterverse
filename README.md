
This project provides a template to build Ansible playbook for AWS.


### fqdn
b-haproxy0.proxy.dev.example.com
availabilityzone-role + index .application.environment.example.com
eg: b-haproxy0.proxy.dev.example.com
### chage the variable to fit your Project

### Group_Vars:
all.yml:

```
buildenv: dev                 # defult environment is dev, you can change it by add -e to your ansible-playbook command eg: ansible-playbook ansible.yaml -e buildenv=stage
cluster: aws_eu_west1         # defualt cluster
application: "database"       # name of your application for example prox, database. this will be part of your domain name. example anginx0.proxy.dev.example.com

```

cluster.yml:
```
cluster_vars:
  aws_eu_west1:
    type: aws
    image: "ami-8fd760f6"
    assign_public_ip: "no"
    dev:
      region: "eu-west-1"
      host_vars:
        # applicationr role (eg: etcd, nginx):{ number of instances, availability zones, type of instances}  exampple testdb: {count_per_az: 1, az: ["a", "b", "c"], flavor: t2.medium } #
        testdb: {count_per_az: 1, az: ["a", "b", "c"], flavor: t2.medium }
      dns_zone: "{{application}}.dev.example.com" # proxy.dev.example.com
      dns_zone_external: "{{application}}.dev.example.com"
      aws_access_key:
      aws_secret_key:
      vpc_id: ""
      vpc_subnet_id_per_az:
        a: ""
        b: ""
        c: ""
      key_name: "dev-key"
      security_groups:
        - 'dev-private-sg'
      rules:
         - proto: "tcp"
           ports: 22
           cidr_ip: 10.0.0.0/8  # internal ip range. This can be change per environment. for example if you wish to have more ristricted security in prd you can just change the range to your application
      rules_egress:
        - proto: all
          cidr_ip: 0.0.0.0/0
      volumes:
        - device_name: /dev/sdb
          volume_type: gp2
          volume_size: 100
          delete_on_termination: true
```

### Requirements
### AWS

- AWS account with IAM rights to create EC2 VMs + Security Groups in the chosen VPC/Subnets
- Already created VPCs subnet ID
- Already created Subnets IDs

### Other

- Infoblox access and credentials
- Internal DNS zone delegated to the Infoblox instance (eg. example.com)

### Software

- ansible 2.4.x
- python 2.7
- pip:
  - aws-cli
  - boto3

The following environment variable needs to be added to your ~/.bashrc: `export VAULT_PASSORD=password` to access credentials encrypted by Ansible-Vault.

### How to run it

ansible-playbook ansible.yaml -u ubuntu  --ask-vault-pass --private-key=
or ansible-playbook ansible.yaml -u ubuntu  --ask-vault-pass --private-key=~ -e buildenv=prod

### Tags

- create: Creates only EC2 VMs, based on the host_vars values in group_vars/all/cluster.yml  
- config: Installs packages, dependencies and Couchbase related optimizations


### Warning

This is a work in progress project and not production ready (yet)
