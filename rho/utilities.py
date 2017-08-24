#
# Copyright (c) 2009-2016 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

""" A set of reusable methods common to many of the commands """

from __future__ import print_function
import os
import sys
import re
from rho.translation import _

CREDENTIALS_PATH = 'data/credentials'
PROFILES_PATH = 'data/profiles'

PLAYBOOK_DEV_PATH = 'rho_playbook.yml'
PLAYBOOK_RPM_PATH = '/usr/share/ansible/rho/rho_playbook.yml'

PASSWORD_MASKING = '********'

SENSITIVE_FACTS_TUPLE = ('connection.host',
                         'connection.port',
                         'uname.all',
                         'uname.hostname')

CONNECTION_FACTS_TUPLE = ('connection.host',
                          'connection.port',
                          'connection.uuid')
UNAME_FACTS_TUPLE = ('uname.os',
                     'uname.hostname',
                     'uname.processor',
                     'uname.kernel',
                     'uname.all',
                     'uname.hardware_platform')

REDHAT_RELEASE_FACTS_TUPLE = ('redhat-release.name',
                              'redhat-release.version',
                              'redhat-release.release')

INSTNUM_FACTS_TUPLE = ('instnum.instnum',)

SYSID_FACTS_TUPLE = ('systemid.system_id',
                     'systemid.username')

CPU_FACTS_TUPLE = ('cpu.count',
                   'cpu.socket_count',
                   'cpu.vendor_id',
                   'cpu.bogomips',
                   'cpu.cpu_family',
                   'cpu.model_name',
                   'cpu.model_ver')

ETC_RELEASE_FACTS_TUPLE = ('etc_release.name',
                           'etc_release.version',
                           'etc_release.release')

ETC_ISSUE_FACTS_TUPLE = ('etc-issue.etc-issue',)

DMI_FACTS_TUPLE = ('dmi.bios-vendor',
                   'dmi.bios-version',
                   'dmi.system-manufacturer',
                   'dmi.processor-family')

VIRT_FACTS_TUPLE = ('virt.virt',
                    'virt.type',
                    'virt.num_guests',
                    'virt.num_running_guests')

RH_PKG_FACTS_TUPLE = ('redhat-packages.is_redhat',
                      'redhat-packages.num_rh_packages',
                      'redhat-packages.num_installed_packages',
                      'redhat-packages.last_installed',
                      'redhat-packages.last_built')

VIRT_WHAT_FACTS_TUPLE = ('virt-what.type',)

DATE_FACTS_TUPLE = ('date.date',
                    'date.anaconda_log',
                    'date.machine_id',
                    'date.filesystem_create',
                    'date.yum_history')

SUBMAN_FACTS_TUPLE = ('subman.cpu.core(s)_per_socket',
                      'subman.cpu.cpu(s)',
                      'subman.cpu.cpu_socket(s)',
                      'subman.virt.host_type',
                      'subman.virt.is_guest',
                      'subman.virt.uuid',
                      'subman.has_facts_file')

JBOSS_FACTS_TUPLE = ('jboss.installed-versions',
                     'jboss.deploy-dates',
                     'jboss.running-versions')

BRMS_FACTS_TUPLE = ('jboss.brms.kie-api-ver',
                    'jboss.brms.drools-core-ver',
                    'jboss.brms.kie-war-ver')

FUSE_FACTS_TUPLE = ('jboss.fuse.activemq-ver',
                    'jboss.fuse.camel-ver',
                    'jboss.fuse.cxf-ver')

