# Copyright (c) 2016 Hewlett-Packard Enterprise Development, L.P.
# All Rights Reserved.
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

from neutronclient.common import exceptions
from neutronclient.common import extension
from neutronclient.common import utils

from networking_hpe.common import constants as const

meta_snmpv1_v2 = 'write_community=WRITE_COMMUNITY'
meta_snmpv3 = ('security_name=SECURITY_NAME,'
               'auth_protocol=AUTH_PROTOCOL,'
               'priv_protocol=PRIV_PROTOCOL,'
               'auth_key=AUTH_KEY,'
               'priv_key=PRIV_KEY')
meta_netconf_ssh = ('user_name=USER_NAME,'
                    'password=PASSWORD,'
                    'key_path=KEY_PATH')
meta_netconf_soap = ('user_name=USER_NAME,'
                     'password=PASSWORD')


def check_multiple_args(args, attribute):
    if len(args) > 1:
        raise exceptions.CommandError(_('Attribute \'%s\' given'
                                        ' multiple times') % attribute)


class BnpCredential(extension.NeutronClientExtension):
    resource = const.BNP_CREDENTIAL_RESOURCE_NAME
    resource_plural = '%ss' % resource
    path = 'bnp-credentials'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class UpdateCredentialSnmpNetconfMixin(object):

    def add_arguments_snmp_netconf(self, parser):
        group_snmp_netconf = parser.add_mutually_exclusive_group()
        group_snmp_netconf.add_argument('--snmpv1',
                                        metavar=meta_snmpv1_v2,
                                        action='append',
                                        type=utils.str2dict_type(
                                            optional_keys=['write_community']),
                                        dest='snmpv1', help=_('SNMPV1 access '
                                                              'credentials for'
                                                              ' physical'
                                                              ' switch.')
                                        )
        group_snmp_netconf.add_argument('--snmpv2c',
                                        metavar=meta_snmpv1_v2,
                                        action='append', dest='snmpv2c',
                                        type=utils.str2dict_type(
                                            optional_keys=['write_community']),
                                        help=_('SNMPV2c access credentials'
                                               ' for physical switch.'))
        group_snmp_netconf.add_argument('--snmpv3', metavar=meta_snmpv3,
                                        action='append', dest='snmpv3',
                                        type=utils.str2dict_type(
                                            optional_keys=[
                                                'security_name',
                                                'auth_protocol',
                                                'priv_protocol', 'auth_key',
                                                'priv_key']),
                                        help=_('SNMPV3 access credentials for'
                                               ' physical switch.'))
        group_snmp_netconf.add_argument('--netconf-ssh',
                                        metavar=meta_netconf_ssh,
                                        action='append', dest='netconf_ssh',
                                        type=utils.str2dict_type(
                                            optional_keys=['user_name',
                                                           'password',
                                                           'key_path']),
                                        help=_('NETCONF-SSH access credentials'
                                               ' for physical switch.'
                                               ' Absolute path has to be pro'
                                               'vided for key_path.'))

        group_snmp_netconf.add_argument('--netconf-soap',
                                        metavar=meta_netconf_soap,
                                        action='append', dest='netconf_soap',
                                        type=utils.str2dict_type(
                                            optional_keys=['user_name',
                                                           'password']),
                                        help=_('NETCONF-SOAP access'
                                               ' credentials for physical'
                                               ' switch.'))

    def args2body_snmp_netconf(self, parsed_args, body):
        if parsed_args.snmpv1:
            check_multiple_args(parsed_args.snmpv1, '--snmpv1')
            body[const.BNP_CREDENTIAL_RESOURCE_NAME]['snmpv1'] = (
                parsed_args.snmpv1[0])
        elif parsed_args.snmpv2c:
            check_multiple_args(parsed_args.snmpv2c, '--snmpv2c')
            body[const.BNP_CREDENTIAL_RESOURCE_NAME]['snmpv2c'] = (
                parsed_args.snmpv2c[0])
        elif parsed_args.snmpv3:
            check_multiple_args(parsed_args.snmpv3, '--snmpv3')
            body[const.BNP_CREDENTIAL_RESOURCE_NAME]['snmpv3'] = (
                parsed_args.snmpv3[0])
        elif parsed_args.netconf_ssh:
            check_multiple_args(parsed_args.netconf_ssh, '--netconf-ssh')
            body[const.BNP_CREDENTIAL_RESOURCE_NAME]['netconf_ssh'] = (
                parsed_args.netconf_ssh[0])
        elif parsed_args.netconf_soap:
            check_multiple_args(parsed_args.netconf_soap, '--netconf-soap')
            body[const.BNP_CREDENTIAL_RESOURCE_NAME]['netconf_soap'] = (
                parsed_args.netconf_soap[0])


class BnpCredentialCreate(extension.ClientExtensionCreate, BnpCredential,
                          UpdateCredentialSnmpNetconfMixin):

    """Create credential for a physical switch."""

    shell_command = 'credential-create'

    def add_known_arguments(self, parser):
        parser.add_argument('name', metavar='CRED_NAME',
                            help=_('credential name'))
        self.add_arguments_snmp_netconf(parser)

    def args2body(self, parsed_args):

        body = {const.BNP_CREDENTIAL_RESOURCE_NAME: {
                'name': parsed_args.name}}
        self.args2body_snmp_netconf(parsed_args, body)
        return body


class BnpCredentialUpdate(extension.ClientExtensionUpdate, BnpCredential,
                          UpdateCredentialSnmpNetconfMixin):

    """Update credential's information of a physical switch."""
    shell_command = 'credential-update'

    def add_known_arguments(self, parser):
        self.add_arguments_snmp_netconf(parser)

    def args2body(self, parsed_args):
        body = {const.BNP_CREDENTIAL_RESOURCE_NAME: {}}
        self.args2body_snmp_netconf(parsed_args, body)
        return body


class BnpCredentialList(extension.ClientExtensionList, BnpCredential):

    """List credential's of a physical switch."""
    shell_command = 'credential-list'
    listcolumns = ['id', 'name', 'type']
    pagination_support = True
    sorting_support = True


class BnpCredentialShow(extension.ClientExtensionShow, BnpCredential):

    """Show credential information of a physical switch."""
    shell_command = 'credential-show'


class BnpCredentialDelete(extension.ClientExtensionDelete, BnpCredential):

    """Delete credential information of a physical switch."""
    shell_command = 'credential-delete'
