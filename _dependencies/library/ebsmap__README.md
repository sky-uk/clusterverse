# ebsmap

This is an Ansible module that is able to map AWS EBS device names (including NVME devices) to the host device names.  

## Credits
The bulk of the heavy lifting is nvme ioctl commands written by AWS for their Amazon Linux AMIs.  See: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nvme-ebs-volumes.html

## Execution
This can be run as an Ansible module (needs root):
```yaml
- name: Get the nvme map information
  ebsmap:
  become: yes
  register: r__ebsmap

- name: ebsmap
  debug: msg={{ebsmap}}

```

or from the console:
```bash
python3 ./ebsmap.py console
```