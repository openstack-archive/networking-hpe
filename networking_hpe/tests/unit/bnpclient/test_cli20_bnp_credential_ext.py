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

import importlib
bnp_credential = importlib.import_module('._bnp_credential',
                                         'networking_hpe.'
                                         'bnpclient.bnp_client_ext.'
                                         'bnpcredential')
from networking_hpe.bnpclient.bnp_client_ext import shell
from networking_hpe.tests.unit.bnpclient import test_cli20

import mock
from neutronclient.common import exceptions

import sys


class CLITestV20ExtensionBNPCredentialJSON(test_cli20.CLITestV20Base):

    def setUp(self):
        self._mock_extension_loading()
        super(CLITestV20ExtensionBNPCredentialJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = ('networking_hpe.bnpclient.bnp_client_ext'
                   '.shell')
        contrib = mock.patch(ext_pkg + '.discover_via_entry_points').start()
        contrib.return_value = [("_bnp_credential", bnp_credential)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests bnpcredential commands loaded."""
        bnp_shell = shell.BnpShell('2.0')
        ext_cmd = {
            'credential-list':
            bnp_credential.BnpCredentialList,
            'credential-create':
            bnp_credential.BnpCredentialCreate,
            'credential-delete':
            bnp_credential.BnpCredentialDelete,
            'credential-show':
            bnp_credential.BnpCredentialShow,
            'credential-update':
            bnp_credential.BnpCredentialUpdate}
        for cmd_name, cmd_class in ext_cmd.items():
            found = bnp_shell.command_manager.find_command([cmd_name])
            self.assertEqual(cmd_class, found[0])

    def test_create_bnp_credential_snmpv1(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv1 = {'write_community': 'public'}
        position_names = ['name', 'snmpv1']
        position_values = [name, snmpv1]
        args = [name, '--snmpv1', 'write_community=public']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_bnp_credential_with_mulitple_snmpv1(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv1 = {'write_community': 'public'}
        position_names = ['name', 'snmpv1']
        position_values = [name, snmpv1]
        args = [name, '--snmpv1', 'write_community=public',
                '--snmpv1', 'write_community=public']
        self.assertRaises(exceptions.CommandError, self._test_create_resource,
                          resource, cmd, None, myid, args, position_names,
                          position_values)

    def test_create_bnp_credential_snmpv2c(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv2c = {'write_community': 'public'}
        position_names = ['name', 'snmpv2c']
        position_values = [name, snmpv2c]
        args = [name, '--snmpv2c', 'write_community=public']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_bnp_credential_with_multiple_snmpv2c(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv2c = {'write_community': 'public'}
        position_names = ['name', 'snmpv2c']
        position_values = [name, snmpv2c]
        args = [name, '--snmpv2c', 'write_community=public',
                '--snmpv2', 'write_community=public']
        self.assertRaises(exceptions.CommandError, self._test_create_resource,
                          resource, cmd, None, myid, args, position_names,
                          position_values)

    def test_create_credential_snmpv3_with_auth_protocol_key(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv3 = {'security_name': 'secName',
                  'auth_protocol': 'authProtocol', 'auth_key': 'authKey'}
        position_names = ['name', 'snmpv3']
        position_values = [name, snmpv3]
        args = [name, '--snmpv3',
                'security_name=secName,auth_protocol=authProtocol,'
                'auth_key=authKey']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_credential_snmpv3_with_priv_protocol_key(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv3 = {'security_name': 'secName',
                  'priv_protocol': 'privProtocol', 'priv_key': 'privKey'}
        position_names = ['name', 'snmpv3']
        position_values = [name, snmpv3]
        args = [name, '--snmpv3', 'security_name=secName,'
                'priv_protocol=privProtocol,priv_key=privKey']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_credential_snmpv3_full(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv3 = {'security_name': 'secName', 'auth_protocol': 'authProtocol',
                  'priv_protocol': 'privProtocol', 'priv_key': 'privKey',
                  'auth_key': 'authKey'}
        position_names = ['name', 'snmpv3']
        position_values = [name, snmpv3]
        args = [name, '--snmpv3', 'security_name=secName,'
                'auth_protocol=authProtocol,priv_protocol=privProtocol,'
                'priv_key=privKey,auth_key=authKey']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_credential_with_multiple_snmpv3(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        snmpv3 = {'security_name': 'secName',
                  'auth_protocol': 'authProtocol', 'auth_key': 'authKey'}
        position_names = ['name', 'snmpv3']
        position_values = [name, snmpv3]
        args = [name, '--snmpv3',
                'security_name=secName,auth_protocol=authProtocol,'
                'auth_key=authKey', '--snmpv3',
                'security_name=secName,auth_protocol=authProtocol,'
                'auth_key=authKey']
        self.assertRaises(exceptions.CommandError, self._test_create_resource,
                          resource, cmd, None, myid, args, position_names,
                          position_values)

    def test_create_credential_netconf_ssh_with_user_name_password(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        netconf_ssh = {'user_name': 'userName', 'password': 'Password'}
        position_names = ['name', 'netconf_ssh']
        position_values = [name, netconf_ssh]
        args = [name, '--netconf-ssh', 'user_name=userName,password=Password']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_credential_netconf_ssh_with_key_path(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        netconf_ssh = {'key_path': 'KeyPath'}
        position_names = ['name', 'netconf_ssh']
        position_values = [name, netconf_ssh]
        args = [name, '--netconf-ssh', 'key_path=KeyPath']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_credential_netconf_ssh_full(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        netconf_ssh = {'user_name': 'userName',
                       'password': 'Password', 'key_path': 'KeyPath'}
        position_names = ['name', 'netconf_ssh']
        position_values = [name, netconf_ssh]
        args = [name, '--netconf-ssh',
                'user_name=userName,password=Password,key_path=KeyPath']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_credential_with_multiple_netconf_ssh(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        netconf_ssh = {'user_name': 'userName', 'password': 'Password'}
        position_names = ['name', 'netconf_ssh']
        position_values = [name, netconf_ssh]
        args = [name, '--netconf-ssh', 'user_name=userName,password=Password',
                '--netconf-ssh', 'user_name=userName,password=Password']
        self.assertRaises(exceptions.CommandError, self._test_create_resource,
                          resource, cmd, None, myid, args, position_names,
                          position_values)

    def test_create_credential_netconf_soap_full(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        netconf_soap = {'user_name': 'userName', 'password': 'Password'}
        position_names = ['name', 'netconf_soap']
        position_values = [name, netconf_soap]
        args = [name, '--netconf-soap', 'user_name=userName,password=Password']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_credential_with_multiple_netconf_soap(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpCredName'
        myid = 'myid'
        netconf_soap = {'user_name': 'userName', 'password': 'Password'}
        position_names = ['name', 'netconf_soap']
        position_values = [name, netconf_soap]
        args = [name, '--netconf-soap', 'user_name=userName,password=Password',
                '--netconf-soap', 'user_name=userName,password=Password']
        self.assertRaises(exceptions.CommandError, self._test_create_resource,
                          resource, cmd, None, myid, args, position_names,
                          position_values)

    def test_update_credential_snmpv1(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialUpdate(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = ['--snmpv1', 'write_community=public',
                '--name=bnpCredName', myid]
        updatefields = {'snmpv1': {
            'write_community': 'public'}, 'name': 'bnpCredName'}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_credential_snmpv2c(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialUpdate(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        name = 'bnpCredName'
        args = ['--snmpv2c', 'write_community=public',
                '--name=bnpCredName', myid]
        updatefields = {'snmpv2c': {'write_community': 'public'}, 'name': name}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_credential_snmpv3(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialUpdate(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        name = 'bnpCredName'
        args = ['--snmpv3', 'security_name=secName,auth_protocol=authProtocol,'
                'priv_protocol=privProtocol,priv_key=privKey,auth_key=authKey',
                '--name=bnpCredName', myid]
        snmpv3 = {'security_name': 'secName', 'auth_protocol': 'authProtocol',
                  'priv_protocol': 'privProtocol', 'priv_key': 'privKey',
                  'auth_key': 'authKey'}
        updatefields = {'snmpv3': snmpv3, 'name': name}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_credential_netconf_ssh(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialUpdate(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        name = 'bnpCredName'
        args = ['--netconf-ssh', 'user_name=userName,password=Password,'
                'key_path=KeyPath', '--name=bnpCredName', myid]
        netconf_ssh = {'user_name': 'userName',
                       'password': 'Password', 'key_path': 'KeyPath'}
        updatefields = {'netconf_ssh': netconf_ssh, 'name': name}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_credential_netconf_soap(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialUpdate(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        name = 'bnpCredName'
        args = ['--netconf-soap', 'user_name=userName,password=Password',
                '--name=bnpCredName', myid]
        netconf_soap = {'user_name': 'userName', 'password': 'Password'}
        updatefields = {'netconf_soap': netconf_soap, 'name': name}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_list_credentials(self):
        resources = 'bnp_credentials'
        cmd = bnp_credential.BnpCredentialList(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_list_credentials_pagination(self):
        resources = 'bnp_credentials'
        cmd = bnp_credential.BnpCredentialList(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources_with_pagination(resources, cmd)

    def test_list_credentials_sort(self):
        resources = 'bnp_credentials'
        cmd = bnp_credential.BnpCredentialList(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd,
                                  sort_key=["name", "id"],
                                  sort_dir=["asc", "desc"])

    def test_list_credentials_limit(self):
        resources = 'bnp_credentials'
        cmd = bnp_credential.BnpCredentialList(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, page_size=1000)

    def test_list_credentials_tags(self):
        resources = 'bnp_credentials'
        cmd = bnp_credential.BnpCredentialList(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, tags=['a', 'b'])

    def test_list_credentials_detail_tags(self):
        resources = 'bnp_credentials'
        cmd = bnp_credential.BnpCredentialList(
            test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, detail=True, tags=['a', 'b'])

    def test_show_credential(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialShow(
            test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(resource, cmd, self.test_id,
                                 args, ['id', 'name'])

    def test_delete_credential(self):
        resource = 'bnp_credential'
        cmd = bnp_credential.BnpCredentialDelete(
            test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(resource, cmd, myid, args)
