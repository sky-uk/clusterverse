# clusterverse  &nbsp; [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) ![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)
A full-lifecycle, immutable cloud infrastructure cluster management **role**, using Ansible.
+ **Multi-cloud:** clusterverse can manage cluster lifecycle in AWS and GCP
+ **Deploy:**  You define your infrastructure as code (in Ansible yaml), and clusterverse will deploy it 
+ **Scale (e.g. add a node):**  If you change the config yaml and rerun the deploy, new nodes will be added.
+ **Redeploy (e.g. up-version):** If you need to up-version, the `redeploy.yml` playbook will replace each node in turn, (with optional callbacks), and rollback if any failures occur. 

**clusterverse** is designed to deploy base-vm infrastructure that underpins cluster-based infrastructure, for example, Couchbase, or Cassandra.

## Contributing
Contributions are welcome and encouraged.  Please see [CONTRIBUTING.md](https://github.com/sky-uk/clusterverse/blob/master/CONTRIBUTING.md) for details.

## Requirements

### Python dependencies
Dependencies are managed via Pipenv:
+ `pipenv install`  will create a Python virtual environment with dependencies specified in the Pipfile

To active the pipenv:
+ `pipenv shell`
+ or prepend the ansible-playbook commands with: `pipenv run`

### AWS
+ AWS account with IAM rights to create EC2 VMs + Security Groups in the chosen VPC/Subnets
+ Preexisting VPCs
+ Preexisting subnets

### GCP
+ Create a gcloud account.
+ Create a service account in `IAM & Admin` / `Service Accounts`.  Download the json file locally. 
  + This file is used in the `GCP_CREDENTIALS` environment variable that is read in `group_vars/<clusterid>/cluster_vars.yml`.  
  + You need to export this variable (e.g. `export GCP_CREDENTIALS=/home/<user>/src/gcp.json`).
+ Google Cloud SDK needs to be installed to run gcloud command-line (e.g. to disable delete protection) - this is handled by `pipenv install`

### DNS
DNS is optional.  If unset, no DNS names will be created.  If required, you will need a DNS zone delegated to one of the following:
+ Bind9
+ Route53

Credentials to the DNS server will also be required. These are specified in the `cluster_vars.yml` file described below.

### Cloud credential management
Credentials can be encrypted inline in the playbooks using [ansible-vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html).
+ Because multiple environments are supported, it is recommended to use [vault-ids](https://docs.ansible.com/ansible/latest/user_guide/vault.html#multiple-vault-passwords), and have credentials per environment (e.g. to help avoid accidentally running a deploy on prod).
+ There is a small script (`.vaultpass-client.py`) that returns a password stored in an environment variable (`VAULT_PASSWORD_BUILDENV`) to ansible. Setting this variable is mandatory within Clusterverse as if you need to decrypt sensitive data within `ansible-vault`, the password set within the variable will be used. This is particularly useful for running within Jenkins.
  + `export VAULT_PASSWORD_BUILDENV=<'dev/stage/prod' password>`
+ To encrypt sensitive information, you must ensure that your current working dir can see the script `.vaultpass-client.py` and `VAULT_PASSWORD_BUILDENV` has been set:
  + `ansible-vault encrypt_string --vault-id=sandbox@.vaultpass-client.py --encrypt-vault-id=sandbox`
    + An example of setting a sensitive value could be your `aws_secret_key`. When running the cmd above, a prompt will appear such as:
    ```
    ansible-vault encrypt_string --vault-id=sandbox@.vaultpass-client.py --encrypt-vault-id=sandbox
    Reading plaintext input from stdin. (ctrl-d to end input)
    ```
    + Enter your plaintext input, then when finished press `CTRL-D` on your keyboard. Sometimes scrambled text will appear after pressing the combination such as `^D`, press the same combination again and your scrambled hash will be displayed. Copy this as a value for your string within your `cluster_vars.yml` or `app_vars.yml` files. Example below:
    ```
    aws_secret_key: !vault |-
      $ANSIBLE_VAULT;1.2;AES256;sandbox
      306164313163633832323236323462333438323061663737666331366631303735666466626434393830356461363464633264623962343262653433383130390a343964393336343564393862316132623734373132393432396366626231376232636131666430666366636466393664353435323561326338333863633131620a66393563663736353032313730613762613864356364306163363338353330383032313130663065666264396433353433363062626465303134613932373934
    ```
    + Notice `!vault |-` this is compulsory in order for the hash to be successfully decrypted
+ To decrypt, either run the playbook with the correct `VAULT_PASSWORD_BUILDENV` and just `debug: msg={{myvar}}`, or:
  + `echo '$ANSIBLE_VAULT;1.2;AES256;sandbox`
  `86338616...33630313034' | ansible-vault decrypt --vault-id=sandbox@.vaultpass-client.py`  
  + **or**, to decrypt using a non-exported password:
  + `echo '$ANSIBLE_VAULT;1.2;AES256;sandbox`
  `86338616...33630313034' | ansible-vault decrypt --ask-vault-pass`


---
## Usage
**clusterverse** is an Ansible _role_, and as such must be imported into your \<project\>/roles directory.  There is a full-featured example in the [/EXAMPLE](https://github.com/sky-uk/clusterverse/tree/master/EXAMPLE) subdirectory.

To import the role into your project, create a `requirements.yml` file containing:
```
- src: https://github.com/sky-uk/clusterverse
  version: master           ## or hash, or version 
  name: clusterverse
```
To install the role into a project's `roles` directory: 
+ `ansible-galaxy install -r requirements.yml -p /<project>/roles/`


### Cluster Variables
+ The clusters are defined as code, within Ansible yaml files that are automatically imported.
+ One of the mandatory command-line variables is `clusterid`, which defines the name of the directory under `group_vars`, from which variable files will be imported.
+ Please see the full AWS and GCP [example group_vars](https://github.com/sky-uk/clusterverse/tree/master/EXAMPLE/group_vars/) 


### Invocation

_**For full invocation examples and command-line arguments, please see the [example README.md](https://github.com/sky-uk/clusterverse/blob/master/EXAMPLE/README.md)**_

The role is designed to run in two modes:
#### Deploy (also performs _scaling_ and _repairs_)
+ A playbook based on the [cluster.yml example](https://github.com/sky-uk/clusterverse/tree/master/EXAMPLE/cluster.yml) will be needed.
+ The `cluster.yml` sub-role immutably deploys a cluster from the config defined above.  If it is run again it will do nothing.  If the cluster_vars are changed (e.g. add a host), the cluster will reflect the new variables (e.g. a new host will be added to the cluster).


#### Redeploy
+ A playbook based on the [redeploy.yml example](https://github.com/sky-uk/clusterverse/tree/master/EXAMPLE/redeploy.yml) will be needed.
+ The `redeploy.yml` sub-role will completely redeploy the cluster; this is useful for example to upgrade the underlying operating system version.
+ It contains callback hooks:
  + `mainclusteryml`: This is the name of the deployment playbook.  It is called to rollback a failed deployment.  It should be set to the value of the primary _deploy_ playbook yml (e.g. `cluster.yml`)
  + `predeleterole`: This is the name of a role that should be called prior to deleting a VM.
+ It supports pluggable infrastructure redeployment schemes.  Two are provided:
  + **_scheme_rmvm_rmdisks_only**
    This scheme runs a very basic rolling redeployment of the cluster.
      + For each node in the cluster, delete it, then run the main cluster.yml, which forces the missing node to be redeployed.  Run with the same parameters as for the main playbook.
      + **This assumes a resilient deployment (it can tolerate one node being removed from the cluster).**
  + **_scheme_addnewvm_rmdisk_rollback**
    This scheme runs a more advanced rolling redeployment of the cluster.
      + For each VM, firstly, a new VM is created, and then the old one is shut down.
      + If the process proceeds correctly for all the VMs, the old (now shut-down) VMs, are terminated
      + If the process fails for any reason, the old VMs are reinstated.

