# clusterverse  &nbsp; [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) ![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)
A full-lifecycle, immutable cloud infrastructure cluster management **role**, using Ansible.
+ **Multi-cloud:** clusterverse can manage cluster lifecycle in AWS, GCP, Azure and Free ESXi (standalone host only, not vCentre).
+ **Deploy:**  You define your infrastructure as code (in Ansible yaml), and clusterverse will deploy it 
+ **Scale-up:**  If you change the cluster definitions and rerun the deploy, new nodes will be added.
+ **Redeploy (e.g. up-version):** If you need to up-version, or replace the underlying OS, (i.e. to achieve fully immutable, zero-patching redeploys), the `redeploy.yml` playbook will replace each node in the cluster (via various redeploy schemes), and rollback if any failures occur. 

**clusterverse** is designed to manage base-vm infrastructure that underpins cluster-based infrastructure, for example, Couchbase, Kafka, Elasticsearch, or Cassandra.

## Contributing
Contributions are welcome and encouraged.  Please see [CONTRIBUTING.md](https://github.com/sky-uk/clusterverse/blob/master/CONTRIBUTING.md) for details.

## Requirements

### Python dependencies
Dependencies are managed via pipenv:
+ `pipenv install`  will create a Python virtual environment with dependencies specified in the Pipfile

To active the pipenv:
+ `pipenv shell`
+ or prepend the ansible-playbook commands with: `pipenv run`

### AWS
+ AWS account with IAM rights to create EC2 VMs and security groups in the chosen VPCs/subnets.  Place the credentials in:
  + `cluster_vars[buildenv].aws_access_key:`
  + `cluster_vars[buildenv].aws_secret_key:`
+ Preexisting VPCs:
  + `cluster_vars[buildenv].vpc_name: my-vpc-{{buildenv}}`
+ Preexisting subnets. This is a prefix - the cloud availability zone will be appended to the end (e.g. `a`, `b`, `c`).
  + `cluster_vars[buildenv].vpc_subnet_name_prefix: my-subnet-{{region}}`
+ Preexisting keys (in AWS IAM):
  + `cluster_vars[buildenv].key_name: my_key__id_rsa`

### GCP
+ Create a gcloud account.
+ Create a service account in `IAM & Admin` / `Service Accounts`.  Download the json file locally.
+ Store the contents within the `cluster_vars[buildenv].gcp_service_account_rawtext` variable. 
  + During execution, the json file will be copied locally because the Ansible GCP modules often require the file as input. 
+ Google Cloud SDK needs to be installed to run gcloud command-line (e.g. to disable delete protection) - this is handled by `pipenv install`

### ESXi (free)
+ Username & password for a privileged user on an ESXi host
+ SSH must be enabled on the host
+ Set the `Config.HostAgent.vmacore.soap.maxSessionCount` variable to 0 to allow many concurrent tests to run.   
+ Set the `Security.SshSessionLimit` variable to max (100) to allow as many ssh sessions as possible.   

### Azure
+ Create an Azure account.
+ Create a Tenant and a Subscription
+ Create a Resource group and networks/subnetworks within that.
+ Create a service principal - add the credentials to:
  + `cluster_vars[buildenv].azure_subscription_id`
  + `cluster_vars[buildenv].azure_client_id`
  + `cluster_vars[buildenv].azure_secret`
  + `cluster_vars[buildenv].azure_tenant`


### DNS
DNS is optional.  If unset, no DNS names will be created.  If DNS is required, you will need a DNS zone delegated to one of the following:
+ nsupdate (e.g. bind9)
+ AWS Route53
+ Google Cloud DNS

Credentials to the DNS server will also be required. These are specified in the `cluster_vars` variable described below.


### Cluster Definition Variables
Clusters are defined as code within Ansible yaml files that are imported at runtime.  Because clusters are built from scratch on the localhost, the automatic Ansible `group_vars` inclusion cannot work with anything except the special `all.yml` group (actual `groups` need to be in the inventory, which cannot exist until the cluster is built).  The `group_vars/all.yml` file is instead used to bootstrap _merge_vars_.

#### merge_vars
Clusterverse is designed to be used to deploy the same clusters in multiple clouds and multiple environments, potentially using similar configurations.  In order to avoid duplicating configuration (adhering to the [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) principle), a new [action plugin](https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#action-plugins) has been developed (called `merge_vars`) to use in place of the standard `include_vars`, which allows users to define the variables hierarchically, and include (and potentially override) those defined before them.  This plugin is similar to `include_vars`, but when it finds dictionaries that have already been defined, it _combines_ them instead of replacing them. 

```yaml
- merge_vars:
    ignore_missing_files: True
    from: "{{ merge_dict_vars_list }}"     #defined in `group_vars/all.yml`
```
 + The variable _ignore_missing_files_ can be set such that any files or directories that are not found in the defined 'from' list will not raise an error.

<br/>

##### merge_dict_vars_list - hierarchical:
In the case of a fully hierarchical set of cluster definitions where each directory is a variable, (e.g. _cloud_ (aws or gcp), _region_ (eu-west-1) and _cluster_id_ (test)), the folders may look like:  

```text
|-- aws
|   |-- eu-west-1
|   |   |-- sandbox
|   |   |   |-- test
|   |   |   |   `-- cluster_vars.yml
|   |   |   `-- cluster_vars.yml
|   |   `-- cluster_vars.yml
|   `-- cluster_vars.yml
|-- gcp
|   |-- europe-west1
|   |   `-- sandbox
|   |       |-- test
|   |       |   `-- cluster_vars.yml
|   |       `-- cluster_vars.yml
|   `-- cluster_vars.yml
|-- app_vars.yml
`-- cluster_vars.yml
```

`group_vars/all.yml` would contain `merge_dict_vars_list` with the files and directories, listed from top to bottom in the order in which they should override their predecessor:
```yaml
merge_dict_vars_list:
  - "./cluster_defs/cluster_vars.yml"
  - "./cluster_defs/app_vars.yml"
  - "./cluster_defs/{{ cloud_type }}/"
  - "./cluster_defs/{{ cloud_type }}/{{ region }}/"
  - "./cluster_defs/{{ cloud_type }}/{{ region }}/{{ buildenv }}/"
  - "./cluster_defs/{{ cloud_type }}/{{ region }}/{{ buildenv }}/{{ clusterid }}/"
```

<br/>

##### merge_dict_vars_list - flat:

It is also valid to define all the variables in a single sub-directory:
```text
cluster_defs/
|-- test_aws_euw1
|   |-- app_vars.yml
|   +-- cluster_vars.yml
+-- test_gcp_euw1
    |-- app_vars.yml
    +-- cluster_vars.yml
```
In this case, `merge_dict_vars_list` would be only the top-level directory (using `cluster_id` as a variable).  `merge_vars` does not recurse through directories.
```yaml
merge_dict_vars_list:
  - "./cluster_defs/{{ clusterid }}"
```

<br/>

#### /group_vars/{{cluster_id}}/*.yml:
If `merge_dict_vars_list` is not defined, it is still possible to put the flat variables in `/group_vars/{{cluster_id}}`, where they will be imported using the standard `include_vars` plugin.  

This functionality offers no advantages over simply defining the same cluster yaml files in the directory structure defined in `merge_dict_vars_list - flat` merge_vars technique above, and that is considered preferred. 

<br/>

### Cloud Credential Management
Credentials can be encrypted inline in the playbooks using [ansible-vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html).
+ Because multiple environments are supported, it is recommended to use [vault-ids](https://docs.ansible.com/ansible/latest/user_guide/vault.html#managing-multiple-passwords-with-vault-ids), and have credentials per environment (e.g. to help avoid accidentally running a deploy on prod).
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
      7669080460651349243347331538721104778691266429457726036813912140404310
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

To import the role into your project, create a [`requirements.yml`](https://github.com/sky-uk/clusterverse/blob/master/EXAMPLE/requirements.yml) file containing:
```
roles:
  - name: clusterverse
    src: https://github.com/sky-uk/clusterverse
    version: master          ## branch, hash, or tag 
```
+ If you use a `cluster.yml` file similar to the example found in [EXAMPLE/cluster.yml](https://github.com/sky-uk/clusterverse/blob/master/EXAMPLE/cluster.yml), clusterverse will be installed from Ansible Galaxy _automatically_ on each run of the playbook.

+ To install it manually: `ansible-galaxy install -r requirements.yml -p /<project>/roles/`


### Invocation

_**For full invocation examples and command-line arguments, please see the [example README.md](https://github.com/sky-uk/clusterverse/blob/master/EXAMPLE/README.md)**_

The role is designed to run in two modes:
#### Deploy (also performs _scaling_ and _repairs_)
+ A playbook based on the [cluster.yml example](https://github.com/sky-uk/clusterverse/tree/master/EXAMPLE/cluster.yml) will be needed.
+ The `cluster.yml` sub-role immutably deploys a cluster from the config defined above.  If it is run again (with no changes to variables), it will do nothing.  If the cluster variables are changed (e.g. add a host), the cluster will reflect the new variables (e.g. a new host will be added to the cluster.  Note: it _will not remove_ nodes, nor, usually, will it reflect changes to disk volumes - these are limitations of the underlying cloud modules).


#### Redeploy
+ A playbook based on the [redeploy.yml example](https://github.com/sky-uk/clusterverse/tree/master/EXAMPLE/redeploy.yml) will be needed.
+ The `redeploy.yml` sub-role will completely redeploy the cluster; this is useful for example to upgrade the underlying operating system version.
+ It supports `canary` deploys.  The `canary` extra variable must be defined on the command line set to one of: `start`, `finish`, `none` or `tidy`. 
+ It contains callback hooks:
  + `mainclusteryml`: This is the name of the deployment playbook.  It is called to deploy nodes for the new cluster, or to rollback a failed deployment.  It should be set to the value of the primary _deploy_ playbook yml (e.g. `cluster.yml`)
  + `predeleterole`: This is the name of a role that should be called prior to deleting VMs; it is used for example to eject nodes from a Couchbase cluster.  It takes a list of `hosts_to_remove` VMs. 
+ It supports pluggable redeployment schemes.  The following are provided:
  + **_scheme_rmvm_rmdisk_only**
      + This is a very basic rolling redeployment of the cluster.  
      + _Supports redploying to bigger, but not smaller clusters_
      + **It assumes a resilient deployment (it can tolerate one node being deleted from the cluster). There is _no rollback_ in case of failure.**
      + For each node in the cluster:
        + Run `predeleterole`
        + Delete/ terminate the node (note, this is _irreversible_).
        + Run the main cluster.yml (with the same parameters as for the main playbook), which forces the missing node to be redeployed (the `cluster_suffix` remains the same).
      + If the process fails at any point:
        + No further VMs will be deleted or rebuilt - the playbook stops. 
  + **_scheme_addnewvm_rmdisk_rollback**
      + _Supports redploying to bigger or smaller clusters_
      + For each node in the cluster:
        + Create a new VM
        + Run `predeleterole` on the previous node
        + Shut down the previous node.
      + If `canary=start`, only the first node is redeployed.  If `canary=finish`, only the remaining (non-first), nodes are redeployed.  If `canary=none`, all nodes are redeployed.
      + If the process fails for any reason, the old VMs are reinstated, and any new VMs that were built are stopped (rollback)
      + To delete the old VMs, either set '-e canary_tidy_on_success=true', or call redeploy.yml with '-e canary=tidy'
  + **_scheme_addallnew_rmdisk_rollback**
      + _Supports redploying to bigger or smaller clusters_
      + If `canary=start` or `canary=none`
        + A full mirror of the cluster is deployed.
      + If `canary=finish` or `canary=none`:
          + `predeleterole` is called with a list of the old VMs.
          + The old VMs are stopped.
      + If the process fails for any reason, the old VMs are reinstated, and the new VMs stopped (rollback)
      + To delete the old VMs, either set '-e canary_tidy_on_success=true', or call redeploy.yml with '-e canary=tidy'
  + **_scheme_rmvm_keepdisk_rollback**
      + Redeploys the nodes one by one, and moves the secondary (non-root) disks from the old to the new (note, only non-ephemeral disks can be moved).
      + _Cluster node topology must remain identical.  More disks may be added, but none may change or be removed._
      + **It assumes a resilient deployment (it can tolerate one node being removed from the cluster).**
      + For each node in the cluster:
        + Run `predeleterole`
        + Stop the node
        + Detach the disks from the old node
        + Run the main cluster.yml to create a new node
        + Attach disks to new node
      + If `canary=start`, only the first node is redeployed.  If `canary=finish`, only the remaining (non-first), nodes are replaced.  If `canary=none`, all nodes are redeployed.
      + If the process fails for any reason, the old VMs are reinstated (and the disks reattached to the old nodes), and the new VMs are stopped (rollback)
      + To delete the old VMs, either set '-e canary_tidy_on_success=true', or call redeploy.yml with '-e canary=tidy'
      + (Azure functionality coming soon)
