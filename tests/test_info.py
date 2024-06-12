import unittest
from unittest.mock import patch

from proximate_utils.info import Info


class InfoTest(unittest.TestCase):

  @patch('proxmoxer.ProxmoxAPI')
  def setUp(self, mock_proxmox):
    self.mock_proxmox = mock_proxmox
    self.info = Info(self.mock_proxmox)

  def test_version(self):
    mock_version = {'version': '6.5'}
    self.mock_proxmox.version.get.return_value = mock_version
    version = self.info.version()
    self.assertEqual(version, mock_version)

  def test_version_error(self):
    self.mock_proxmox.version.get.side_effect = Exception("Test Error")
    version = self.info.version()
    self.assertIsNone(version)

  def test_get_nextvmid(self):
    mock_nextvmid = {'nextid': 100}
    self.mock_proxmox.cluster.nextid.get.return_value = mock_nextvmid
    nextvmid = self.info.get_nextvmid()
    self.assertEqual(nextvmid, mock_nextvmid)

  def test_get_nextvmid_error(self):
    self.mock_proxmox.cluster.nextid.get.side_effect = Exception("Test Error")
    nextvmid = self.info.get_nextvmid()
    self.assertIsNone(nextvmid)

  def test_get_vmid_found(self):
    mock_vms = [{'vmid': 100, 'name': 'testvm'}, {'vmid': 101, 'name': 'othervm'}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vmid = self.info.get_vmid('testvm')
    self.assertEqual(vmid, 100)

  def test_get_vmid_not_found(self):
    mock_vms = [{'vmid': 100, 'name': 'othervm'}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vmid = self.info.get_vmid('testvm')
    self.assertIsNone(vmid)

  def test_get_vmid_not_found_ignore_missing(self):
    mock_vms = [{'vmid': 100, 'name': 'othervm'}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vmid = self.info.get_vmid('testvm', ignore_missing=True)
    self.assertIsNone(vmid)

  def test_get_vmid_multiple_found(self):
    mock_vms = [{'vmid': 100, 'name': 'testvm'}, {'vmid': 101, 'name': 'testvm'}]
    self.mock_proxmox.cluster.resources.get.return_value = mock_vms
    vmid = self.info.get_vmid('testvm')
    self.assertIsNone(vmid)


if __name__ == '__main__':
  unittest.main()
