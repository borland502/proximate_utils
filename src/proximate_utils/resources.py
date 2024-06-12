"""Base resources module for the Proxmoxer API.

https://github.com/ansible-collections/community.general/blob/d2d7deb4ecb978dd21a68b4ebd372da891ee3029/plugins/module_utils/proxmox.py#L12
"""

from proxmoxer import ProxmoxAPI
import logging


class Resources:
    def __init__(self, proxmox: ProxmoxAPI):
        self.proxmox = proxmox
        self.log: logging.Logger = logging.getLogger("Resources")

    def get_nodes(self):
        try:
            return [node for node in self.proxmox.nodes.get()]
        except Exception as e:
            self.log.error(msg="Unable to retrieve Proxmox VE nodes: %s" % e)

    def get_node(self, node):
        try:
            return [n for n in self.proxmox.nodes.get() if n["node"] == node][0]
        except Exception as e:
            self.log.error(msg="Unable to retrieve Proxmox VE node: %s" % e)

    def get_vms(self) -> list:
        return [vm for vm in self.proxmox.cluster.resources.get(type="vm")]

    def get_vm(self, vmid, ignore_missing=False):
        global vms
        try:
            vms = [vm for vm in self.proxmox.cluster.resources.get(type="vm") if vm["vmid"] == int(vmid)]
        except Exception as e:
            vms = None
            self.log.error(msg="Unable to retrieve list of VMs filtered by vmid %s: %s" % (vmid, e))
        if vms:
            return vms[0]
        else:
            if ignore_missing:
                return None
            self.log.error(msg="VM with vmid %s does not exist in cluster" % vmid)

    def get_pool(self, poolid):
        """Retrieve pool information
        :param poolid: str - name of the pool
        :return: dict - pool information
        """
        try:
            return self.proxmox.pools(poolid).get()
        except Exception as e:
            self.log.error(msg="Unable to retrieve pool %s information: %s" % (poolid, e))

    def get_storages(self, type):
        """Retrieve storages information
        :param type: str, optional - type of storages
        :return: list of dicts - array of storages
        """
        try:
            return self.proxmox.storage.get(type=type)
        except Exception as e:
            self.log.error(msg="Unable to retrieve storages information with type %s: %s" % (type, e))

    def get_storage_content(self, node, storage, content=None, vmid=None):
        try:
            return self.proxmox.nodes(node).storage(storage).content().get(content=content, vmid=vmid)
        except Exception as e:
            self.log.error(msg="Unable to list content on %s, %s for %s and %s: %s" % (node, storage, content, vmid, e))
