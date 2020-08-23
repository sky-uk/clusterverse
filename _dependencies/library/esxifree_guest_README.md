# esxifree_guest
https://github.com/dseeley/esxifree_guest

This module can be used to create new ESXi virtual machines, including cloning from templates or other virtual machines. 

It does so using direct SOAP calls and Paramiko SSH to the host - without using the vSphere API - meaning it can be used on the free hypervisor.

## Configuration
Your ESXi host needs some config:
+ Enable SSH
  + Inside the web UI, navigate to “Manage”, then the “Services” tab. Find the entry called: “TSM-SSH”, and enable it.
+ Enable “Guest IP Hack”
  + `esxcli system settings advanced set -o /Net/GuestIPHack -i 1`
+ Open VNC Ports on the Firewall
    ```
    Packer connects to the VM using VNC, so we’ll open a range of ports to allow it to connect to it.
    
    First, ensure we can edit the firewall configuration:
    
    chmod 644 /etc/vmware/firewall/service.xml
    chmod +t /etc/vmware/firewall/service.xml
    Then append the range we want to open to the end of the file:
    
    <service id="1000">
      <id>packer-vnc</id>
      <rule id="0000">
        <direction>inbound</direction>
        <protocol>tcp</protocol>
        <porttype>dst</porttype>
        <port>
          <begin>5900</begin>
          <end>6000</end>
        </port>
      </rule>
      <enabled>true</enabled>
      <required>true</required>
    </service>
    Finally, restore the permissions and reload the firewall:
    
    chmod 444 /etc/vmware/firewall/service.xml
    esxcli network firewall refresh
    ```

## Requirements
+ python 3
+ paramiko
+ Any base-images from which clones are to be made must have cloud-init and [`cloud-init-vmware-guestinfo`](https://github.com/vmware/cloud-init-vmware-guestinfo) installed

## Execution
This can be run as an Ansible module (see inline documentation), or from the console:
```bash
python3 ./esxifree_guest.py console
```