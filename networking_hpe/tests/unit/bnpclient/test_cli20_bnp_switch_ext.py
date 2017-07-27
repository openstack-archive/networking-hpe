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


from networking_hpe.bnpclient.bnp_client_ext.bnpswitch import (
    _bnp_switch as bnp_switch)
from networking_hpe.bnpclient.bnp_client_ext import shell
from networking_hpe.tests.unit.bnpclient import test_cli20

import mock

import sys


class CLITestV20ExtensionBNPSwitchJSON(test_cli20.CLITestV20Base):

    def setUp(self):
        self._mock_extension_loading()
        super(CLITestV20ExtensionBNPSwitchJSON,
              self).setUp(plurals={'tags': 'tag'})

    def _mock_extension_loading(self):
        ext_pkg = ('networking_hpe.bnpclient.bnp_client_ext.shell')
        contrib = mock.patch(ext_pkg + '.discover_via_entry_points').start()
        contrib.return_value = [("_bnp_switch", bnp_switch)]
        return contrib

    def test_ext_cmd_loaded(self):
        """Tests bnpswitch commands loaded."""
        bnp_shell = shell.BnpShell('2.0')
        ext_cmd = {
            'switch-list':
            bnp_switch.BnpSwitchList,
            'switch-create':
            bnp_switch.BnpSwitchCreate,
            'switch-delete':
            bnp_switch.BnpSwitchDelete,
            'switch-show':
            bnp_switch.BnpSwitchShow,
            'switch-update':
            bnp_switch.BnpSwitchUpdate}
        for cmd_name, cmd_class in ext_cmd.items():
            found = bnp_shell.command_manager.find_command([cmd_name])
            self.assertEqual(cmd_class, found[0])

    def test_create_bnp_switch(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpSwitchName'
        mac_address = '08:00:09:01:02:03'
        ip_address = '10.0.0.1'
        vendor = 'hpe'
        myid = 'myid'
        position_names = ['name', 'ip_address', 'mac_address', 'vendor']
        position_values = [name, ip_address, mac_address, vendor]
        args = [name, ip_address, mac_address, vendor]
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_create_bnp_switch_with_all_options(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchCreate(
            test_cli20.MyApp(sys.stdout), None)
        name = 'bnpSwitchName'
        mac_address = '08:00:09:01:02:03'
        ip_address = '10.0.0.1'
        vendor = 'hpe'
        myid = 'myid'
        position_names = ['name', 'ip_address', 'mac_address', 'vendor',
                          'family', 'disc_proto', 'disc_creds', 'prov_proto',
                          'prov_creds']
        position_values = [name, ip_address, mac_address, vendor,
                           '5900', 'snmpv1', 'credential1', 'snmpv2c',
                           'credential2']
        args = [name, ip_address, mac_address, vendor, '--family', '5900',
                '--disc-proto', 'snmpv1', '--disc-creds', 'credential1',
                '--prov-proto', 'snmpv2c', '--prov-creds', 'credential2']
        self._test_create_resource(
            resource, cmd, None, myid, args, position_names, position_values)

    def test_update_bnp_switch_disc_proto_creds_without_discover(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchUpdate(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid, '--disc-proto', 'disc_pro', '--disc-creds', 'fake_cred']
        updatefields = {'disc_proto': 'disc_pro',
                        'disc_creds': 'fake_cred', 'validate': False}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_bnp_switch_disc_proto_creds_with_discover(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchUpdate(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid, '--disc-proto', 'disc_proto', '--disc-creds',
                'fake_cred', '--rediscover']
        updatefields = {'disc_proto': 'disc_proto',
                        'disc_creds': 'fake_cred', 'rediscover': True,
                        'validate': False}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_bnp_switch_prov_proto_creds_without_discover(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchUpdate(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid, '--prov-proto', 'prov_proto',
                '--prov-creds', 'fake_cred']
        updatefields = {'prov_proto': 'prov_proto',
                        'prov_creds': 'fake_cred', 'validate': False}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_bnp_switch_prov_proto_creds_with_discover(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchUpdate(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid, '--prov-proto', 'prov_proto', '--prov-creds',
                'fake_cred', '--rediscover']
        updatefields = {'prov_proto': 'prov_proto',
                        'prov_creds': 'fake_cred', 'rediscover': True,
                        'validate': False}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_bnp_switch_prov_proto_creds_enable_without_discover(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchUpdate(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid, '--prov-proto', 'prov_proto', '--prov-creds',
                'fake_cred', '--enable', 'True']
        updatefields = {'prov_proto': 'prov_proto',
                        'prov_creds': 'fake_cred', 'enable': 'True',
                        'validate': False}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_update_bnp_switch_prov_proto_creds_enable_with_discover(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchUpdate(test_cli20.MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid, '--prov-proto', 'prov_proto', '--prov-creds',
                'fake_cred', '--enable', 'False', '--rediscover']
        updatefields = {'prov_proto': 'prov_proto',
                        'prov_creds': 'fake_cred', 'enable': 'False',
                        'rediscover': True, 'validate': False}
        self._test_update_resource(resource, cmd, myid, args, updatefields)

    def test_list_bnp_switches(self):
        resources = 'bnp_switches'
        cmd = bnp_switch.BnpSwitchList(test_cli20.MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_show_bnp_switch(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchShow(test_cli20.MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(
            resource, cmd, self.test_id, args, ['id', 'name'])

    def test_delete_bnp_switch(self):
        resource = 'bnp_switch'
        cmd = bnp_switch.BnpSwitchDelete(test_cli20.MyApp(sys.stdout), None)
        my_id = 'my-id'
        args = [my_id]
        self._test_delete_resource(resource, cmd, my_id, args)
