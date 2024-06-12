"""Actions module for proxmox tasks using proxmoxer

Logic adapted from:
https://github.com/ansible-collections/community.general/blob/d2d7deb4ecb978dd21a68b4ebd372da891ee3029/plugins/module_utils/proxmox.py#L12
https://github.com/ansible-collections/community.general/blob/d2d7deb4ecb978dd21a68b4ebd372da891ee3029/plugins/modules/proxmox.py
"""

import re
import time

from proxmoxer import ProxmoxAPI

from proximate_utils.info import Info
from proximate_utils.resources import Resources
from proximate_utils.version import LooseVersion


class Actions(Resources):
    def __init__(self, proxmox: ProxmoxAPI, info: Info):
        super().__init__(proxmox)
        self.info: Info = info
        self.VZ_TYPE = "openvz" if LooseVersion(self.info.version()) < "4.0" else "lxc"

    def is_template_container(self, node, vmid):
        """Check if the specified container is a template."""
        proxmox_node = self.proxmox.nodes(node)
        config = getattr(proxmox_node, self.VZ_TYPE)(vmid).config.get()
        return config.get("template", False)

    def create_instance(self, vmid, node, disk, storage, cpus, memory, swap, timeout, clone, **kwargs):
        # Version limited features
        minimum_version = {"tags": "6.1", "timezone": "6.3"}
        proxmox_node = self.proxmox.nodes(node)

        # Remove all empty kwarg entries
        kwargs = dict((k, v) for k, v in kwargs.items() if v is not None)

        pve_version = LooseVersion(self.info.version())

        # Fail on unsupported features
        for option, version in minimum_version.items():
            if pve_version < LooseVersion(version) and option in kwargs:
                self.log.error(
                    msg="Feature {option} is only supported in PVE {version}+, and you're using PVE {pve_version}".format(
                        option=option, version=version, pve_version=pve_version
                    )
                )
                return False

        if self.VZ_TYPE == "lxc":
            kwargs["cpulimit"] = cpus
            kwargs["rootfs"] = disk
            if "netif" in kwargs:
                kwargs.update(kwargs["netif"])
                del kwargs["netif"]
            if "mounts" in kwargs:
                kwargs.update(kwargs["mounts"])
                del kwargs["mounts"]
            if "pubkey" in kwargs:
                if self.info.version() >= "4.2":
                    kwargs["ssh-public-keys"] = kwargs["pubkey"]
                del kwargs["pubkey"]
        else:
            kwargs["cpus"] = cpus
            kwargs["disk"] = disk

        # LXC tags are expected to be valid and presented as a comma/semi-colon delimited string
        if "tags" in kwargs:
            re_tag = re.compile(r"^[a-z0-9_][a-z0-9_\-\+\.]*$")
            for tag in kwargs["tags"]:
                if not re_tag.match(tag):
                    self.log.error(msg="%s is not a valid tag" % tag)
                    return False
            kwargs["tags"] = ",".join(kwargs["tags"])

        if kwargs.get("ostype") == "auto":
            kwargs.pop("ostype")

        if clone is not None:
            if self.VZ_TYPE != "lxc":
                self.log.error(msg="Clone operator is only supported for LXC enabled proxmox clusters.")
                return False

            # clone_is_template = self.is_template_container(node, clone)
            # TODO: Integrate options back without adopting ansible structure completely
            clone_parameters = {}

            taskid = getattr(proxmox_node, self.VZ_TYPE)(clone).clone.post(newid=vmid, **clone_parameters)
        else:
            taskid = getattr(proxmox_node, self.VZ_TYPE).create(vmid=vmid, storage=storage, memory=memory, swap=swap, **kwargs)

        while timeout:
            if self.info.api_task_ok(node, taskid):
                return True
            timeout -= 1
            if timeout == 0:
                self.log.error(
                    msg="Reached timeout while waiting for creating VM. Last line in task before timeout: %s"
                    % proxmox_node.tasks(taskid).log.get()[:1]
                )
                return False
            time.sleep(1)
        return False
