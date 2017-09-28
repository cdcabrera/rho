#
# Copyright (c) 2009-2016 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

# pylint: disable=too-few-public-methods

""" AuthClearCommand is for removing a specific or all
existing authentication credentials.
"""

from __future__ import print_function
import os
import sys
from rho import utilities
from rho.clicommand import CliCommand
from rho.vault import get_vault
from rho.translation import _


class AuthClearCommand(CliCommand):
    """
    This command is for removing a specific
    or all existing auths.
    """

    def __init__(self):
        usage = _("usage: %prog auth clear")
        shortdesc = _("clears out the credentials")
        desc = _("clears out the crendentials")

        CliCommand.__init__(self, "auth clear", usage, shortdesc, desc)

        self.parser.add_option("--name", dest="name", metavar="NAME",
                               help=_("NAME of the auth "
                                      "credential to be removed"))
        self.parser.add_option("--all", dest="all", action="store_true",
                               help=_("remove ALL auth credentials"))
        self.parser.add_option("--vault", dest="vaultfile", metavar="VAULT",
                               help=_("file containing vault password for"
                                      " scripting"))

    def _validate_options(self):
        CliCommand._validate_options(self)

        if not self.options.name and not self.options.all:
            print(_('You must provide either "--all" or a value for '
                    '"--name".'))
            self.parser.print_help()
            sys.exit(1)

        if self.options.name and self.options.all:
            print(_('You must provide either "--all" or a value for '
                    '"--name". You cannot supply both.'))
            self.parser.print_help()
            sys.exit(1)

    def _do_command(self):
        if self.options.name:
            auth_found = False
            vault = get_vault(self.options.vaultfile)
            if os.path.isfile(utilities.CREDENTIALS_PATH):
                cred_list = vault.load_as_json(utilities.CREDENTIALS_PATH)
                for index, cred in enumerate(cred_list):
                    if cred.get('name') == self.options.name:
                        del cred_list[index]
                        print(_('Auth "%s" was removed' % self.options.name))
                        auth_found = True
                        break
                if not auth_found:
                    print(_('Auth "%s" was not found' % self.options.name))
                    sys.exit(1)
                vault.dump_as_json_to_file(
                    cred_list, utilities.CREDENTIALS_PATH)
            else:
                print(_("All authorization credentials removed"))

        elif self.options.all:
            if os.path.isfile(utilities.CREDENTIALS_PATH):
                os.remove(utilities.CREDENTIALS_PATH)

            print(_("All authorization credentials removed"))
