#
# Copyright (c) 2009 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#

# pylint: disable=too-few-public-methods

""" Unit tests for CLI """

import unittest
import sys
import os
from rho.authaddcommand import AuthAddCommand
from rho.authlistcommand import AuthListCommand
from rho.authclearcommand import AuthClearCommand
from rho.autheditcommand import AuthEditCommand
from rho.authshowcommand import AuthShowCommand
from rho.profileaddcommand import ProfileAddCommand
from rho.profileclearcommand import ProfileClearCommand
from rho.profileeditcommand import ProfileEditCommand
from rho.profilelistcommand import ProfileListCommand
from rho.profileshowcommand import ProfileShowCommand
from rho.scancommand import ScanCommand

TMP_VAULT_PASS = "/tmp/vault_pass"
TMP_FACTS = "/tmp/facts.txt"
TMP_HOSTS = "/tmp/hosts.txt"
TMP_TEST_REPORT = "/tmp/test_report.csv"


class HushUpStderr(object):
    """Class used to quiet standard error output"""
    def write(self, stream):
        """Ignore standard error output"""
        pass


# pylint: disable=too-many-public-methods, no-self-use
class CliCommandsTests(unittest.TestCase):
    """Class for testing the various cli commands for rho"""
    def setUp(self):
        # Temporarily disable stderr for these tests, CLI errors clutter up
        # nosetests command.
        self.orig_stderr = sys.stderr
        sys.stderr = HushUpStderr()
        if os.path.isfile('data'):
            os.remove('data')

        if os.path.isfile(TMP_VAULT_PASS):
            os.remove(TMP_VAULT_PASS)
        with open(TMP_VAULT_PASS, 'w') as vault_pass_file:
            vault_pass_file.write('passw0rd')

        if os.path.isfile(TMP_FACTS):
            os.remove(TMP_FACTS)
        with open(TMP_FACTS, 'w') as facts_file:
            # Username_uname.hostname
            # Username_uname.os
            # Date_date.date
            # Cpu_cpu.bogomips
            # Cpu_cpu.vendor_id
            # RedhatRelease_redhat-release.name
            # RedhatPackages_redhat-packages.num_installed_packages
            facts_file.write('Username_uname.hostname\n')
            facts_file.write('Username_uname.os\n')
            facts_file.write('Date_date.date\n')
            facts_file.write('Cpu_cpu.bogomips\n')
            facts_file.write('Cpu_cpu.vendor_id\n')
            facts_file.write('RedhatRelease_redhat-release.name\n')

        if os.path.isfile(TMP_HOSTS):
            os.remove(TMP_HOSTS)
        with open(TMP_HOSTS, 'w') as hosts_file:
            # 192.168.124.[1:40]
            # 192.168.121.007
            # 192.168.121.140
            # 192.168.124.153
            # 192.168.124.[150:200]
            hosts_file.write('192.168.124.[1:40]\n')
            hosts_file.write('192.168.121.007\n')
            hosts_file.write('192.168.121.140\n')
            hosts_file.write('192.168.124.153\n')
            hosts_file.write('192.168.124.[150:200]\n')

    def tearDown(self):
        # Restore stderr
        sys.stderr = self.orig_stderr
        if os.path.isfile('data'):
            os.remove('data')

        if os.path.isfile(TMP_VAULT_PASS):
            os.remove(TMP_VAULT_PASS)

        if os.path.isfile(TMP_FACTS):
            os.remove(TMP_FACTS)

        if os.path.isfile(TMP_HOSTS):
            os.remove(TMP_HOSTS)

    def test_scan_facts_no_profile(self):
        """Test utilizing the scan command catch no profile error
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--reset", "--reportfile",
                        TMP_TEST_REPORT, "--facts",
                        "default", "ansible_forks",
                        "100", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_scan_facts_no_facts(self):
        """Test utilizing the scan command catch no facts error
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--profile", "profilename",
                        "--reset", "--reportfile",
                        TMP_TEST_REPORT, "ansible_forks",
                        "100", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_scan_facts_no_reportfile(self):
        """Test utilizing the scan command catch no report file error
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--profile", "profilename",
                        "--reset", "--facts", "default", "ansible_forks",
                        "100", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_scan_facts_non_int_forks(self):
        """Test utilizing the scan command catch bad input for forks error
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--profile", "profilename",
                        "--reset", "--reportfile", TMP_TEST_REPORT,
                        "--facts", "default", "ansible_forks",
                        "a", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_scan_facts_neg_int_forks(self):
        """Test utilizing the scan command catch bad input for forks error
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--profile", "profilename",
                        "--reset", "--reportfile",
                        TMP_TEST_REPORT, "--facts",
                        "default", "ansible_forks",
                        "-4", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_scan_facts_default(self):
        """Test utilizing the scan command exercising the collection
        the default facts with 100 ansible forks
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--profile", "profilename",
                        "--reset", "--reportfile",
                        TMP_TEST_REPORT, "--facts",
                        "default", "ansible_forks",
                        "100", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_scan_facts_file(self):
        """Test utilizing the scan command exercising the collection
        the facts from an input facts file with 100 ansible forks
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--profile", "profilename",
                        "--reset", "--reportfile",
                        TMP_TEST_REPORT, "--facts",
                        TMP_FACTS, "ansible_forks",
                        "100", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_scan_facts_list(self):
        """Test utilizing the scan command exercising the collection
        the facts from an input facts list with 100 ansible forks
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "scan", "--profile", "profilename",
                        "--reset", "--reportfile",
                        TMP_TEST_REPORT, "--facts",
                        "Username_uname.all",
                        "Cpu_cpu.bogomips",
                        "--ansible_forks",
                        "100", "--vault", TMP_VAULT_PASS]
            ScanCommand().main()

    def test_profile_list(self):
        """Testing the profle list command execution"""

        sys.argv = ['/bin/rho', "profile", "list",
                    "--vault", TMP_VAULT_PASS]
        ProfileListCommand().main()

    def test_profile_add_hosts_list(self):
        """Test the profile command adding a profile with a list and
        range of hosts and an ordered list of auths
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "profile", "add", "--name",
                        "profilename", "hosts",
                        "1.2.3.4", "1.2.3.[4:100]",
                        "--auths", "auth_1", "auth2",
                        "--vault", TMP_VAULT_PASS]
            ProfileAddCommand().main()

    def test_profile_add_hosts_file(self):
        """Test the profile command adding a profile with a file of hosts
        and an ordered list of auths
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "profile", "add", "--name",
                        "profilename", "hosts",
                        TMP_HOSTS, "--auths",
                        "auth_1", "auth2",
                        "--vault", TMP_VAULT_PASS]
            ProfileAddCommand().main()

    def test_auth_list(self):
        """Testing the auth list command execution"""

        sys.argv = ['/bin/rho', "auth", "list", "--vault",
                    TMP_VAULT_PASS]
        AuthListCommand().main()

    def test_profile_add_nonexist_auth(self):
        """Test the proile add command with an non-existent auth
        in order to catch error case
        """

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "profile", "add", "--name", "profile",
                        "hosts", "1.2.3.4", "--auth", "doesnotexist",
                        "--vault", TMP_VAULT_PASS]
            ProfileAddCommand().main()

    def test_bad_range_options(self):
        """Test profile add command with an invalid host range"""

        # Should fail scanning range without a username:
        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "profile", "add", "--name",
                        "profilename", "hosts",
                        "a:d:b:s", "--auths",
                        "auth_1", "auth2",
                        "--vault", TMP_VAULT_PASS]
            ProfileAddCommand().main()

    def test_a_auth_add(self):
        """Testing the auth add command execution"""

        sys.argv = ['/bin/rho', "auth", "add", "--name", "auth1",
                    "--username", "user", "--sshkeyfile",
                    "./privatekey", "--vault",
                    TMP_VAULT_PASS]
        AuthAddCommand().main()

    def test_a_auth_add_again(self):
        """Testing the auth add command execution"""

        sys.argv = ['/bin/rho', "auth", "add", "--name", "auth2",
                    "--username", "user", "--sshkeyfile",
                    "./privatekey", "--vault",
                    TMP_VAULT_PASS]
        AuthAddCommand().main()

    def test_a_profile_add(self):
        """Testing the profile add command execution"""

        sys.argv = ['/bin/rho', "profile", "add", "--name", "p1",
                    "--hosts", "1.2.3.4",
                    "--auth", "auth1",
                    "--vault", TMP_VAULT_PASS]
        ProfileAddCommand().main()

    def test_a_profile_add_existing(self):
        """Testing the profile add command execution"""

        with self.assertRaises(SystemExit):
            sys.argv = ['/bin/rho', "profile", "add", "--name",
                        "p1", "--hosts", "1.2.3.4",
                        "--auth", "auth1",
                        "--vault", TMP_VAULT_PASS]
            ProfileAddCommand().main()

    def test_auth_edit(self):
        """Testing the auth edit command execution"""

        sys.argv = ['/bin/rho', "auth", "edit", "--name", "auth1",
                    "--username", "user",
                    "--sshkeyfile", "./privatekey",
                    "--vault", TMP_VAULT_PASS]
        AuthEditCommand().main()

    def test_auth_show(self):
        """Testing the auth show command execution"""

        sys.argv = ['/bin/rho', "auth", "show", "--name", "auth1",
                    "--vault", TMP_VAULT_PASS]
        AuthShowCommand().main()

    def test_profile_edit(self):
        """Testing the profile edit command execution"""

        sys.argv = ['/bin/rho', "profile", "edit", "--name",
                    "p1", "--hosts", "1.2.3.4",
                    "--auth", "auth1",
                    "--vault", TMP_VAULT_PASS]
        ProfileEditCommand().main()

    def test_profile_show(self):
        """Testing the profile show command execution"""

        sys.argv = ['/bin/rho', "profile", "show", "--name",
                    "p1", "--vault", TMP_VAULT_PASS]
        ProfileShowCommand().main()

    def test_z_auth_clear_all(self):
        """Testing the auth clear all command execution"""

        sys.argv = ['/bin/rho', "auth", "clear", "--all",
                    "--vault", TMP_VAULT_PASS]
        AuthClearCommand().main()

    def test_z_profile_clear_all(self):
        """Testing the profile clear all command execution"""

        sys.argv = ['/bin/rho', "profile", "clear", "--all",
                    "--vault", TMP_VAULT_PASS]
        ProfileClearCommand().main()
