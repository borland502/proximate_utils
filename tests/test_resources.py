import unittest
from unittest.mock import patch

from proximate_utils.resources import Resources


class ResourcesTest(unittest.TestCase):

  @patch('proxmoxer.ProxmoxAPI')
  def setUp(self, mock_proxmox):
    self.mock_proxmox = mock_proxmox
    self.resources = Resources(self.mock_proxmox)

  def test_get_nodes(self):
    mock_nodes = [{'node': 'node1'}, {'node': 'node2'}]
    self.mock_proxmox.nodes.get.return_value = mock_nodes
    nodes = self.resources.get_nodes()
    self.assertEqual(nodes, mock_nodes)

  def test_get_nodes_error(self):
    self.mock_proxmox.nodes.get.side_effect = Exception("Test Error")
    nodes = self.resources.get_nodes()
    self.assertIsNone(nodes)

  def test_get_node(self):
    mock_nodes = [{'node': 'node1'}, {'node': 'node2'}]
    self.mock_proxmox.nodes.get.return_value = mock_nodes
    node = self.resources.get_node('node1')
    self.assertEqual(node, {'node': 'node1'})

  def test_get_node_error(self):
    self.mock_proxmox.nodes.get.side_effect = Exception("Test Error")
    node = self.resources.get_node('node1')
    self.assertIsNone(node)

  def test_get_vms(self):
    mock_vms = [{'vmid': 100}, {'vmid': 101}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vms = self.resources.get_vms()
    self.assertEqual(vms, mock_vms)

  def test_get_vm(self):
    mock_vms = [{'vmid': 100}, {'vmid': 101}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vm = self.resources.get_vm(100)
    self.assertEqual(vm, {'vmid': 100})

  def test_get_vm_not_found(self):
    mock_vms = [{'vmid': 100}, {'vmid': 101}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vm = self.resources.get_vm(102)
    self.assertIsNone(vm)

  def test_get_vm_ignore_missing(self):
    mock_vms = [{'vmid': 100}, {'vmid': 101}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vm = self.resources.get_vm(102, ignore_missing=True)
    self.assertIsNone(vm)

  def test_get_vm_error(self):
    self.mock_proxmox.cluster.resources.get.side_effect = Exception("Test Error")
    vm = self.resources.get_vm(100)
    self.assertIsNone(vm)

  def test_get_pool(self):
    mock_pool = {'poolid': 'pool1'}
    self.mock_proxmox.pools.return_value.get.return_value = mock_pool
    pool = self.resources.get_pool('pool1')
    self.assertEqual(pool, mock_pool)

  def test_get_pool_error(self):
    self.mock_proxmox.pools.return_value.get.side_effect = Exception("Test Error")
    pool = self.resources.get_pool('pool1')
    self.assertIsNone(pool)

  def test_get_storages(self):
    mock_storages = [{'storage': 'storage1'}, {'storage': 'storage2'}]
    self.mock_proxmox.storage.get.return_value = mock_storages
    storages = self.resources.get_storages('type')
    self.assertEqual(storages, mock_storages)

  def test_get_storages_error(self):
    self.mock_proxmox.storage.get.side_effect = Exception("Test Error")
    storages = self.resources.get_storages('type')
    self.assertIsNone(storages)

  def test_get_storage_content(self):
    mock_content = {'content': 'content1'}
    self.mock_proxmox.nodes.return_value.storage.return_value.content.return_value.get.return_value = mock_content
    content = self.resources.get_storage_content('node1', 'storage1', 'content1', 100)
    self.assertEqual(content, mock_content)

  def test_get_storage_content_error(self):
    self.mock_proxmox.nodes.return_value.storage.return_value.content.return_value.get.side_effect = Exception("Test Error")
    content = self.resources.get_storage_content('node1', 'storage1', 'content1', 100)
    self.assertIsNone(content)


if __name__ == '__main__':
  unittest.main()
