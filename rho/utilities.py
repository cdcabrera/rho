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
from rho.translation import get_translation

CREDENTIALS_PATH = 'data/credentials'
PROFILES_PATH = 'data/profiles'


def ensure_config_dir_exists():
    """Ensure the Rho configuration directory exists."""

    if not os.path.exists('data'):
        os.makedirs('data')


_ = get_translation()


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
        arg = int(arg)
    elif not isinstance(arg, int):
        raise ValueError('Port %s not of recognized type '
                         '(should be string or int)' % arg)

    # We need to support both system and user ports (see
    # https://en.wikipedia.org/wiki/Registered_port) because we don't
    # know how the user will have configured their system.
    if arg < 0 or arg > 65535:
        raise ValueError('Port %s not in valid range (0-65535)' % arg)

    return arg


def str_to_ascii(in_string):
    """ Coverts unicode string to ascii string
    :param in_string: input string to convert to ascii
    :returns: ASCII encoded string
    """
    return in_string.decode('utf-8').encode('ascii')
