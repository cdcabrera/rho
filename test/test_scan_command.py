# Copyright (c) 2017 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

"""Unit tests for the scan command."""

# This file has tests for specific functions in rho.scancommand, but
# does not actually call ScanCommand.main(). The tests that do call
# main are in test_clicommand.py, becuase that's where the
# infrastructure for mocking out credentials and profiles is.

import unittest
import mock

from rho import scancommand


class TestScanCommand(unittest.TestCase):
    def test_make_inventory_dict_one_host(self):
        auth_item = [
            '1',       # ID
            'auth_1',  # name
            'user',    # username
            'pass',    # password
            'sshkey']  # ssh_key_file
        self.assertEqual(
            scancommand.make_inventory_dict(
                ['host_ip_1'],                       # success_map
                {'host_ip_1': '22'},                 # success_port_map
                {tuple(auth_item): ['host_ip_1']}),  # best_map
            {'alpha':
             {'hosts':
              {'host_ip_1':
               {'ansible_host': 'host_ip_1',
                'ansible_port': '22',
                'ansible_user': 'user',
                'ansible_ssh_pass': 'pass',
                'ansible_ssh_private_key_file': 'sshkey'}}}})
