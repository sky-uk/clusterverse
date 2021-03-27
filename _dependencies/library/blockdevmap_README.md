# blockdevmap
This is an Ansible module (or python script) that is able to map AWS, GCP and Azure device names to the host device names.  It returns a list of dictionaries (per disk), derived from Linux `lsblk`, (augmented in the case of AWS & Azure with disk information from other machine metadata).

## Output
### Common
+ `lsblk` is run for options: NAME,TYPE,UUID,FSTYPE,MOUNTPOINT,MODEL,SERIAL,SIZE,HCTL (all of which are supported from CentOS7+ and Ubuntu1804+).
+ _NAME_ is always the OS device name, although in some cases symlinked to a `xvd[\d]` name
    + For convenience, this is copied to a parameter `device_name_os`
+ A parameter `device_name_cloud` is created that relates to the name the cloud gives to the device when it is created.

### AWS
+ On AWS 'nitro' instances all EBS mappings are attached to the NVME controller. The nvme mapping is non-deterministic though, so the script uses ioctl commands to query the nvme controller (from a script by Amazon that is present on 'Amazon Linux' machines: `/sbin/ebsnvme-id`.  See documentation: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nvme-ebs-volumes).
+ For non-nitro EBS mapping, the script enumerates the mapping in the alphanumerical order of the disk device names.  This is the correct order except for some very old RHEL/Centos AMIs, which are not supported.
+ For ephemeral volume mapping, it uses the http://169.254.169.254/latest/meta-data/block-device-mapping/ endpoint.

### GCP
+ GCP device names are user-defined, and appear as entries in the `lsblk` _SERIAL_ column (which is copied for consistency to `device_name_cloud`).

### Azure
+ Azure LUNs are user-defined, and appear as the last entry in the `lsblk` _HCTL_ column, (which is copied for consistency to `device_name_cloud`).

### lsblk
+ The script can be run as plain `lsblk` command, where the cloud provider does not include a mapping, and will return the information as a dictionary.  For example, the _bytes_ mapped to the _NAME_ field could be cross-checked against the requested disk size to create a mapping.


## Execution
This can be run as an Ansible module (needs root):
```yaml
- name: Get block device map information for cloud
  blockdevmap:
    cloud_type: <gcp|aws|azure>
  become: yes
  register: r__blockdevmap

- name: Get lsblk device map information
  blockdevmap:
    cloud_type: lsblk
  become: yes
  register: r__blockdevmap

- name: debug blockdevmap
  debug: msg={{r__blockdevmap}}
```

or from the console:
```bash
python3 ./blockdevmap.py console
```