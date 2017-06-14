# Copyright (c) 2015 Hewlett-Packard Enterprise Development, L.P.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""
Command-line interface to the BNP Switch APIs
"""
from __future__ import print_function

import itertools
import sys

from cliff import commandmanager
from neutronclient.common import clientmanager
from neutronclient.common import exceptions as exc
from neutronclient import shell as neutronshell
from oslo_utils import encodeutils
from stevedore import extension as ext


VERSION = '2.0'
NEUTRON_API_VERSION = '2.0'
clientmanager.neutron_client.API_VERSIONS = {
    '2.0': 'networking_hpe.bnpclient.'
           'bnp_client_ext.v2_0.client.Client',
}


COMMANDS = {'2.0': {}}


class BnpShell(neutronshell.NeutronShell):

    def _register_extensions(self, version):
        for name, module in itertools.chain(
                discover_via_entry_points()):
            self._extend_shell_commands(name, module, version)

    def __init__(self, apiversion):
        super(neutronshell.NeutronShell, self).__init__(
            description=__doc__.strip(),
            version=VERSION,
            command_manager=commandmanager.CommandManager('bnp.cli'), )
        self.commands = COMMANDS
        for k, v in self.commands[apiversion].items():
            self.command_manager.add_command(k, v)
        self._register_extensions(VERSION)
        self.auth_client = None
        self.api_version = apiversion


def discover_via_entry_points():
    emgr = ext.ExtensionManager('bnpclient.extension',
                                invoke_on_load=False)
    return ((ext.name, ext.plugin) for ext in emgr)


def main(argv=sys.argv[1:]):
    try:
        return BnpShell(NEUTRON_API_VERSION).run(list(map(
            encodeutils.safe_decode, argv)))
    except exc.NeutronClientException:
        return 1
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