DEFAULT_FACTS_TUPLE = SUBMAN_FACTS_TUPLE + DATE_FACTS_TUPLE \
    + VIRT_WHAT_FACTS_TUPLE + RH_PKG_FACTS_TUPLE + VIRT_FACTS_TUPLE \
    + DMI_FACTS_TUPLE + ETC_ISSUE_FACTS_TUPLE + ETC_RELEASE_FACTS_TUPLE \
    + CPU_FACTS_TUPLE + SYSID_FACTS_TUPLE + INSTNUM_FACTS_TUPLE \
    + REDHAT_RELEASE_FACTS_TUPLE + UNAME_FACTS_TUPLE \
    + JBOSS_FACTS_TUPLE + BRMS_FACTS_TUPLE + FUSE_FACTS_TUPLE \
    + CONNECTION_FACTS_TUPLE


def ensure_config_dir_exists():
    """Ensure the Rho configuration directory exists."""

    if not os.path.exists('data'):
        os.makedirs('data')


# pylint: disable=unused-argument
def multi_arg(option, opt_str, value, parser):
    """Call back function for arg-parse
    for when arguments are multiple
    :param option: The option
    :param opt_str: The option string
    :param value: The value
    :param parser: The parser for handling the option
    """
    args = []
    for arg in parser.rargs:
        if arg[0] != "-":
            args.append(arg)
        else:
            del parser.rargs[:len(args)]
            break
    if getattr(parser.values, option.dest):
        args.extend(getattr(parser.values, option.dest))
    setattr(parser.values, option.dest, args)


# Read in a file and make it a list
def _read_in_file(filename):
    result = None
    hosts = None
    try:
        hosts = open(os.path.expanduser(os.path.expandvars(filename)), "r")
        result = hosts.read().splitlines()
        hosts.close()
    except EnvironmentError as err:
        sys.stderr.write('Error reading from %s: %s\n' % (filename, err))
        hosts.close()
    return result


# Makes sure the hosts passed in are in a format Ansible
# understands.
def _check_range_validity(range_list):
    # pylint: disable=anomalous-backslash-in-string
    regex_list = ['www\[[0-9]*:[0-9]*\].[a-z]*.[a-z]*',
                  '[a-z]*-\[[a-z]*:[a-z]*\].[a-z]*.[a-z]*',
                  '[0-9]*.[0-9]*.[0-9]'
                  '*.\[[0-9]*:[0-9]*\]',
                  '^(([0-9]|[1-9][0-9]|1[0-9]'
                  '{2}|2[0-4][0-9]|25[0-5])\.)'
                  '{3}']

    for reg_item in range_list:
        match = False
        for reg in regex_list:
            if re.match(reg, reg_item):
                match = True
        if not match:
            if len(reg_item) <= 1:

                print(_("No such hosts file."))

            print(_("Bad host name/range : '%s'") % reg_item)
            sys.exit(1)


def validate_port(arg):
    """Check that arg is a valid port.

    :param arg: either a string or an integer.
    :returns: The arg, as an integer.
    :raises: ValueError, if arg is not a valid port.
    """

    if isinstance(arg, str):
        try:
            arg = int(arg)
        except ValueError:
            raise ValueError('Port value %s'
                             ' should be a positive integer'
                             ' in the valid range (0-65535)' % arg)
    elif not isinstance(arg, int):
        raise ValueError('Port value %s should be a positive integer'
                         ' in the valid range (0-65535)' % arg)

    # We need to support both system and user ports (see
    # https://en.wikipedia.org/wiki/Registered_port) because we don't
    # know how the user will have configured their system.
    if arg < 0 or arg > 65535:
        raise ValueError('Port value %s should be a positive integer'
                         ' in the valid range (0-65535)' % arg)

    return arg


def str_to_ascii(in_string):
    """ Coverts unicode string to ascii string
    :param in_string: input string to convert to ascii
    :returns: ASCII encoded string
    """
    if sys.version_info.major == 2:
        return in_string.decode('utf-8').encode('ascii')

    return in_string


def iteritems(dictionary):
    """Iterate over a dictionary's (key, value) pairs using Python 2 or 3.

    :param dictionary: the dictionary to iterate over.
    """

    if sys.version_info.major == 2:
        return dictionary.iteritems()

    return dictionary.items()
