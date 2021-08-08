#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Dougal Seeley
# https://github.com/dseeley/esxifree_guest
# BSD 3-Clause License

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: esxifree_guest
short_description: Manages virtual machines in ESXi without a dependency on the vSphere/ vCenter API.
description: >
   This module can be used to create new virtual machines from scratch or from templates or other virtual machines (i.e. clone them),
   delete, or manage the power state of virtual machine such as power on, power off, suspend, shutdown, reboot, restart etc.,
version_added: '2.7'
author:
- Dougal Seeley (ansible@dougalseeley.com)
requirements:
- python >= 2.7
- paramiko
- xmltodict
notes:
    - Please make sure that the user used for esxifree_guest should have correct level of privileges.
    - Tested on vSphere 7.0.2
options:
  hostname:
    description:
    - The hostname or IP address of the ESXi server.
    required: true
    type: str
  username:
    description:
    - The username to access the ESXi server at C(hostname).
    required: true
    type: str
  password:
    description:
    - The password of C(username) for the ESXi server, or the password for the private key (if required).
    required: true
    type: str
  state:
    description:
    - Specify the state the virtual machine should be in.
    - 'If C(state) is set to C(present) and virtual machine exists, ensure the virtual machine
       configurations conforms to task arguments.'
    - 'If C(state) is set to C(absent) and virtual machine exists, then the specified virtual machine
      is removed with its associated components.'
    - 'If C(state) is set to one of the following C(poweredon), C(poweredoff), C(present)
      and virtual machine does not exists, then virtual machine is deployed with given parameters.'
    - 'If C(state) is set to C(poweredon) and virtual machine exists with powerstate other than powered on,
      then the specified virtual machine is powered on.'
    - 'If C(state) is set to C(poweredoff) and virtual machine exists with powerstate other than powered off,
      then the specified virtual machine is powered off.'
    - 'If C(state) is set to C(shutdownguest) and virtual machine exists, then the virtual machine is shutdown.'
    - 'If C(state) is set to C(rebootguest) and virtual machine exists, then the virtual machine is rebooted.'
    - 'If C(state) is set to C(unchanged) the state of the VM will not change (if it's on/off, it will stay so).  Used for updating annotations.'
    choices: [ present, absent, poweredon, poweredoff, shutdownguest, rebootguest, unchanged ]
    default: present
  name:
    description:
    - Name of the virtual machine to work with.
    - Virtual machine names in ESXi are unique
    - This parameter is required, if C(state) is set to C(present) and virtual machine does not exists.
    - This parameter is case sensitive.
    type: str
  moid:
    description:
    - Managed Object ID of the virtual machine to manage
    - This is required if C(name) is not supplied.
    - If virtual machine does not exists, then this parameter is ignored.
    - Will be ignored on virtual machine creation
    type: str
  template:
    description:
    - Template or existing virtual machine used to create new virtual machine.
    - If this value is not set, virtual machine is created without using a template.
    - If the virtual machine already exists, this parameter will be ignored.
    - This parameter is case sensitive.
    type: str
  hardware:
    description:
    - Manage virtual machine's hardware attributes.
    type: dict
    suboptions:
      version:
        description:
        - The Virtual machine hardware version. Default is 15 (ESXi 6.7U2 and onwards).
        type: int
        default: 15
        required: false
      num_cpus:
        description:
        - Number of CPUs.
        - C(num_cpus) must be a multiple of C(num_cpu_cores_per_socket).
        type: int
        default: 2
        required: false
      num_cpu_cores_per_socket:
        description:
        - Number of Cores Per Socket.
        type: int
        default: 1
        required: false
      hotadd_cpu:
        description: 
        - Allow virtual CPUs to be added while the virtual machine is running.
        type: bool
        required: false
      memory_mb:
        description: 
        - Amount of memory in MB.
        type: int
        default: 2048
        required: false
      memory_reservation_lock:
        description:
        - If set true, memory resource reservation for the virtual machine
          will always be equal to the virtual machine's memory size.
        type: bool
        required: false
      hotadd_memory:
        description: 
        - Allow memory to be added while the virtual machine is running.
        type: bool
        required: false
  guest_id:
    description:
    - Set the guest ID.
    - This parameter is case sensitive.
    - 'Examples:'
    - "  virtual machine with RHEL7 64 bit, will be 'rhel7-64'"
    - "  virtual machine with CentOS 7 (64-bit), will be 'centos7-64'"
    - "  virtual machine with Debian 9 (Stretch) 64 bit, will be 'debian9-64'"
    - "  virtual machine with Ubuntu 64 bit, will be 'ubuntu-64'"
    - "  virtual machine with Windows 10 (64 bit), will be 'windows9-64'"
    - "  virtual machine with Other (64 bit), will be 'other-64'"
    - This field is required when creating a virtual machine, not required when creating from the template.
    type: str
    default: ubuntu-64
  disks:
    description:
    - A list of disks to add (or create via cloning).
    - Resizing disks is not supported.
    - Removing existing disks of the virtual machine is not supported.
    required: false
    type: list
    suboptions:
      boot:
        description:
        - Indicates that this is a boot disk. 
        required: false
        default: no
        type: bool
      size_gb:
        description:  Specifies the size of the disk in base-2 GB.
        type: int
        required: true
      type:
        description:
        - Type of disk provisioning
        choices: [thin, thick, eagerzeroedthick]
        type: str
        required: false
        default: thin
      volname:
        description:
        - Volume name.  This will be a suffix of the vmdk file, e.g. "testdisk" on a VM named "mynewvm", would yield mynewvm--testdisk.vmdk
        type: str
        required: true
      src:
        description:
        - The source disk from which to create this disk.
        required: false
        type: dict
        suboptions:
          backing_filename:
            description:
            - The source file, e.g. "[datastore1] linux_dev/linux_dev--webdata.vmdk"
            type: str
          copy_or_move
            description:
            - Whether to copy (clone) from the source datastore, or move the file.  Move will fail if source and destination datastore differ.  
            choices: [copy, move]

  cdrom:
    description:
    - A CD-ROM configuration for the virtual machine.
    - 'Valid attributes are:'
    - ' - C(type) (string): The type of CD-ROM, valid options are C(none), C(client) or C(iso). With C(none) the CD-ROM will be disconnected but present.'
    - ' - C(iso_path) (string): The datastore path to the ISO file to use, in the form of C([datastore1] path/to/file.iso). Required if type is set C(iso).'
  wait:
    description:
    - On creation, wait for the instance to obtain its IP address before returning.
    type: bool
    required: false
    default: true
  wait_timeout:
    description:
    - How long before wait gives up, in seconds.
    type: int
    required: false
    default: 180
  delete_cloudinit:
    description:
    - Delete the cloud-init config after creation.  If you do this, you will need to remove cloud-init from the system, or it will overwrite with defaults on next boot.
    type: bool
    required: false
    default: false
  force:
    description:
    - Delete the existing host if it exists.  Use with extreme care!
    type: bool
    required: false
    default: false
  customvalues:
    description:
    - Define a list of custom values to set on virtual machine.
    - A custom value object takes two fields C(key) and C(value).
    - Incorrect key and values will be ignored.
    version_added: '2.3'
  cloudinit_userdata:
    description:
    - A list of userdata (per user) as defined U(https://cloudinit.readthedocs.io/en/latest/topics/examples.html).  The 
      VM must already have cloud-init-vmware-guestinfo installed U(https://github.com/vmware/cloud-init-vmware-guestinfo)
  networks:
    description:
    - A list of networks (in the order of the NICs).
    - Removing NICs is not allowed, while reconfiguring the virtual machine.
    - All parameters and VMware object names are case sensetive.
    - 'One of the below parameters is required per entry:'
    - ' - C(networkName) (string): Name of the portgroup for this interface.
    - ' - C(virtualDev) (string): Virtual network device (one of C(e1000e), C(vmxnet3) (default), C(sriov)).'
    - 'Optional parameters per entry (used for OS customization):'
    - ' - C(cloudinit_ethernets) (dict): A list of C(ethernets) within the definition of C(Networking Config Version 2)
          defined in U(https://cloudinit.readthedocs.io/en/latest/topics/network-config-format-v2.html)'.  The 
          VM must already have cloud-init-vmware-guestinfo installed U(https://github.com/vmware/cloud-init-vmware-guestinfo)
  datastore:
    description:
    - Specify datastore or datastore cluster to provision virtual machine.
    type: str
    required: true

'''
EXAMPLES = r'''
- name: Create a virtual machine
  esxifree_guest:
    hostname: "192.168.1.3"
    username: "svc"
    password: "my_passsword"
    datastore: "datastore1"
    name: "test_asdf"
    state: present
    guest_id: ubuntu-64
    hardware: {"version": "15", "num_cpus": "2", "memory_mb": "2048"}
    cloudinit_userdata:
      - name: dougal
        primary_group: dougal
        sudo: "ALL=(ALL) NOPASSWD:ALL"
        groups: "admin"
        home: "/media/filestore/home/dougal"
        ssh_import_id: None
        lock_passwd: false
        passwd: $6$j212wezy$7...YPYb2F
        ssh_authorized_keys: ['ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACA+.................GIMhdojtl6mzVn38vXMzSL29LQ== ansible@dougalseeley.com']
    disks:
     - {"boot": true, "size_gb": 16, "type": "thin"}
     - {"size_gb": 2, "type": "thin", "volname": "test_new"}
     - {"size_gb": 1, "type": "thin", "volname": "test_clone", "src": {"backing_filename": "[datastore1] linux_dev/linux_dev--webdata.vmdk", "copy_or_move": "copy"}}],
    cdrom: {"type": "iso", "iso_path": "/vmfs/volumes/4tb-evo860-ssd/ISOs/ubuntu-18.04.4-server-amd64.iso"},
    networks:
      - networkName: VM Network
        virtualDev: vmxnet3
        cloudinit_ethernets:
          eth0:
            addresses: ["192.168.1.8/25"]
            dhcp4: false
            gateway4: 192.168.1.1
            nameservers:
              addresses: ["192.168.1.2", "8.8.8.8", "8.8.4.4"]
              search: ["local.dougalseeley.com"]
  delegate_to: localhost

- name: Clone a virtual machine
  esxifree_guest:
    hostname: "192.168.1.3"
    username: "svc"
    password: "my_passsword"
    datastore: "datastore1"
    template: "ubuntu1804-packer-template"
    name: "test_asdf"
    state: present
    guest_id: ubuntu-64
    hardware: {"version": "15", "num_cpus": "2", "memory_mb": "2048"}
    cloudinit_userdata:
      - default
      - name: dougal
        primary_group: dougal
        sudo: "ALL=(ALL) NOPASSWD:ALL"
        groups: "admin"
        home: "/media/filestore/home/dougal"
        ssh_import_id: None
        lock_passwd: true
        ssh_authorized_keys: ['ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACA+.................GIMhdojtl6mzVn38vXMzSL29LQ== ansible@dougalseeley.com']
    disks:
     - {"size_gb": 2, "type": "thin", "volname": "test_new"}
     - {"size_gb": 1, "type": "thin", "volname": "test_clone", "src": {"backing_filename": "[datastore1] linux_dev/linux_dev--webdata.vmdk", "copy_or_move": "copy"}}],
    networks:
      - networkName: VM Network
        virtualDev: vmxnet3
        cloudinit_ethernets:
          eth0:
            addresses: ["192.168.1.8/25"]
            dhcp4: false
            gateway4: 192.168.1.1
            nameservers:
              addresses: ["192.168.1.2", "8.8.8.8", "8.8.4.4"]
              search: ["local.dougalseeley.com"]
  delegate_to: localhost

- name: Delete a virtual machine
  esxifree_guest:
    hostname: "{{ esxi_ip }}"
    username: "{{ username }}"
    password: "{{ password }}"
    name: test_vm_0001
    state: absent
  delegate_to: localhost
'''

RETURN = r'''
instance:
    description: metadata about the new virtual machine
    returned: always
    type: dict
    sample: None
'''

import os
import time
import re
import json
import socket
import collections
import paramiko
import sys
import base64
import yaml
import errno  # For the python2.7 IOError, because FileNotFound is for python3
import xmltodict

# define a custom yaml representer to force quoted strings
yaml.add_representer(str, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"'))

# For the soap client
try:
    from urllib.request import Request, build_opener, HTTPSHandler, HTTPCookieProcessor
    from urllib.response import addinfourl
    from urllib.error import HTTPError
    from http.cookiejar import CookieJar
    from http.client import HTTPResponse
except ImportError:
    from urllib2 import Request, build_opener, HTTPError, HTTPSHandler, HTTPCookieProcessor, addinfourl
    from cookielib import CookieJar
    from httplib import HTTPResponse
import ssl

if sys.version_info[0] < 3:
    from io import BytesIO as StringIO
else:
    from io import StringIO

# paramiko.util.log_to_file("paramiko.log")
# paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)

try:
    from ansible.module_utils.basic import AnsibleModule
except:
    # For testing without Ansible (e.g on Windows)
    class cDummyAnsibleModule():
        def __init__(self):
            self.params={}
        def exit_json(self, changed, **kwargs):
            print(changed, json.dumps(kwargs, sort_keys=True, indent=4, separators=(',', ': ')))
        def fail_json(self, msg):
            print("Failed: " + msg)
            exit(1)

# Executes soap requests on the remote host.
class vmw_soap_client(object):
    def __init__(self, host, username, password):
        self.vmware_soap_session_cookie = None
        self.host = host
        response, cookies = self.send_req("<RetrieveServiceContent><_this>ServiceInstance</_this></RetrieveServiceContent>")
        xmltodictresponse = xmltodict.parse(response.read())
        sessionManager_name = xmltodictresponse['soapenv:Envelope']['soapenv:Body']['RetrieveServiceContentResponse']['returnval']['sessionManager']['#text']

        response, cookies = self.send_req("<Login><_this>" + sessionManager_name + "</_this><userName>" + username + "</userName><password>" + password + "</password></Login>")
        self.vmware_soap_session_cookie = cookies['vmware_soap_session'].value

    def send_req(self, envelope_body=None):
        envelope = '<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' + '<Body>' + str(envelope_body) + '</Body></Envelope>'
        cj = CookieJar()
        req = Request(
                url='https://' + self.host + '/sdk/vimService.wsdl', data=envelope.encode(),
                headers={"Content-Type": "text/xml", "SOAPAction": "urn:vim25/6.7.3", "Accept": "*/*", "Cookie": "vmware_client=VMware; vmware_soap_session=" + str(self.vmware_soap_session_cookie)})

        opener = build_opener(HTTPSHandler(context=ssl._create_unverified_context()), HTTPCookieProcessor(cj))
        num_send_attempts = 3
        for send_attempt in range(num_send_attempts):
            try:
                response = opener.open(req, timeout=30)
            except HTTPError as err:
                response = str(err)
            except:
                if send_attempt < num_send_attempts - 1:
                    time.sleep(1)
                    continue
                else:
                    raise
            break

        cookies = {i.name: i for i in list(cj)}
        return (response[0] if isinstance(response, list) else response, cookies)  # If the cookiejar contained anything, we get a list of two responses

    def wait_for_task(self, task, timeout=30):
        time_s = int(timeout)
        while time_s > 0:
            response, cookies = self.send_req('<RetrieveProperties><_this type="PropertyCollector">ha-property-collector</_this><specSet><propSet><type>Task</type><all>false</all><pathSet>info</pathSet></propSet><objectSet><obj type="Task">' + task + '</obj><skip>false</skip></objectSet></specSet></RetrieveProperties>')
            if isinstance(response, HTTPResponse) or isinstance(response, addinfourl):
                xmltodictresponse = xmltodict.parse(response.read())
                if xmltodictresponse['soapenv:Envelope']['soapenv:Body']['RetrievePropertiesResponse']['returnval']['propSet']['val'] == 'running':
                    time.sleep(1)
                    time_s = time_s - 1
                elif xmltodictresponse['soapenv:Envelope']['soapenv:Body']['RetrievePropertiesResponse']['returnval']['propSet']['val']['state'] == 'success':
                    response = xmltodictresponse['soapenv:Envelope']['soapenv:Body']['RetrievePropertiesResponse']['returnval']['propSet']['val']['state']
                    break
                elif xmltodictresponse['soapenv:Envelope']['soapenv:Body']['RetrievePropertiesResponse']['returnval']['propSet']['val']['state'] == 'error':
                    response = str(xmltodictresponse)
                    break
            else:
                break
        return response


# Executes a command on the remote host.
class SSHCmdExec(object):
    def __init__(self, hostname, username=None, password=None, pkeyfile=None, pkeystr=None):
        self.hostname = hostname

        try:
            if pkeystr and pkeystr != "":
                pkey_fromstr = paramiko.RSAKey.from_private_key(StringIO(pkeystr), password)
            if pkeyfile and pkeyfile != "":
                pkey_fromfile = paramiko.RSAKey.from_private_key_file(pkeyfile, password)
        except paramiko.ssh_exception.PasswordRequiredException as auth_err:
            print("Authentication failure, Password required" + "\n\n" + str(auth_err))
            exit(1)
        except paramiko.ssh_exception.SSHException as auth_err:
            print("Authentication failure, SSHException" + "\n\n" + str(auth_err))
            exit(1)
        except:
            print("Unexpected error: ", sys.exc_info()[0])
            raise
        else:
            if pkeystr:
                self.pkey = pkey_fromstr
                if pkeyfile:
                    if pkey_fromstr != pkey_fromfile:
                        print("Both private key file and private key string specified and not equal!")
                        exit(1)
            elif pkeyfile:
                self.pkey = pkey_fromfile

        # Create instance of SSHClient object
        self.remote_conn_client = paramiko.SSHClient()
        self.remote_conn_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # initiate SSH connection
        try:
            if hasattr(self, 'pkey'):
                self.remote_conn_client.connect(hostname=hostname, username=username, pkey=self.pkey, timeout=10, look_for_keys=False, allow_agent=False)
            else:
                self.remote_conn_client.connect(hostname=hostname, username=username, password=password, timeout=10, look_for_keys=False, allow_agent=False)
        except socket.error as sock_err:
            print("Connection timed-out to " + hostname)  # + "\n\n" + str(sock_err)
            exit(1)
        except paramiko.ssh_exception.AuthenticationException as auth_err:
            print("Authentication failure, unable to connect to " + hostname + " as " + username + "\n\n" + str(auth_err) + "\n\n" + str(sys.exc_info()[0]))  # + str(auth_err))
            exit(1)
        except:
            print("Unexpected error: ", sys.exc_info()[0])
            raise

        # print("SSH connection established to " + hostname + " as " + username)

    def __del__(self):
        if self.remote_conn_client:
            self.remote_conn_client.close()

    def get_sftpClient(self):
        return self.remote_conn_client.open_sftp()

    # execute the command and wait for it to finish
    def exec_command(self, command_string):
        # print("Command is: {0}".format(command_string))

        (stdin, stdout, stderr) = self.remote_conn_client.exec_command(command_string)
        if stdout.channel.recv_exit_status() != 0:  # Blocking call
            raise IOError(stderr.read())

        return stdin, stdout, stderr


class esxiFreeScraper(object):
    vmx_skeleton = collections.OrderedDict()
    vmx_skeleton['.encoding'] = "UTF-8"
    vmx_skeleton['config.version'] = "8"
    vmx_skeleton['pciBridge0.present'] = "TRUE"
    vmx_skeleton['svga.present'] = "TRUE"
    vmx_skeleton['svga.autodetect'] = "TRUE"
    vmx_skeleton['pciBridge4.present'] = "TRUE"
    vmx_skeleton['pciBridge4.virtualDev'] = "pcieRootPort"
    vmx_skeleton['pciBridge4.functions'] = "8"
    vmx_skeleton['pciBridge5.present'] = "TRUE"
    vmx_skeleton['pciBridge5.virtualDev'] = "pcieRootPort"
    vmx_skeleton['pciBridge5.functions'] = "8"
    vmx_skeleton['pciBridge6.present'] = "TRUE"
    vmx_skeleton['pciBridge6.virtualDev'] = "pcieRootPort"
    vmx_skeleton['pciBridge6.functions'] = "8"
    vmx_skeleton['pciBridge7.present'] = "TRUE"
    vmx_skeleton['pciBridge7.virtualDev'] = "pcieRootPort"
    vmx_skeleton['pciBridge7.functions'] = "8"
    vmx_skeleton['vmci0.present'] = "TRUE"
    vmx_skeleton['hpet0.present'] = "TRUE"
    vmx_skeleton['floppy0.present'] = "FALSE"
    vmx_skeleton['usb.present'] = "TRUE"
    vmx_skeleton['ehci.present'] = "TRUE"
    vmx_skeleton['tools.syncTime'] = "TRUE"
    vmx_skeleton['scsi0.virtualDev'] = "pvscsi"
    vmx_skeleton['scsi0.present'] = "TRUE"
    vmx_skeleton['disk.enableuuid'] = "TRUE"

    def __init__(self, hostname, username='root', password=None, name=None, moid=None):
        self.soap_client = vmw_soap_client(host=hostname, username=username, password=password)
        self.esxiCnx = SSHCmdExec(hostname=hostname, username=username, password=password)
        self.name, self.moid = self.get_vm(name, moid)
        if self.moid is None:
            self.name = name

    def get_vm(self, name=None, moid=None):
        response, cookies = self.soap_client.send_req('<RetrievePropertiesEx><_this type="PropertyCollector">ha-property-collector</_this><specSet><propSet><type>VirtualMachine</type><all>false</all><pathSet>name</pathSet></propSet><objectSet><obj type="Folder">ha-folder-vm</obj><selectSet xsi:type="TraversalSpec"><name>traverseChild</name><type>Folder</type><path>childEntity</path> <selectSet><name>traverseChild</name></selectSet><selectSet xsi:type="TraversalSpec"><type>Datacenter</type><path>vmFolder</path><selectSet><name>traverseChild</name></selectSet> </selectSet> </selectSet> </objectSet></specSet><options type="RetrieveOptions"></options></RetrievePropertiesEx>')
        xmltodictresponse = xmltodict.parse(response.read())
        allVms = [{'moid': a['obj']['#text'], 'name': a['propSet']['val']['#text']} for a in xmltodictresponse['soapenv:Envelope']['soapenv:Body']['RetrievePropertiesExResponse']['returnval']['objects']]
        for vm in allVms:
            if ((name and name == vm['name']) or (moid and moid == vm['moid'])):
                return vm['name'], vm['moid']
        return None, None

    def get_vmx(self, moid):
        (stdin, stdout, stderr) = self.esxiCnx.exec_command("vim-cmd vmsvc/get.filelayout " + str(moid) + " | grep 'vmPathName = ' | sed -r 's/^\s+vmPathName = \"(.*?)\",/\\1/g'")
        vmxPathName = stdout.read().decode('UTF-8').lstrip("\r\n").rstrip(" \r\n")
        vmxPath = re.sub(r"^\[(.*?)]\s+(.*?)$", r"/vmfs/volumes/\1/\2", vmxPathName)

        if vmxPath:
            sftp_cnx = self.esxiCnx.get_sftpClient()
            vmxFileDict = {}
            for vmxline in sftp_cnx.file(vmxPath).readlines():
                vmxline_params = re.search('^(?P<key>.*?)\s*=\s*(?P<value>.*)$', vmxline)
                if vmxline_params and vmxline_params.group('key') and vmxline_params.group('value'):
                    vmxFileDict[vmxline_params.group('key').strip(" \"\r\n").lower()] = vmxline_params.group('value').strip(" \"\r\n")

            return vmxPath, vmxFileDict

    def put_vmx(self, vmxDict, vmxPath):
        # print(json.dumps(vmxDict, sort_keys=True, indent=4, separators=(',', ': ')))
        vmxDict = collections.OrderedDict(sorted(vmxDict.items()))
        vmxStr = StringIO()
        for vmxKey, vmxVal in vmxDict.items():
            vmxStr.write(str(vmxKey.lower()) + " = " + "\"" + str(vmxVal) + "\"\n")
        vmxStr.seek(0)
        sftp_cnx = self.esxiCnx.get_sftpClient()
        try:
            sftp_cnx.stat(vmxPath)
            sftp_cnx.remove(vmxPath)
        except IOError as e:  # python 2.7
            if e.errno == errno.ENOENT:
                pass
        except FileNotFoundError:  # python 3.x
            pass
        sftp_cnx.putfo(vmxStr, vmxPath, file_size=0, callback=None, confirm=True)

    def create_vm(self, vmTemplate=None, annotation=None, datastore=None, hardware=None, guest_id=None, disks=None, cdrom=None, customvalues=None, networks=None, cloudinit_userdata=None):
        vmPathDest = "/vmfs/volumes/" + datastore + "/" + self.name

        ## Sanity checks
        for dryRunDisk in [newDisk for newDisk in disks if ('src' in newDisk and newDisk['src'] is not None)]:
            if 'copy_or_move' not in dryRunDisk['src']:
                return ("'copy_or_move' parameter is mandatory when src is specified for a disk.")
            if 'backing_filename' not in dryRunDisk['src']:
                return ("'backing_filename' parameter is mandatory when src is specified for a disk.")

            dryRunDiskFileInfo = re.search('^\[(?P<datastore>.*?)\] *(?P<fulldiskpath>.*\/(?P<filepath>(?P<fileroot>.*?)(?:--(?P<diskname_suffix>.*?))?\.vmdk))$', dryRunDisk['src']['backing_filename'])
            try:
                self.esxiCnx.exec_command("vmkfstools -g /vmfs/volumes/" + dryRunDiskFileInfo.group('datastore') + "/" + dryRunDiskFileInfo.group('fulldiskpath'))
            except IOError as e:
                return "'" + dryRunDisk['src']['backing_filename'] + "' is not accessible (is the VM turned on?)\n" + str(e)

        # Create VM directory
        self.esxiCnx.exec_command("mkdir -p " + vmPathDest)

        vmxDict = collections.OrderedDict(esxiFreeScraper.vmx_skeleton)

        diskCount = 0

        # First apply any vmx settings from the template.
        # These will be overridden by explicit configuration.
        if vmTemplate:
            template_name, template_moid = self.get_vm(vmTemplate, None)
            if template_moid:
                template_vmxPath, template_vmxDict = self.get_vmx(template_moid)

                # Generic settings
                vmxDict.update({"guestos": template_vmxDict['guestos']})

                # Hardware settings
                vmxDict.update({"virtualhw.version": template_vmxDict['virtualhw.version']})
                vmxDict.update({"memsize": template_vmxDict['memsize']})
                if 'numvcpus' in template_vmxDict:
                    vmxDict.update({"numvcpus": template_vmxDict['numvcpus']})
                if 'cpuid.coresPerSocket' in template_vmxDict:
                    vmxDict.update({"cpuid.coresPerSocket": template_vmxDict['cpuid.coresPerSocket']})
                if 'vcpu.hotadd' in template_vmxDict:
                    vmxDict.update({"vcpu.hotadd": template_vmxDict['vcpu.hotadd']})
                if 'mem.hotadd' in template_vmxDict:
                    vmxDict.update({"mem.hotadd": template_vmxDict['mem.hotadd']})
                if 'sched.mem.pin' in template_vmxDict:
                    vmxDict.update({"sched.mem.pin": template_vmxDict['sched.mem.pin']})

                # Network settings
                netCount = 0
                while "ethernet" + str(netCount) + ".virtualdev" in template_vmxDict:
                    vmxDict.update({"ethernet" + str(netCount) + ".virtualdev": template_vmxDict["ethernet" + str(netCount) + ".virtualdev"]})
                    vmxDict.update({"ethernet" + str(netCount) + ".networkname": template_vmxDict["ethernet" + str(netCount) + ".networkname"]})
                    vmxDict.update({"ethernet" + str(netCount) + ".addresstype": "generated"})
                    vmxDict.update({"ethernet" + str(netCount) + ".present": "TRUE"})
                    netCount = netCount + 1

                ### Disk cloning - clone all disks from source
                response, cookies = self.soap_client.send_req('<RetrievePropertiesEx><_this type="PropertyCollector">ha-property-collector</_this><specSet><propSet><type>VirtualMachine</type><all>false</all><pathSet>layout</pathSet></propSet><objectSet><obj type="VirtualMachine">' + str(template_moid) + '</obj><skip>false</skip></objectSet></specSet><options/></RetrievePropertiesEx>')
                xmltodictresponse = xmltodict.parse(response.read(), force_list='disk')
                srcDiskFiles = [disk.get('diskFile') for disk in xmltodictresponse['soapenv:Envelope']['soapenv:Body']['RetrievePropertiesExResponse']['returnval']['objects']['propSet']['val']['disk']]
                for srcDiskFile in srcDiskFiles:
                    srcDiskFileInfo = re.search('^\[(?P<datastore>.*?)\] *(?P<fulldiskpath>.*\/(?P<filepath>(?P<fileroot>.*?)(?:--(?P<diskname_suffix>.*?))?\.vmdk))$', srcDiskFile)
                    diskTypeKey = next((key for key, val in template_vmxDict.items() if val == srcDiskFileInfo.group('filepath')), None)

                    if re.search('scsi', diskTypeKey):
                        controllerTypeStr = "scsi0:"
                    else:
                        controllerTypeStr = "sata0:"

                    # See if vmTemplate disk exists
                    try:
                        (stdin, stdout, stderr) = self.esxiCnx.exec_command("stat /vmfs/volumes/" + srcDiskFileInfo.group('datastore') + "/" + srcDiskFileInfo.group('fulldiskpath'))
                    except IOError as e:
                        return (srcDiskFileInfo.group('fulldiskpath') + " not found!")
                    else:
                        if diskCount == 0:
                            disk_filename = self.name + "--boot.vmdk"
                        else:
                            if 'diskname_suffix' in srcDiskFileInfo.groupdict() and srcDiskFileInfo.group('diskname_suffix'):
                                disk_filename = self.name + "--" + srcDiskFileInfo.group('diskname_suffix') + ".vmdk"
                            else:
                                disk_filename = self.name + ".vmdk"
                        self.esxiCnx.exec_command("vmkfstools -i /vmfs/volumes/" + srcDiskFileInfo.group('datastore') + "/" + srcDiskFileInfo.group('fulldiskpath') + " -d thin " + vmPathDest + "/" + disk_filename)

                        vmxDict.update({controllerTypeStr + str(diskCount) + ".devicetype": "scsi-hardDisk"})
                        vmxDict.update({controllerTypeStr + str(diskCount) + ".present": "TRUE"})
                        vmxDict.update({controllerTypeStr + str(diskCount) + ".filename": disk_filename})
                        diskCount = diskCount + 1

            else:
                return (vmTemplate + " not found!")

        ## Now add remaining settings, overriding template copies.

        # Generic settings
        if guest_id:
            vmxDict.update({"guestos": guest_id})
        vmxDict.update({"displayname": self.name})
        vmxDict.update({"vm.createdate": time.time()})

        if annotation:
            vmxDict.update({"annotation": annotation})

        # Hardware settings
        if 'version' in hardware:
            vmxDict.update({"virtualhw.version": hardware['version']})
        if 'memory_mb' in hardware:
            vmxDict.update({"memsize": hardware['memory_mb']})
        if 'num_cpus' in hardware:
            vmxDict.update({"numvcpus": hardware['num_cpus']})
        if 'num_cpu_cores_per_socket' in hardware:
            vmxDict.update({"cpuid.coresPerSocket": hardware['num_cpu_cores_per_socket']})
        if 'hotadd_cpu' in hardware:
            vmxDict.update({"vcpu.hotadd": hardware['hotadd_cpu']})
        if 'hotadd_memory' in hardware:
            vmxDict.update({"mem.hotadd": hardware['hotadd_memory']})
        if 'memory_reservation_lock' in hardware:
            vmxDict.update({"sched.mem.pin": hardware['memory_reservation_lock']})

        # CDROM settings
        if cdrom['type'] == 'client':
            (stdin, stdout, stderr) = self.esxiCnx.exec_command("find /vmfs/devices/cdrom/ -mindepth 1 ! -type l")
            cdrom_dev = stdout.read().decode('UTF-8').lstrip("\r\n").rstrip(" \r\n")
            vmxDict.update({"ide0:0.devicetype": "atapi-cdrom"})
            vmxDict.update({"ide0:0.filename": cdrom_dev})
            vmxDict.update({"ide0:0.present": "TRUE"})
        elif cdrom['type'] == 'iso':
            if 'iso_path' in cdrom:
                vmxDict.update({"ide0:0.devicetype": "cdrom-image"})
                vmxDict.update({"ide0:0.filename": cdrom['iso_path']})
                vmxDict.update({"ide0:0.present": "TRUE"})
                vmxDict.update({"ide0:0.startconnected": "TRUE"})

        # Network settings
        cloudinit_nets = {"version": 2}
        for netCount in range(0, len(networks)):
            vmxDict.update({"ethernet" + str(netCount) + ".virtualdev": networks[netCount]['virtualDev']})
            vmxDict.update({"ethernet" + str(netCount) + ".networkname": networks[netCount]['networkName']})
            if "macAddress" in networks[netCount]:
                vmxDict.update({"ethernet" + str(netCount) + ".addresstype": "static"})
                vmxDict.update({"ethernet" + str(netCount) + ".address": networks[netCount]['macAddress']})
                vmxDict.update({"ethernet" + str(netCount) + ".checkmacaddress": "FALSE"})
            else:
                vmxDict.update({"ethernet" + str(netCount) + ".addresstype": "generated"})
            vmxDict.update({"ethernet" + str(netCount) + ".present": "TRUE"})
            if "cloudinit_netplan" in networks[netCount]:
                cloudinit_nets.update(networks[netCount]['cloudinit_netplan'])

        # Add cloud-init metadata (hostname & network)
        cloudinit_metadata = {"local-hostname": self.name}
        if 'ethernets' in cloudinit_nets and cloudinit_nets['ethernets'].keys():
            # Force guest to use the MAC address as the DHCP identifier, in case the machine-id is not reset for each clone
            for cloudeth in cloudinit_nets['ethernets'].keys():
                cloudinit_nets['ethernets'][cloudeth].update({"dhcp-identifier": "mac"})
            # Add the metadata
            cloudinit_metadata.update({"network": base64.b64encode(yaml.dump(cloudinit_nets, width=4096, encoding='utf-8')).decode('ascii'), "network.encoding": "base64"})
        vmxDict.update({"guestinfo.metadata": base64.b64encode(yaml.dump(cloudinit_metadata, width=4096, encoding='utf-8')).decode('ascii'), "guestinfo.metadata.encoding": "base64"})

        # Add cloud-init userdata (must be in MIME multipart format)
        if cloudinit_userdata and len(cloudinit_userdata):
            import sys
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            combined_message = MIMEMultipart()
            sub_message = MIMEText(yaml.dump({"users": cloudinit_userdata}, width=4096, encoding='utf-8'), "cloud-config", sys.getdefaultencoding())
            sub_message.add_header('Content-Disposition', 'attachment; filename="cloud-config.yaml"')
            combined_message.attach(sub_message)
            if sys.version_info >= (3, 0):
                vmxDict.update({"guestinfo.userdata": base64.b64encode(combined_message.as_bytes()).decode('ascii'), "guestinfo.userdata.encoding": "base64"})
            else:
                vmxDict.update({"guestinfo.userdata": base64.b64encode(combined_message.as_string()).decode('ascii'), "guestinfo.userdata.encoding": "base64"})

        ### Disk create
        # If the first disk doesn't exist, create it
        bootDisks = [bootDisk for bootDisk in disks if 'boot' in bootDisk]
        if len(bootDisks) > 1:
            return ("Muiltiple boot disks not allowed")

        if "scsi0:0.filename" not in vmxDict:
            if len(bootDisks) == 1:
                disk_filename = self.name + "--boot.vmdk"
                (stdin, stdout, stderr) = self.esxiCnx.exec_command("vmkfstools -c " + str(bootDisks[0]['size_gb']) + "G -d " + bootDisks[0]['type'] + " " + vmPathDest + "/" + disk_filename)

                vmxDict.update({"scsi0:0.devicetype": "scsi-hardDisk"})
                vmxDict.update({"scsi0:0.present": "TRUE"})
                vmxDict.update({"scsi0:0.filename": disk_filename})
                diskCount = diskCount + 1
            if len(bootDisks) == 0:
                return ("Boot disk parameters not defined for new VM")
        else:
            if len(bootDisks) == 1:
                return ("Boot disk parameters defined for cloned VM.  Ambiguous requirement - not supported.")

        # write the vmx
        self.put_vmx(vmxDict, vmPathDest + "/" + self.name + ".vmx")

        # Register the VM
        (stdin, stdout, stderr) = self.esxiCnx.exec_command("vim-cmd solo/registervm " + vmPathDest + "/" + self.name + ".vmx")
        self.moid = int(stdout.readlines()[0])

        # The logic used to update the disks is the same for an existing as a new VM.
        self.update_vm(annotation=None, disks=disks)

    def update_vm(self, annotation, disks):
        vmxPath, vmxDict = self.get_vmx(self.moid)
        if annotation:
            # Update the config (annotation) in the running VM
            response, cookies = self.soap_client.send_req('<ReconfigVM_Task><_this type="VirtualMachine">' + str(self.moid) + '</_this><spec><annotation>' + annotation + '</annotation></spec></ReconfigVM_Task>')
            waitresp = self.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['ReconfigVM_TaskResponse']['returnval']['#text'])
            if waitresp != 'success':
                return ("Failed to ReconfigVM_Task: %s" % waitresp)

            # Now update the vmxFile on disk (should not be necessary, but for some reason, sometimes the ReconfigVM_Task does not flush config to disk).
            vmxDict.update({"annotation": annotation})

        if disks:
            curDisks = [{"filename": vmxDict[scsiDisk], "volname": re.sub(r".*--([\w\d]+)\.vmdk", r"\1", vmxDict[scsiDisk])} for scsiDisk in sorted(vmxDict) if re.match(r"scsi0:\d\.filename", scsiDisk)]
            curDisksCount = len(curDisks)
            newDisks = [newDisk for newDisk in disks if ('boot' not in newDisk or newDisk['boot'] == False)]
            for newDiskCount, newDisk in enumerate(newDisks):
                scsiDiskIdx = newDiskCount + curDisksCount
                disk_filename = self.name + "--" + newDisk['volname'] + ".vmdk"

                # Don't clone already-existing disks
                try:
                    (stdin, stdout, stderr) = self.esxiCnx.exec_command("stat " + os.path.dirname(vmxPath) + "/" + disk_filename)
                except IOError as e:
                    if 'src' in newDisk and newDisk['src'] is not None:
                        cloneSrcBackingFile = re.search('^\[(?P<datastore>.*?)\] *(?P<fulldiskpath>.*\/(?P<filepath>(?P<fileroot>.*?)(?:--(?P<diskname_suffix>.*?))?\.vmdk))$', newDisk['src']['backing_filename'])
                        try:
                            (stdin, stdout, stderr) = self.esxiCnx.exec_command("stat /vmfs/volumes/" + cloneSrcBackingFile.group('datastore') + "/" + cloneSrcBackingFile.group('fulldiskpath'))
                        except IOError as e:
                            return (cloneSrcBackingFile.group('fulldiskpath') + " not found!\n" + str(e))
                        else:
                            if newDisk['src']['copy_or_move'] == 'copy':
                                self.esxiCnx.exec_command("vmkfstools -i /vmfs/volumes/" + cloneSrcBackingFile.group('datastore') + "/" + cloneSrcBackingFile.group('fulldiskpath') + " -d thin " + os.path.dirname(vmxPath) + "/" + disk_filename)
                            else:
                                self.esxiCnx.exec_command("vmkfstools -E /vmfs/volumes/" + cloneSrcBackingFile.group('datastore') + "/" + cloneSrcBackingFile.group('fulldiskpath') + " " + os.path.dirname(vmxPath) + "/" + disk_filename)

                    else:
                        (stdin, stdout, stderr) = self.esxiCnx.exec_command("vmkfstools -c " + str(newDisk['size_gb']) + "G -d " + newDisk['type'] + " " + os.path.dirname(vmxPath) + "/" + disk_filename)

                    # if this is a new disk, not a restatement of an existing disk:
                    if len(curDisks) >= newDiskCount + 2 and curDisks[newDiskCount + 1]['volname'] == newDisk['volname']:
                        pass
                    else:
                        vmxDict.update({"scsi0:" + str(scsiDiskIdx) + ".devicetype": "scsi-hardDisk"})
                        vmxDict.update({"scsi0:" + str(scsiDiskIdx) + ".present": "TRUE"})
                        vmxDict.update({"scsi0:" + str(scsiDiskIdx) + ".filename": disk_filename})

        self.put_vmx(vmxDict, vmxPath)
        self.esxiCnx.exec_command("vim-cmd vmsvc/reload " + str(self.moid))

    # def update_vm_pyvmomi(self, annotation=None):
    #     if annotation:
    #         from pyVmomi import vim
    #         from pyVim.task import WaitForTask
    #         from pyVim import connect
    #
    #         SI = connect.SmartConnectNoSSL(host=hostname, user=username, pwd=password, port=443)
    #         vm = SI.content.searchIndex.FindByDnsName(None, self.name, True)
    #
    #         spec = vim.vm.ConfigSpec()
    #         spec.annotation = annotation
    #         task = vm.ReconfigVM_Task(spec)
    #         WaitForTask(task)

    # Delete the cloud-init guestinfo.metadata info from the .vmx file, otherwise it will be impossible to change the network configuration or hostname.
    def delete_cloudinit(self):
        vmxPath, vmxDict = self.get_vmx(self.moid)
        if 'guestinfo.metadata' in vmxDict:
            del vmxDict['guestinfo.metadata']
        if 'guestinfo.metadata.encoding' in vmxDict:
            del vmxDict['guestinfo.metadata.encoding']
        if 'guestinfo.userdata' in vmxDict:
            del vmxDict['guestinfo.userdata']
        if 'guestinfo.userdata.encoding' in vmxDict:
            del vmxDict['guestinfo.userdata.encoding']

        # write the vmx
        self.put_vmx(vmxDict, vmxPath)


def main():
    argument_spec = {
        "hostname": {"type": "str", "required": True},
        "username": {"type": "str", "required": True},
        "password": {"type": "str"},
        "name": {"type": "str"},
        "moid": {"type": "str"},
        "template": {"type": "str"},
        "state": {"type": "str", "default": 'present', "choices": ['absent', 'present', 'unchanged', 'rebootguest', 'poweredon', 'poweredoff', 'shutdownguest']},
        "delete_cloudinit": {"type": "bool", "default": False},
        "force": {"type": "bool", "default": False},
        "datastore": {"type": "str"},
        "annotation": {"type": "str", "default": ""},
        "guest_id": {"type": "str", "default": "ubuntu-64"},
        "hardware": {"type": "dict", "default": {"version": "15", "num_cpus": "2", "memory_mb": "2048", "num_cpu_cores_per_socket": "1", "hotadd_cpu": "False", "hotadd_memory": "False", "memory_reservation_lock": "False"}},
        "cloudinit_userdata": {"type": "list", "default": []},
        "disks": {"type": "list", "default": [{"boot": True, "size_gb": 16, "type": "thin"}]},
        "cdrom": {"type": "dict", "default": {"type": "client"}},
        "networks": {"type": "list", "default": [{"networkName": "VM Network", "virtualDev": "vmxnet3"}]},
        "customvalues": {"type": "list", "default": []},
        "wait": {"type": "bool", "default": True},
        "wait_timeout": {"type": "int", "default": 180}
    }

    if not (len(sys.argv) > 1 and sys.argv[1] == "console"):
        module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True, required_one_of=[['name', 'moid']])
    else:
        # For testing without Ansible (e.g on Windows)
        module = cDummyAnsibleModule()
        ## Update VM
        module.params = {
            "hostname": "192.168.1.3",
            "username": "svc",
            "password": sys.argv[2],
            # "annotation": "{'Name': 'dougal-test-dev-sysdisks2-a0-1617548508', 'hosttype': 'sysdisks2', 'env': 'dev', 'cluster_name': 'dougal-test-dev', 'owner': 'dougal', 'cluster_suffix': '1617548508', 'lifecycle_state': 'retiring', 'maintenance_mode': 'false'}",
            "annotation": None,
            "disks": None,
            "name": "cvtest-16-dd9032f65aef7-dev-sys-b0-1617726990",
            "moid": None,
            "state": "unchanged",
            "wait_timeout": 180
        }

        # ## Delete VM
        # module.params = {
        #     "hostname": "192.168.1.3",
        #     "username": "svc",
        #     "password": sys.argv[2],
        #     "name": "test-asdf",
        #     "moid": None,
        #     "state": "absent"
        # }
        #
        # ## Clone VM
        # module.params = {
        #     "hostname": "192.168.1.3",
        #     "username": "svc",
        #     "password": sys.argv[2],
        #     "annotation": None,
        #     # "annotation": "{'lifecycle_state': 'current', 'Name': 'test-prod-sys-a0-1589979249', 'cluster_suffix': '1589979249', 'hosttype': 'sys', 'cluster_name': 'test-prod', 'env': 'prod', 'owner': 'dougal'}",
        #     "cdrom": {"type": "client"},
        #     "cloudinit_userdata": [],
        #     "customvalues": [],
        #     "datastore": "4tb-evo860-ssd",
        #     "disks": [],
        #     # "disks": [{"size_gb": 1, "type": "thin", "volname": "test"}],
        #     # "disks": [{"size_gb": 1, "type": "thin", "volname": "test", "src": {"backing_filename": "[4tb-evo860-ssd] testdisks-dev-sys-a0-1601204786/testdisks-dev-sys-a0-1601204786--test.vmdk", "copy_or_move": "move"}}],
        #     "delete_cloudinit": False,
        #     "force": False,
        #     "guest_id": "ubuntu-64",
        #     "hardware": {"memory_mb": "2048", "num_cpus": "2", "version": "15"},
        #     "moid": None,
        #     "name": "dougal-test-dev-sys-a0-new",
        #     "networks": [{"cloudinit_netplan": {"ethernets": {"eth0": {"dhcp4": True}}}, "networkName": "VM Network", "virtualDev": "vmxnet3"}],
        #     "state": "present",
        #     "template": "dougal-test-dev-sys-a0-1617553110",
        #     "wait": True,
        #     "wait_timeout": 180
        # }
        #
        # ## Create blank VM
        # module.params = {
        #     "hostname": "192.168.1.3",
        #     "username": "svc",
        #     "password": sys.argv[2],
        #     "name": "test-asdf",
        #     "annotation": "{'Name': 'test-asdf'}",
        #     "datastore": "4tb-evo860-ssd",
        #     "delete_cloudinit": False,
        #     "force": False,
        #     "moid": None,
        #     "template": None,
        #     "state": "present",
        #     "guest_id": "ubuntu-64",
        #     "hardware": {"version": "15", "num_cpus": "2", "memory_mb": "2048"},
        #     "cloudinit_userdata": [],
        #     "disks": [{"boot": True, "size_gb": 16, "type": "thin"}, {"size_gb": 5, "type": "thin"}, {"size_gb": 2, "type": "thin"}],
        #     "cdrom": {"type": "iso", "iso_path": "/vmfs/volumes/4tb-evo860-ssd/ISOs/ubuntu-18.04.2-server-amd64.iso"},
        #     "networks": [{"networkName": "VM Network", "virtualDev": "vmxnet3"}],
        #     "customvalues": [],
        #     "wait": True,
        #     "wait_timeout": 180,
        # }

    iScraper = esxiFreeScraper(hostname=module.params['hostname'],
                               username=module.params['username'],
                               password=module.params['password'],
                               name=module.params['name'],
                               moid=module.params['moid'])

    if iScraper.moid is None and iScraper.name is None:
        module.fail_json(msg="If VM doesn't already exist, you must provide a name for it")

    # Check if the VM exists before continuing
    if module.params['state'] == 'unchanged':
        if iScraper.moid is not None:
            updateVmResult = iScraper.update_vm(annotation=module.params['annotation'], disks=module.params['disks'])
            if updateVmResult != None:
                module.fail_json(msg=updateVmResult)
            module.exit_json(changed=True, meta={"msg": "Shutdown " + iScraper.name + ": " + str(iScraper.moid)})
        else:
            module.fail_json(msg="VM doesn't exist.")

    elif module.params['state'] == 'shutdownguest':
        if iScraper.moid:
            iScraper.soap_client.send_req('<ShutdownGuest><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></ShutdownGuest>')
            time_s = 60
            while time_s > 0:
                (stdin, stdout, stderr) = iScraper.esxiCnx.exec_command("vim-cmd vmsvc/power.getstate " + str(iScraper.moid))
                if re.search('Powered off', stdout.read().decode('UTF-8')) is not None:
                    break
                else:
                    time.sleep(1)
                    time_s = time_s - 1
            module.exit_json(changed=True, meta={"msg": "Shutdown " + iScraper.name + ": " + str(iScraper.moid)})
        else:
            module.fail_json(msg="VM doesn't exist.")

    elif module.params['state'] == 'poweredon':
        if iScraper.moid:
            (stdin, stdout, stderr) = iScraper.esxiCnx.exec_command("vim-cmd vmsvc/power.getstate " + str(iScraper.moid))
            if re.search('Powered off', stdout.read().decode('UTF-8')) is not None:
                response, cookies = iScraper.soap_client.send_req('<PowerOnVM_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></PowerOnVM_Task>')
                if iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['PowerOnVM_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout'])) != 'success':
                    module.fail_json(msg="Failed to PowerOnVM_Task")
                module.exit_json(changed=True, meta={"msg": "Powered-on " + iScraper.name + ": " + str(iScraper.moid)})
            else:
                module.exit_json(changed=False, meta={"msg": "VM " + iScraper.name + ": already on."})
        else:
            module.fail_json(msg="VM doesn't exist.")

    elif module.params['state'] == 'poweredoff':
        if iScraper.moid:
            (stdin, stdout, stderr) = iScraper.esxiCnx.exec_command("vim-cmd vmsvc/power.getstate " + str(iScraper.moid))
            if re.search('Powered on', stdout.read().decode('UTF-8')) is not None:
                response, cookies = iScraper.soap_client.send_req('<PowerOffVM_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></PowerOffVM_Task>')
                if iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['PowerOffVM_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout'])) != 'success':
                    module.fail_json(msg="Failed to PowerOffVM_Task")
                module.exit_json(changed=True, meta={"msg": "Powered-off " + iScraper.name + ": " + str(iScraper.moid)})
            else:
                module.exit_json(changed=False, meta={"msg": "VM " + iScraper.name + ": already off."})
        else:
            module.fail_json(msg="VM doesn't exist.")

    elif module.params['state'] == 'absent':
        if iScraper.moid:
            # Turn off (ignoring failures), then destroy
            response, cookies = iScraper.soap_client.send_req('<PowerOffVM_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></PowerOffVM_Task>')
            iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['PowerOffVM_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout']))

            response, cookies = iScraper.soap_client.send_req('<Destroy_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></Destroy_Task>')
            if iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['Destroy_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout'])) != 'success':
                module.fail_json(msg="Failed to Destroy_Task")
            module.exit_json(changed=True, meta={"msg": "Deleted " + iScraper.name + ": " + str(iScraper.moid)})
        else:
            module.exit_json(changed=False, meta={"msg": "VM " + iScraper.name + ": already absent."})

    elif module.params['state'] == 'rebootguest':
        if iScraper.moid:
            (stdin, stdout, stderr) = iScraper.esxiCnx.exec_command("vim-cmd vmsvc/power.getstate " + str(iScraper.moid))
            if re.search('Powered off', stdout.read().decode('UTF-8')) is not None:
                response, cookies = iScraper.soap_client.send_req('<PowerOnVM_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></PowerOnVM_Task>')
                if iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['PowerOffVM_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout'])) != 'success':
                    module.fail_json(msg="Failed to PowerOnVM_Task")
            else:
                response, cookies = iScraper.soap_client.send_req('<RebootGuest><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></RebootGuest>')
            module.exit_json(changed=True, meta={"msg": "Rebooted " + iScraper.name + ": " + str(iScraper.moid)})
        else:
            module.fail_json(msg="VM doesn't exist.")

    elif module.params['state'] == 'present':
        exit_args = {}
        # If the VM already exists, and the 'force' flag is set, then we delete it (and recreate it)
        if iScraper.moid and module.params['force']:
            # Turn off (ignoring failures), then destroy
            response, cookies = iScraper.soap_client.send_req('<PowerOffVM_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></PowerOffVM_Task>')
            if iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['PowerOffVM_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout'])) != 'success':
                module.fail_json(msg="Failed to PowerOffVM_Task (prior to Destroy_Task")

            response, cookies = iScraper.soap_client.send_req('<Destroy_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></Destroy_Task>')
            if iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['Destroy_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout'])) != 'success':
                module.fail_json(msg="Failed to Destroy_Task")
            iScraper.moid = None

        # If the VM doesn't exist, create it.
        if iScraper.moid is None:
            # If we're cloning, ensure template VM is powered off.
            if module.params['template'] is not None:
                iScraperTemplate = esxiFreeScraper(hostname=module.params['hostname'], username=module.params['username'], password=module.params['password'], name=module.params['template'], moid=None)
                (stdin, stdout, stderr) = iScraper.esxiCnx.exec_command("vim-cmd vmsvc/power.getstate " + str(iScraperTemplate.moid))
                if re.search('Powered off', stdout.read().decode('UTF-8')) is not None:
                    createVmResult = iScraper.create_vm(module.params['template'], module.params['annotation'], module.params['datastore'], module.params['hardware'], module.params['guest_id'], module.params['disks'], module.params['cdrom'], module.params['customvalues'], module.params['networks'], module.params['cloudinit_userdata'])
                    if createVmResult != None:
                        module.fail_json(msg="Failed to create_vm: %s" % createVmResult)
                else:
                    module.fail_json(msg="Template VM must be powered off before cloning")

        else:
            updateVmResult = iScraper.update_vm(annotation=module.params['annotation'], disks=module.params['disks'])
            if updateVmResult != None:
                module.fail_json(msg=updateVmResult)

        (stdin, stdout, stderr) = iScraper.esxiCnx.exec_command("vim-cmd vmsvc/power.getstate " + str(iScraper.moid))
        if re.search('Powered off', stdout.read().decode('UTF-8')) is not None:
            response, cookies = iScraper.soap_client.send_req('<PowerOnVM_Task><_this type="VirtualMachine">' + str(iScraper.moid) + '</_this></PowerOnVM_Task>')
            if iScraper.soap_client.wait_for_task(xmltodict.parse(response.read())['soapenv:Envelope']['soapenv:Body']['PowerOnVM_TaskResponse']['returnval']['#text'], int(module.params['wait_timeout'])) != 'success':
                module.fail_json(msg="Failed to PowerOnVM_Task")

        isChanged = True

        ## Delete the cloud-init config
        if module.params['delete_cloudinit']:
            iScraper.delete_cloudinit()

        ## Wait for IP address and hostname to be advertised by the VM (via open-vm-tools)
        if "wait" in module.params and module.params['wait']:
            time_s = int(module.params['wait_timeout'])
            while time_s > 0:
                (stdin, stdout, stderr) = iScraper.esxiCnx.exec_command("vim-cmd vmsvc/get.guest " + str(iScraper.moid))
                guest_info = stdout.read().decode('UTF-8')
                vm_params = re.search('\s*hostName\s*=\s*\"?(?P<vm_hostname>.*?)\"?,.*\n\s*ipAddress\s*=\s*\"?(?P<vm_ip>.*?)\"?,.*', guest_info)
                if vm_params and vm_params.group('vm_ip') != "<unset>" and vm_params.group('vm_hostname') != "":
                    break
                else:
                    time.sleep(1)
                    time_s = time_s - 1

            module.exit_json(changed=isChanged,
                             guest_info=guest_info,
                             hostname=vm_params.group('vm_hostname'),
                             ip_address=vm_params.group('vm_ip'),
                             name=module.params['name'],
                             moid=iScraper.moid)
        else:
            module.exit_json(changed=isChanged,
                             hostname="",
                             ip_address="",
                             name=module.params['name'],
                             moid=iScraper.moid)

    else:
        module.exit_json(changed=False, meta={"msg": "No state."})


if __name__ == '__main__':
    main()
