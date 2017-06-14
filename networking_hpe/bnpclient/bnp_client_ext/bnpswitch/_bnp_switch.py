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

from neutronclient.common import extension
from neutronclient.neutron import v2_0 as neutronV20

from networking_hpe.common import constants as const


class BnpSwitch(extension.NeutronClientExtension):
    resource = const.BNP_SWITCH_RESOURCE_NAME
    resource_plural = '%ses' % resource
    path = 'bnp-switches'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class BnpSwitchCreate(extension.ClientExtensionCreate, BnpSwitch):
    """Create Physical Switch information."""
    shell_command = 'switch-create'

    def add_known_arguments(self, parser):

        parser.add_argument('name', metavar='NAME',
                            help=_('Name of the physical switch.'))
        parser.add_argument('ip_address', metavar='IP_ADDRESS',
                            help=_('IP address of the physical switch.'))
        parser.add_argument('mac_address', metavar='MAC_ADDRESS',
                            help=_('MAC address of the physical switch.'))
        parser.add_argument('vendor', metavar='VENDOR',
                            help=_('Vendor of the physical switch.'))
        parser.add_argument('--family',
                            metavar='FAMILY',
                            help=_('Family of the physical switch.'))
        parser.add_argument('--management-protocol',
                            metavar='MANAGEMENT_PROTOCOL',
                            help=_('Management protocol of the physical'
                                   ' switch.'))
        parser.add_argument('--credentials',
                            metavar='CREDS',
                            help=_('Credential of the physical'
                                   ' switch.'))

    def args2body(self, parsed_args):

        body = {
            const.BNP_SWITCH_RESOURCE_NAME: {
                'name': parsed_args.name,
                'ip_address': parsed_args.ip_address,
                'vendor': parsed_args.vendor,
                'mac_address': parsed_args.mac_address}}

        neutronV20.update_dict(parsed_args, body[
                               const.BNP_SWITCH_RESOURCE_NAME], [
                               'family', 'management_protocol',
                               'credentials'])
        return body


class BnpSwitchList(extension.ClientExtensionList, BnpSwitch):
    """List all physical switch information."""

    shell_command = 'switch-list'
    allow_names = True
    list_columns = ['id', 'name', 'ip_address',
                    'mac_address', 'vendor', 'family', 'port_provisioning',
                    'management_protocol', 'credentials', 'validation_result']
    pagination_support = True
    sorting_support = True


class BnpSwitchShow(extension.ClientExtensionShow, BnpSwitch):
    """Show the physical switch information."""

    shell_command = 'switch-show'
    allow_names = True


class BnpSwitchDelete(extension.ClientExtensionDelete, BnpSwitch):
    """Delete the physical switch."""

    shell_command = 'switch-delete'
    allow_names = True


class BnpSwitchUpdate(extension.ClientExtensionUpdate, BnpSwitch):
    """Update the physical switch information."""

    shell_command = 'switch-update'
    allow_names = True

    def add_known_arguments(self, parser):

        parser.add_argument('--vendor', metavar='VENDOR',
                            help=_('Vendor of the physical switch.'))
        parser.add_argument('--mac-address', metavar='MAC_ADDRESS',
                            help=_('MAC address of the physical switch.'))
        parser.add_argument('--family',
                            metavar='FAMILY',
                            help=_('Family of the physical switch.'))
        parser.add_argument('--port-provisioning',
                            metavar='{ENABLED, DISABLED}',
                            help=_('Port Provisioning status of '
                                   ' the physical switch.'))
        parser.add_argument('--management-protocol',
                            metavar='MANAGEMENT_PROTOCOL',
                            help=_('Management protocol of the physical'
                                   ' switch.'))
        parser.add_argument('--credentials',
                            metavar='CREDS',
                            help=_('Credential of the physical'
                                   ' switch.'))
        parser.add_argument('--validate', action='store_true',
                            help=_('validate the given credentials based on'
                                   ' protocol.'))

    def args2body(self, parsed_args):

        body = {const.BNP_SWITCH_RESOURCE_NAME: {}}
        neutronV20.update_dict(parsed_args, body[
                               const.BNP_SWITCH_RESOURCE_NAME], [
                               'name', 'vendor', 'mac_address',
                               'family', 'port_provisioning',
                               'management_protocol',
                               'credentials', 'validate'])
        return body
