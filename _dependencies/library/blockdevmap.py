# Copyright 2020 Dougal Seeley <github@dougalseeley.com>
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
    - Map the block device name as defined in AWS/GCP (e.g. /dev/sdf) with the volume provided to the OS
authors:
    - Dougal Seeley <blockdevmap@dougalseeley.com>
    - Amazon.com Inc.
'''

EXAMPLES = '''
- name: Get block device map information for GCP
  blockdevmap:
    cloud_type: gcp
  become: yes
  register: r__blockdevmap

- name: Get block device map information for AWS
  blockdevmap:
    cloud_type: aws
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
'''

from ctypes import *
from fcntl import ioctl
import subprocess
import sys
import json
import re

try:
    from ansible.module_utils.basic import AnsibleModule
    from ansible.errors import AnsibleError
    from ansible.utils.display import Display
except:
    pass

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
                ("vs", nvme_identify_controller_amzn_vs)]  # Vendor Specific


class cBlockDevMap(object):
    def __init__(self, module, **kwds):
        self.module = module
        self.device_map = []

    def get_lsblk(self):
        # Get all existing block volumes by key=value, then parse this into a dictionary (which excludes non disk and partition block types, e.g. ram, loop).
        lsblk_devices = subprocess.check_output(['lsblk', '-o', 'NAME,TYPE,UUID,FSTYPE,MOUNTPOINT,MODEL,SERIAL,SIZE', '-P', '-b']).decode().rstrip().split('\n')
        os_device_names = [dict((map(lambda x: x.strip("\""), sub.split("="))) for sub in dev.split('\" ') if '=' in sub) for dev in lsblk_devices]
        os_device_names = [dev for dev in os_device_names if dev['TYPE'] in ['disk', 'part', 'lvm']]
        os_device_names.sort(key=lambda k: k['NAME'])
        return os_device_names


class cLsblkMapper(cBlockDevMap):
    def __init__(self, **kwds):
        super(cLsblkMapper, self).__init__(**kwds)

        self.device_map = self.get_lsblk()
        for os_device in self.device_map:
            os_device.update({"device_name_os": "/dev/" + os_device['NAME'], "device_name_cloud": ""})


class cGCPMapper(cBlockDevMap):
    def __init__(self, **kwds):
        super(cGCPMapper, self).__init__(**kwds)

        self.device_map = self.get_lsblk()

        for os_device in self.device_map:
            os_device.update({"device_name_os": "/dev/" + os_device['NAME'], "device_name_cloud": os_device['SERIAL']})


class cAwsMapper(cBlockDevMap):
    def __init__(self, **kwds):
        super(cAwsMapper, self).__init__(**kwds)
        # Instance stores (AKA ephemeral volumes) do not appear to have a defined endpoint that maps between the /dev/sd[b-e] defined in the instance creation map, and the OS /dev/nvme[0-26]n1 device.
        # For this scenario, we can only return the instance stores in the order that they are defined.  Because instance stores do not survive a poweroff and cannot be detached and reattached, the order doesn't matter as much.
        instance_store_map = []

        response__block_device_mapping = urlopen('http://169.254.169.254/latest/meta-data/block-device-mapping/')
        block_device_mappings = response__block_device_mapping.read().decode().split("\n")
        for block_device_mappings__ephemeral_id in [dev for dev in block_device_mappings if dev.startswith('ephemeral')]:
            with urlopen("http://169.254.169.254/latest/meta-data/block-device-mapping/" + block_device_mappings__ephemeral_id) as response__ephemeral_device:
                block_device_mappings__ephemeral_mapped = response__ephemeral_device.read().decode()
                instance_store_map.append({'ephemeral_id': block_device_mappings__ephemeral_id, 'ephemeral_map': block_device_mappings__ephemeral_mapped})

        instance_store_count = 0
        self.device_map = self.get_lsblk()
        for os_device in self.device_map:
            os_device_path = "/dev/" + os_device['NAME']
            if os_device['NAME'].startswith("nvme"):
                try:
                    dev = cAwsMapper.ebs_nvme_device(os_device_path)
                except FileNotFoundError as e:
                    self.module.fail_json(msg=os_device_path + ": FileNotFoundError" + str(e))
                except TypeError as e:
                    if instance_store_count < len(instance_store_map):
                        os_device.update({"device_name_os": os_device_path, "device_name_cloud": '/dev/' + instance_store_map[instance_store_count]['ephemeral_map'], "volume_id": dev.get_volume_id()})
                        instance_store_count += 1
                    else:
                        self.module.warn(u"%s is not an EBS device and there is no instance store mapping." % os_device_path)
                except OSError as e:
                    self.module.warn(u"%s is not an nvme device." % os_device_path)
                else:
                    os_device.update({"device_name_os": os_device_path, "device_name_cloud": '/dev/' + dev.get_block_device(stripped=True).rstrip(), "volume_id": dev.get_volume_id()})
            elif os_device['NAME'].startswith("xvd"):
                os_device.update({"device_name_os": os_device_path, "device_name_cloud": '/dev/' + re.sub(r'xvd(.*)', r'sd\1', os_device['NAME'])})
            else:
                os_device.update({"device_name_os": os_device_path, "device_name_cloud": ""})

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
        module = AnsibleModule(argument_spec={"cloud_type": {"type": "str", "required": True, "choices": ['aws', 'gcp', 'lsblk']}}, supports_check_mode=True)
    else:
        # For testing without Ansible (e.g on Windows)
        class cDummyAnsibleModule():
            params = {"cloud_type": "aws"}

            def exit_json(self, changed, **kwargs):
                print(changed, json.dumps(kwargs, sort_keys=True, indent=4, separators=(',', ': ')))

            def warn(self, msg):
                print("[WARNING]: " + msg)

            def fail_json(self, msg):
                print("Failed: " + msg)
                exit(1)

        module = cDummyAnsibleModule()

    if module.params['cloud_type'] == 'aws':
        blockdevmap = cAwsMapper(module=module)
    elif module.params['cloud_type'] == 'gcp':
        blockdevmap = cGCPMapper(module=module)
    elif module.params['cloud_type'] == 'lsblk':
        blockdevmap = cLsblkMapper(module=module)
    else:
        module.fail_json(msg="cloud_type not valid :" + module.params['cloud_type'])

    module.exit_json(changed=False, device_map=blockdevmap.device_map)


if __name__ == '__main__':
    main()
