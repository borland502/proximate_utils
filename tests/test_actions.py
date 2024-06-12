import unittest
from unittest.mock import patch

from mockito import when

from proximate_utils.actions import Actions


class ActionsTest(unittest.TestCase):

  @patch('proxmoxer.ProxmoxAPI')
  @patch('proximate_utils.info.Info')
  def setUp(self, mock_proxmox, mock_info):
    self.mock_proxmox = mock_proxmox
    self.mock_info = mock_info
    self.mock_info.version.return_value = '8.5'
    self.actions = Actions(self.mock_proxmox, self.mock_info)

  def test_is_template_container_lxc(self):
    self.actions.VZ_TYPE = 'lxc'
    mock_config = {'template': True}
    self.mock_proxmox.nodes.return_value.lxc.return_value.config.get.return_value = mock_config
    result = self.actions.is_template_container('node1', 100)
    self.assertTrue(result)

  def test_is_template_container_lxc_false(self):
    self.actions.VZ_TYPE = 'lxc'
    mock_config = {'template': False}
    self.mock_proxmox.nodes.return_value.lxc.return_value.config.get.return_value = mock_config
    result = self.actions.is_template_container('node1', 100)
    self.assertFalse(result)

  def test_is_template_container_openvz(self):
    self.actions.VZ_TYPE = 'openvz'
    mock_config = {'template': True}
    self.mock_proxmox.nodes.return_value.openvz.return_value.config.get.return_value = mock_config
    result = self.actions.is_template_container('node1', 100)
    self.assertTrue(result)

  def test_is_template_container_openvz_false(self):
    self.actions.VZ_TYPE = 'openvz'
    mock_config = {'template': False}
    self.mock_proxmox.nodes.return_value.openvz.return_value.config.get.return_value = mock_config
    result = self.actions.is_template_container('node1', 100)
    self.assertFalse(result)

  def test_create_instance_lxc_success(self):
    self.actions.VZ_TYPE = 'lxc'
    self.mock_info.version.return_value = '6.5'
    self.mock_info.api_task_ok.return_value = True
    mock_taskid = 100
    self.mock_proxmox.nodes.return_value.lxc.return_value.create.return_value = mock_taskid
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=10, clone=None,
                                          netif={'name': 'eth0', 'ip': '192.168.1.100', 'hwaddr': '00:16:3e:22:44:55'},
                                          mounts={'mp': '/mnt/data', 'target': '/data', 'options': 'bind,create=dir'})
    self.assertTrue(result)

  def test_create_instance_lxc_timeout(self):
    self.actions.VZ_TYPE = 'lxc'
    self.mock_info.version.return_value = '6.5'
    self.mock_info.api_task_ok.return_value = False
    mock_taskid = 100
    self.mock_proxmox.nodes.return_value.lxc.return_value.create.return_value = mock_taskid
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=1, clone=None,
                                          netif={'name': 'eth0', 'ip': '192.168.1.100', 'hwaddr': '00:16:3e:22:44:55'},
                                          mounts={'mp': '/mnt/data', 'target': '/data', 'options': 'bind,create=dir'})
    self.assertFalse(result)

  def test_create_instance_lxc_unsupported_feature(self):
    self.actions.VZ_TYPE = 'lxc'
    self.mock_info.version.return_value = '6.0'
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=10, clone=None,
                                          netif={'name': 'eth0', 'ip': '192.168.1.100', 'hwaddr': '00:16:3e:22:44:55'},
                                          mounts={'mp': '/mnt/data', 'target': '/data', 'options': 'bind,create=dir'},
                                          tags=['testtag'])
    self.assertFalse(result)

  def test_create_instance_openvz_success(self):
    self.actions.VZ_TYPE = 'openvz'
    self.mock_info.version.return_value = '6.5'
    self.mock_info.api_task_ok.return_value = True
    mock_taskid = 100
    self.mock_proxmox.nodes.return_value.openvz.return_value.create.return_value = mock_taskid
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=10, clone=None)
    self.assertTrue(result)

  def test_create_instance_openvz_timeout(self):
    self.actions.VZ_TYPE = 'openvz'
    self.mock_info.version.return_value = '6.5'
    self.mock_info.api_task_ok.return_value = False
    mock_taskid = 100
    self.mock_proxmox.nodes.return_value.openvz.return_value.create.return_value = mock_taskid
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=1, clone=None)
    self.assertFalse(result)

  def test_create_instance_clone_lxc_success(self):
    self.actions.VZ_TYPE = 'lxc'
    self.mock_info.version.return_value = '6.5'
    self.mock_info.api_task_ok.return_value = True
    mock_taskid = 100
    self.mock_proxmox.nodes.return_value.lxc.return_value.clone.post.return_value = mock_taskid
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=10, clone=101)
    self.assertTrue(result)

  def test_create_instance_clone_openvz_error(self):
    self.actions.VZ_TYPE = 'openvz'
    self.mock_info.version.return_value = '6.5'
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=10, clone=101)
    self.assertFalse(result)

  def test_create_instance_invalid_tag(self):
    self.actions.VZ_TYPE = 'lxc'
    self.mock_info.version.return_value = '6.5'
    self.mock_info.api_task_ok.return_value = True
    mock_taskid = 100
    self.mock_proxmox.nodes.return_value.lxc.return_value.create.return_value = mock_taskid
    result = self.actions.create_instance(vmid=100, node='node1', disk='local-lvm:vm-100-disk-0', storage='local', cpus=2,
                                          memory=1024, swap=0, timeout=10, clone=None, tags=['invalid-$-tag'])
    self.assertFalse(result)


if __name__ == '__main__':
  unittest.main()
