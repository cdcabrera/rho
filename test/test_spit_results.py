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
        pkg_line = """
        pciutils|3.5.1|2.el7|1500397509|Red Hat, Inc.|1491250625|
        x86-038.build.eng.bos.redhat.com|pciutils-3.5.1-2.el7.src.rpm|
        GPLv2+|Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>|
        Tue 18 Jul 2017 01:05:09 PM EDT|Mon 03 Apr 2017 04:17:05 PM EDT
        """
        args = {
            "name": "foo",
            "file_path": TMP_TEST_REPORT,
            "vals": [{'connection.uuid': '1',
                      'systemid.contents': '',
                      'redhat-packages.results': [pkg_line]}],
            "all_vars": {'host1':
                         {'fact1': 'value1',
                          'fact2': 'value2',
                          'res': {'fact3': 'value3'},
                          'connection': {'connection.uuid': '1'},
                          'jboss.jar-ver':
                          {'stdout_lines':
                           ['1.5.4.Final-redhat-1**2017-08-03']}}},
            "fact_names": ['fact1', 'connection.uuid',
                           'systemid.username',
                           'redhat-packages.last_built',
                           'jboss.deploy-dates', 'jboss.installed-versions']
        }
        mod_obj.params = args
        spit_results.main()
        expected_arguments_spec = {
            "name": {"required": True, "type": "str"},
            "file_path": {"required": True, "type": "str"},
            "vals": {"required": True, "type": "list"},
            "all_vars": {"required": True, "type": "dict"},
            "fact_names": {"required": True, "type": "list"}
        }

        assert(mock.call(argument_spec=expected_arguments_spec) ==
               ansible_mod_cls.call_args)


class TestSafeAnsibleProperty(unittest.TestCase):
    def test_missing_fact(self):
        self.assertEqual(
            spit_results.safe_ansible_property(
                {'foo': 'bar'}, 'baz', 'property'),
            None)

    def test_skipped_fact(self):
        self.assertEqual(
            spit_results.safe_ansible_property(
                {'foo': {'skipped': True}}, 'foo', 'property'),
            None)

    def test_not_skipped_fact(self):
        fact = {'skipped': False,
                'property': 'value'}
        self.assertEqual(
            spit_results.safe_ansible_property(
                {'foo': fact}, 'foo', 'property'),
            'value')

    def test_skipped_not_present(self):
        fact = {'property': 'value'}
        self.assertEqual(
            spit_results.safe_ansible_property(
                {'foo': fact}, 'foo', 'property'),
            'value')


class TestProcessIdUJboss(unittest.TestCase):
    def run_func(self, output):
        return spit_results.process_id_u_jboss(
            ['jboss.eap.jboss-user'],
            {'jboss_eap_id_jboss': output})

    def test_fact_not_requested(self):
        self.assertEqual(
            spit_results.process_id_u_jboss([], None),
            {})

    def test_wrongly_skipped(self):
        res = self.run_func({'skipped': True})
        self.assertTrue('jboss.eap.jboss-user' in res and
                        res['jboss.eap.jboss-user'].startswith('Error:'),
                        msg=res['jboss.eap.jboss-user'])

    def test_user_found(self):
        self.assertEqual(
            self.run_func({'rc': 0, 'stdout_lines': []}),
            {'jboss.eap.jboss-user': "User 'jboss' present"})

    def test_no_such_user(self):
        self.assertEqual(
            self.run_func({'rc': 1,
                           'stdout_lines': ['id: jboss: no such user']}),
            {'jboss.eap.jboss-user': 'No user "jboss" found'})

    def test_unknown_error(self):
        res = self.run_func({'rc': 1,
                             'stdout_lines': ['id: something went wrong!']})

        self.assertTrue('jboss.eap.jboss-user' in res and
                        res['jboss.eap.jboss-user'].startswith('Error:'),
                        msg=res['jboss.eap.jboss-user'])


class TestProcessJbossCommonDirectories(unittest.TestCase):
    def run_func(self, output):
        return spit_results.process_jboss_eap_common_dirs(
            ['jboss.eap.common-directories'],
            {'jboss_eap_common_directories': output})

    def test_fact_not_requested(self):
        self.assertEqual(
            spit_results.process_jboss_eap_common_dirs([], {}),
            {})

    def test_not_in_host_vars(self):
        res = spit_results.process_jboss_eap_common_dirs(
            ['jboss.eap.common-directories'], {})

        self.assertTrue(
            'jboss.eap.common-directories' in res and
            res['jboss.eap.common-directories'].startswith('Error:'),
            msg=res['jboss.eap.common-directories'])

    def test_three_states(self):
        self.assertEqual(
            self.run_func({
                'results': [
                    {'item': 'dir1',
                     'skipped': True},
                    {'item': 'dir2',
                     'rc': 1},
                    {'item': 'dir3',
                     'rc': 0}]}),
            {'jboss.eap.common-directories':
             'Error: "test -d dir1" not run;'
             'dir2 not found;'
             'dir3 found'})


class TestProcessJbossEapProcesses(unittest.TestCase):
    def run_func(self, output):
        return spit_results.process_jboss_eap_processes(
            ['jboss.eap.processes'],
            {'jboss.eap.processes': output})

    def test_no_processes(self):
        self.assertEqual(
            self.run_func({'rc': 1, 'stdout_lines': []}),
            {'jboss.eap.processes': 'No EAP processes found'})

    def test_found_processes(self):
        self.assertEqual(
            self.run_func({'rc': 0, 'stdout_lines': [1, 2, 3]}),
            {'jboss.eap.processes': '2 EAP processes found'})


class TestProcessJbossEapPackages(unittest.TestCase):
    def run_func(self, output):
        return spit_results.process_jboss_eap_packages(
            ['jboss.eap.packages'],
            {'jboss.eap.packages': output})

    def test_nonzero_return_code(self):
        self.assertEqual(
            self.run_func({'rc': 1, 'stdout_lines': []}),
            {'jboss.eap.packages': 'Pipeline returned non-zero status'})

    def test_found_packages(self):
        self.assertEqual(
            self.run_func({'rc': 0, 'stdout_lines': ['a', 'b', 'c']}),
            {'jboss.eap.packages': '3 JBoss-related packages found'})

    def test_no_packages(self):
        self.assertEqual(
            self.run_func({'rc': 0, 'stdout_lines': []}),
            {'jboss.eap.packages': '0 JBoss-related packages found'})
