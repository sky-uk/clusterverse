# Copyright 2020 Dougal Seeley <github@dougalseeley.com>
# BSD 3-Clause License
# https://github.com/dseeley/blockdevmap

# Copyright 2017 Amazon.com, Inc. and its affiliates. All Rights Reserved.
# Licensed under the MIT License. See the LICENSE accompanying this file
# for the specific language governing permissions and limitations under
# the License.
# /sbin/ebsnvme-id - https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/nvme-ebs-volumes.html

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
---
module: blockdevmap
version_added: 1.0.0
short_description: blockdevmap
description:
    - Map the block device name as defined in AWS/GCP/Azure (e.g. /dev/sdf) with the volume provided to the OS
authors:
    - Dougal Seeley <blockdevmap@dougalseeley.com>
    - Amazon.com Inc.
'''

EXAMPLES = '''
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
'''

RETURN = '''
## AWS Nitro
"device_map": [
    {
        "FSTYPE": "ext4",
        "MOUNTPOINT": "/media/mysvc",
        "NAME": "nvme1n1",
        "PARTLABEL": "",
        "SERIAL": "vol0c2c47ee4516063e9",
        "TYPE": "disk",
        "UUID": "c3630dbe-042e-44e5-ac67-54fa1c9e4cd2",
        "device_name_cloud": "/dev/sdf",
        "device_name_os": "/dev/nvme1n1",
        "volume_id": "vol-0c2c47ee4516063e9"
    },
    {
        "FSTYPE": "",
        "MOUNTPOINT": "",
        "NAME": "nvme0n1",
        "PARTLABEL": "",
        "SERIAL": "vol0b05e48d5677db81a",
        "TYPE": "disk",
        "UUID": "",
        "device_name_cloud": "/dev/sda1",
        "device_name_os": "/dev/nvme0n1",
        "volume_id": "vol-0b05e48d5677db81a"
    },
    {
        "FSTYPE": "ext4",
        "MOUNTPOINT": "/",
        "NAME": "nvme0n1p1",
        "PARTLABEL": "",
        "SERIAL": "",
        "TYPE": "part",
        "UUID": "96ec7adb-9d94-41c0-96a5-d6992c9d5f20",
        "device_name_cloud": "/dev/sda1",
        "device_name_os": "/dev/nvme0n1p1",
        "volume_id": "vol-0b05e48d5677db81a"
    }
    
## AWS non-Nitro
"device_map": [
    {
        "FSTYPE": "",
        "MOUNTPOINT": "",
        "NAME": "xvda",
        "PARTLABEL": "",
        "SERIAL": "",
        "TYPE": "disk",
        "UUID": "",
        "device_name_cloud": "/dev/sda",
        "device_name_os": "/dev/xvda"
    },
    {
        "FSTYPE": "ext4",
        "MOUNTPOINT": "/",
        "NAME": "xvda1",
        "PARTLABEL": "",
        "SERIAL": "",
        "TYPE": "part",
        "UUID": "96ec7adb-9d94-41c0-96a5-d6992c9d5f20",
        "device_name_cloud": "/dev/sda1",
        "device_name_os": "/dev/xvda1"
    }

## AZURE    
"device_map": [
    {
        "FSTYPE": "",
        "HCTL": "0:0:0:0",
        "MODEL": "Virtual Disk",
        "MOUNTPOINT": "",
        "NAME": "sda",
        "SERIAL": "6002248071748569390b23178109d35e",
        "SIZE": "32212254720",
        "TYPE": "disk",
        "UUID": "",
        "device_name_cloud": "ROOTDISK",
        "device_name_os": "/dev/sda",
        "parttable_type": "gpt"
    },
    {
        "FSTYPE": "xfs",
        "HCTL": "",
        "MODEL": "",
        "MOUNTPOINT": "/boot",
        "NAME": "sda1",
        "SERIAL": "",
        "SIZE": "524288000",
        "TYPE": "part",
        "UUID": "8bd4ad1d-13a7-4bb1-a40c-b05444f11db3",
        "device_name_cloud": "",
        "device_name_os": "/dev/sda1",
        "parttable_type": "gpt"
    },
    {
        "FSTYPE": "",
        "HCTL": "",
        "MODEL": "",
        "MOUNTPOINT": "",
        "NAME": "sda14",
        "SERIAL": "",
        "SIZE": "4194304",
        "TYPE": "part",
        "UUID": "",
        "device_name_cloud": "",
        "device_name_os": "/dev/sda14",
        "parttable_type": "gpt"
    },
    {
        "FSTYPE": "vfat",
        "HCTL": "",
        "MODEL": "",
        "MOUNTPOINT": "/boot/efi",
        "NAME": "sda15",
        "SERIAL": "",
        "SIZE": "519045632",
        "TYPE": "part",
        "UUID": "F5EB-013D",
        "device_name_cloud": "",
        "device_name_os": "/dev/sda15",
        "parttable_type": "gpt"
    },
    {
        "FSTYPE": "xfs",
        "HCTL": "",
        "MODEL": "",
        "MOUNTPOINT": "/",
        "NAME": "sda2",
        "SERIAL": "",
        "SIZE": "31161581568",
        "TYPE": "part",
        "UUID": "40a878b6-3fe8-4336-820a-951a19f79a76",
        "device_name_cloud": "",
        "device_name_os": "/dev/sda2",
        "parttable_type": "gpt"
    },
    {
        "FSTYPE": "",
        "HCTL": "0:0:0:1",
        "MODEL": "Virtual Disk",
        "MOUNTPOINT": "",
        "NAME": "sdb",
        "SERIAL": "60022480c891da018bdd14b5dd1895b0",
        "SIZE": "4294967296",
        "TYPE": "disk",
        "UUID": "",
        "device_name_cloud": "RESOURCEDISK",
        "device_name_os": "/dev/sdb",
        "parttable_type": "dos"
    },
    {
        "FSTYPE": "ext4",
        "HCTL": "",
        "MODEL": "",
        "MOUNTPOINT": "/mnt/resource",
        "NAME": "sdb1",
        "SERIAL": "",
        "SIZE": "4292870144",
        "TYPE": "part",
        "UUID": "95192b50-0c76-4a03-99a7-67fdc225504f",
        "device_name_cloud": "",
        "device_name_os": "/dev/sdb1",
        "parttable_type": "dos"
    },
    {
        "FSTYPE": "",
        "HCTL": "1:0:0:0",
        "MODEL": "Virtual Disk",
        "MOUNTPOINT": "",
        "NAME": "sdc",
        "SERIAL": "60022480b71fde48d1f2212130abc54e",
        "SIZE": "1073741824",
        "TYPE": "disk",
        "UUID": "",
        "device_name_cloud": "0",
        "device_name_os": "/dev/sdc",
        "parttable_type": ""
    },
    {
        "FSTYPE": "",
        "HCTL": "1:0:0:1",
        "MODEL": "Virtual Disk",
        "MOUNTPOINT": "",
        "NAME": "sdd",
        "SERIAL": "60022480aa9c0d340c125a5295ee678d",
        "SIZE": "1073741824",
        "TYPE": "disk",
        "UUID": "",
        "device_name_cloud": "1",
        "device_name_os": "/dev/sdd",
        "parttable_type": ""
    }
]
'''

from ctypes import *
from fcntl import ioctl
import subprocess
import os
import sys
import json
import re

try:
    from ansible.module_utils.basic import AnsibleModule
    from ansible.errors import AnsibleError
    from ansible.utils.display import Display
except:
    pass

# FileNotFoundError does not exist in python2 - it is an IOError
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

NVME_ADMIN_IDENTIFY = 0x06
NVME_IOCTL_ADMIN_CMD = 0xC0484E41
AMZN_NVME_VID = 0x1D0F
AMZN_NVME_EBS_MN = "Amazon Elastic Block Store"


class nvme_admin_command(Structure):
    _pack_ = 1
    _fields_ = [("opcode", c_uint8),  # op code
                ("flags", c_uint8),  # fused operation
                ("cid", c_uint16),  # command id
                ("nsid", c_uint32),  # namespace id
                ("reserved0", c_uint64),
                ("mptr", c_uint64),  # metadata pointer
                ("addr", c_uint64),  # data pointer
                ("mlen", c_uint32),  # metadata length
                ("alen", c_uint32),  # data length
                ("cdw10", c_uint32),
                ("cdw11", c_uint32),
                ("cdw12", c_uint32),
                ("cdw13", c_uint32),
                ("cdw14", c_uint32),
                ("cdw15", c_uint32),
                ("reserved1", c_uint64)]


class nvme_identify_controller_amzn_vs(Structure):
    _pack_ = 1
    _fields_ = [("bdev", c_char * 32),  # block device name
                ("reserved0", c_char * (1024 - 32))]


class nvme_identify_controller_psd(Structure):
    _pack_ = 1
    _fields_ = [("mp", c_uint16),  # maximum power
                ("reserved0", c_uint16),
                ("enlat", c_uint32),  # entry latency
                ("exlat", c_uint32),  # exit latency
                ("rrt", c_uint8),  # relative read throughput
                ("rrl", c_uint8),  # relative read latency
                ("rwt", c_uint8),  # relative write throughput
                ("rwl", c_uint8),  # relative write latency
                ("reserved1", c_char * 16)]


class nvme_identify_controller(Structure):
    _pack_ = 1
    _fields_ = [("vid", c_uint16),  # PCI Vendor ID
                ("ssvid", c_uint16),  # PCI Subsystem Vendor ID
                ("sn", c_char * 20),  # Serial Number
                ("mn", c_char * 40),  # Module Number
                ("fr", c_char * 8),  # Firmware Revision
                ("rab", c_uint8),  # Recommend Arbitration Burst
                ("ieee", c_uint8 * 3),  # IEEE OUI Identifier
                ("mic", c_uint8),  # Multi-Interface Capabilities
                ("mdts", c_uint8),  # Maximum Data Transfer Size
                ("reserved0", c_uint8 * (256 - 78)),
                ("oacs", c_uint16),  # Optional Admin Command Support
                ("acl", c_uint8),  # Abort Command Limit
                ("aerl", c_uint8),  # Asynchronous Event Request Limit
                ("frmw", c_uint8),  # Firmware Updates
                ("lpa", c_uint8),  # Log Page Attributes
                ("elpe", c_uint8),  # Error Log Page Entries
                ("npss", c_uint8),  # Number of Power States Support
                ("avscc", c_uint8),  # Admin Vendor Specific Command Configuration
                ("reserved1", c_uint8 * (512 - 265)),
                ("sqes", c_uint8),  # Submission Queue Entry Size
                ("cqes", c_uint8),  # Completion Queue Entry Size
                ("reserved2", c_uint16),
                ("nn", c_uint32),  # Number of Namespaces
                ("oncs", c_uint16),  # Optional NVM Command Support
                ("fuses", c_uint16),  # Fused Operation Support
                ("fna", c_uint8),  # Format NVM Attributes
                ("vwc", c_uint8),  # Volatile Write Cache
                ("awun", c_uint16),  # Atomic Write Unit Normal
                ("awupf", c_uint16),  # Atomic Write Unit Power Fail
                ("nvscc", c_uint8),  # NVM Vendor Specific Command Configuration
                ("reserved3", c_uint8 * (704 - 531)),
                ("reserved4", c_uint8 * (2048 - 704)),
                ("psd", nvme_identify_controller_psd * 32),  # Power State Descriptor
                ("vs", nvme_identify_controller_amzn_vs)]  # Vendor Specific.  NOTE: AWS add the mapping here for both the root *and* the first partition.


class cBlockDevMap(object):
    def __init__(self, module, **kwds):
        self.module = module
        self.device_map = self.get_lsblk()

    def get_lsblk(self):
        # Get all existing block volumes by key=value, then parse this into a dictionary (which excludes non disk and partition block types, e.g. ram, loop).  Cannot use the --json output as it not supported on older versions of lsblk (e.g. CentOS 7)
        lsblk_devices = subprocess.check_output(['lsblk', '-o', 'NAME,TYPE,UUID,FSTYPE,MOUNTPOINT,MODEL,SERIAL,SIZE,HCTL', '-p', '-P', '-b']).decode().rstrip().split('\n')
        os_device_names = [dict((map(lambda x: x.strip("\"").rstrip(), sub.split("="))) for sub in dev.split('\" ') if '=' in sub) for dev in lsblk_devices]
        os_device_names = [dev for dev in os_device_names if dev['TYPE'] in ['disk', 'part', 'lvm']]

        # We call lsblk with '-p', which returns the OS path in the 'NAME' field.  We'll change that .
        for dev in os_device_names:
            dev.update({'device_name_os': dev['NAME']})
            dev.update({'NAME': dev['NAME'].split('/')[-1]})

        # Sort by NAME
        os_device_names.sort(key=lambda k: k['NAME'])

        # Get the partition table type.  Useful to know in case we are checking whether this block device is partition-less.  Cannot use the PTTYPE option to lsblk above, as it is not supported in earlier versions of lsblk (e.g. CentOS7)
        for os_device in os_device_names:
            os_device.update({"parttable_type": ""})
            udevadm_output_lines = subprocess.check_output(['udevadm', 'info', '--query=property', '--name', os_device['device_name_os']]).decode().rstrip().split('\n')
            udevadm_output = dict(s.split('=', 1) for s in udevadm_output_lines)
            if 'ID_PART_TABLE_TYPE' in udevadm_output:
                os_device.update({"parttable_type": udevadm_output['ID_PART_TABLE_TYPE']})
        return os_device_names


class cLsblkMapper(cBlockDevMap):
    def __init__(self, **kwds):
        super(cLsblkMapper, self).__init__(**kwds)


class cAzureMapper(cBlockDevMap):
    def __init__(self, **kwds):
        super(cAzureMapper, self).__init__(**kwds)

        # The Azure root and resource disks are symlinked at install time (by cloud-init) to /dev/disk/cloud/azure_[root|resource]. (They are NOT at predictable /dev/sd[a|b] locations)
        # Other managed 'azure_datadisk' disks are mapped by udev (/etc/udev/rules.d/66-azure-storage.rules) when attached.
        devrootdisk = os.path.basename(os.path.realpath('/dev/disk/cloud/azure_root'))
        devresourcedisk = os.path.basename(os.path.realpath('/dev/disk/cloud/azure_resource'))

        for os_device in self.device_map:
            if os_device['NAME'] not in [devrootdisk, devresourcedisk]:
                lun = os_device['HCTL'].split(':')[-1] if len(os_device['HCTL']) else ""
                os_device.update({"device_name_cloud": lun})
            else:
                os_device.update({"device_name_cloud": "ROOTDISK" if os_device['NAME'] in devrootdisk else "RESOURCEDISK"})


class cGCPMapper(cBlockDevMap):
    def __init__(self, **kwds):
        super(cGCPMapper, self).__init__(**kwds)

        for os_device in self.device_map:
            os_device.update({"device_name_cloud": os_device['SERIAL']})


class cAwsMapper(cBlockDevMap):
    def __init__(self, **kwds):
        super(cAwsMapper, self).__init__(**kwds)

        # Instance stores (AKA ephemeral volumes) do not appear to have a defined endpoint that maps between the /dev/sd[b-e] defined in the instance creation map, and the OS /dev/nvme[0-26]n1 device.
        # For this scenario, we can only return the instance stores in the order that they are defined.  Because instance stores do not survive a poweroff and cannot be detached and reattached, the order doesn't matter as much.
        instance_store_map = []

        response__block_device_mapping = urlopen('http://169.254.169.254/latest/meta-data/block-device-mapping/')
        block_device_mappings = response__block_device_mapping.read().decode().split("\n")
        for block_device_mappings__ephemeral_id in [dev for dev in block_device_mappings if dev.startswith('ephemeral')]:
            response__ephemeral_device = urlopen("http://169.254.169.254/latest/meta-data/block-device-mapping/" + block_device_mappings__ephemeral_id)
            block_device_mappings__ephemeral_mapped = response__ephemeral_device.read().decode()
            instance_store_map.append({'ephemeral_id': block_device_mappings__ephemeral_id, 'ephemeral_map': block_device_mappings__ephemeral_mapped})

        instance_store_count = 0
        for os_device in self.device_map:
            if os_device['NAME'].startswith("nvme"):
                try:
                    dev = cAwsMapper.ebs_nvme_device(os_device['device_name_os'])
                except FileNotFoundError as e:
                    self.module.fail_json(msg=os_device['device_name_os'] + ": FileNotFoundError" + str(e))
                except TypeError as e:
                    if instance_store_count < len(instance_store_map):
                        os_device.update({"device_name_os": os_device['device_name_os'], "device_name_cloud": '/dev/' + instance_store_map[instance_store_count]['ephemeral_map'], "volume_id": instance_store_map[instance_store_count]['ephemeral_id']})
                        instance_store_count += 1
                    else:
                        self.module.warn(u"%s is not an EBS device and there is no instance store mapping." % os_device['device_name_os'])
                except OSError as e:
                    self.module.warn(u"%s is not an nvme device." % os_device['device_name_os'])
                else:
                    os_device.update({"device_name_os": os_device['device_name_os'], "device_name_cloud": '/dev/' + dev.get_block_device(stripped=True).rstrip(), "volume_id": dev.get_volume_id()})
            elif os_device['NAME'].startswith("xvd"):
                os_device.update({"device_name_os": os_device['device_name_os'], "device_name_cloud": '/dev/' + re.sub(r'xvd(.*)', r'sd\1', os_device['NAME'])})
            else:
                os_device.update({"device_name_os": os_device['device_name_os'], "device_name_cloud": ""})

    class ebs_nvme_device():
        def __init__(self, device):
            self.device = device
            self.ctrl_identify()

        def _nvme_ioctl(self, id_response, id_len):
            admin_cmd = nvme_admin_command(opcode=NVME_ADMIN_IDENTIFY, addr=id_response, alen=id_len, cdw10=1)
            with open(self.device, "rt") as nvme:
                ioctl(nvme, NVME_IOCTL_ADMIN_CMD, admin_cmd)

        def ctrl_identify(self):
            self.id_ctrl = nvme_identify_controller()
            self._nvme_ioctl(addressof(self.id_ctrl), sizeof(self.id_ctrl))
            if self.id_ctrl.vid != AMZN_NVME_VID or self.id_ctrl.mn.decode().strip() != AMZN_NVME_EBS_MN:
                raise TypeError("[ERROR] Not an EBS device: '{0}'".format(self.device))

        def get_volume_id(self):
            vol = self.id_ctrl.sn.decode()
            if vol.startswith("vol") and vol[3] != "-":
                vol = "vol-" + vol[3:]
            return vol

        def get_block_device(self, stripped=False):
            device = self.id_ctrl.vs.bdev.decode()
            if stripped and device.startswith("/dev/"):
                device = device[5:]
            return device


def main():
    if not (len(sys.argv) > 1 and sys.argv[1] == "console"):
        module = AnsibleModule(argument_spec={"cloud_type": {"type": "str", "required": True, "choices": ['aws', 'gcp', 'azure', 'lsblk']}}, supports_check_mode=True)
    else:
        class cDummyAnsibleModule():  # For testing without Ansible (e.g on Windows)
            def __init__(self):
                self.params = {}

            def exit_json(self, changed, **kwargs):
                print(changed, json.dumps(kwargs, sort_keys=True, indent=4, separators=(',', ': ')))

            def fail_json(self, msg):
                print("Failed: " + msg)
                exit(1)

        module = cDummyAnsibleModule()
        module.params = {"cloud_type": sys.argv[2]}

    if module.params['cloud_type'] == 'aws':
        blockdevmap = cAwsMapper(module=module)
    elif module.params['cloud_type'] == 'gcp':
        blockdevmap = cGCPMapper(module=module)
    elif module.params['cloud_type'] == 'azure':
        blockdevmap = cAzureMapper(module=module)
    elif module.params['cloud_type'] == 'lsblk':
        blockdevmap = cLsblkMapper(module=module)
    else:
        module.fail_json(msg="cloud_type not valid :" + module.params['cloud_type'])

    module.exit_json(changed=False, device_map=blockdevmap.device_map)


if __name__ == '__main__':
    main()
