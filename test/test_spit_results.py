# Copyright (c) 2017 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

"""Unit tests for library/spit_results.py."""

import os
import unittest
import mock
from library import spit_results

# pylint: disable=missing-docstring, no-self-use

TMP_TEST_REPORT = "/tmp/test_report.csv"


class TestSpitResults(unittest.TestCase):

    def setUp(self):
        if os.path.isfile(TMP_TEST_REPORT):
            os.remove(TMP_TEST_REPORT)

    @mock.patch("library.spit_results.AnsibleModule", autospec=True)
    def test__main__success(self, ansible_mod_cls):
        mod_obj = ansible_mod_cls.return_value
        args = {
            "name": "foo",
            "file_path": TMP_TEST_REPORT,
            "vals": [{'fact1': 'value1'}],
            "fact_names": ["Cpu_cpu.model_ver", "SysId_systemid.system_id",
                           "SysId_systemid.username"]
        }
        mod_obj.params = args
        spit_results.main()
        expected_arguments_spec = {
            "name": {"required": True, "type": "str"},
            "file_path": {"required": True, "type": "str"},
            "vals": {"required": True, "type": "list"},
            "fact_names": {"required": True, "type": "list"}
        }

        assert(mock.call(argument_spec=expected_arguments_spec) ==
               ansible_mod_cls.call_args)
