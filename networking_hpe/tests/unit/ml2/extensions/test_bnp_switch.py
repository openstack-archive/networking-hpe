# Copyright (c) 2014 OpenStack Foundation.
# Copyright (c) 2016 Hewlett-Packard Enterprise Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from neutron.api import extensions
from neutron.common import config
import neutron.extensions
from neutron.plugins.ml2 import config as ml2_config
from neutron.tests.unit.api.v2 import test_base
from neutron.tests.unit.db import test_db_base_plugin_v2 as test_plugin
from neutron.tests.unit import testlib_api

from networking_hpe.ml2.extensions import bnp_switch


TARGET_PLUGIN = 'neutron.plugins.ml2.plugin.Ml2Plugin'
_get_path = test_base._get_path
extensions_path = ':'.join(neutron.extensions.__path__)


class TestBnpSwitches(test_plugin.NeutronDbPluginV2TestCase,
                      testlib_api.WebTestCase):

    fmt = 'json'
    _mechanism_drivers = ['hpe_bnp']
    _ext_drivers = 'bnp_ext_driver'

    def setUp(self):
        super(TestBnpSwitches, self).setUp()
        self.setup_coreplugin(TARGET_PLUGIN)
        ext_mgr = extensions.PluginAwareExtensionManager.get_instance()
        ml2_config.cfg.CONF.set_override('extension_drivers',
                                         self._ext_drivers,
                                         group='ml2')
        ml2_config.cfg.CONF.set_override('mechanism_drivers',
                                         self._mechanism_drivers,
                                         group='ml2')
        app = config.load_paste_app('extensions_test_app')
        self.ext_api = extensions.ExtensionMiddleware(app, ext_mgr=ext_mgr)
        self.bnp_wsgi_controller = bnp_switch.BNPSwitchController()
        self.data = {"bnp_switch":
                     {"access_parameters":
                      {"priv_key": None,
                       "auth_key": None,
                       "write_community": "public",
                       "security_name": None,
                       "auth_protocol": None,
                       "priv_protocol": None},
                      "vendor": "hpe",
                      "ip_address": "1.2.3.4",
                      "access_protocol": "snmpv1"}}
        self.data1 = {"bnp_switch":
                      {"access_parameters":
                       {"priv_key": None,
                        "auth_key": None,
                        "write_community": "private",
                        "security_name": None,
                        "auth_protocol": None,
                        "priv_protocol": None},
                       "vendor": "hpe",
                       "ip_address": "1.1.1.1",
                       "access_protocol": "snmpv2c"}}
        self.bnp_switch_dict = {"mac_address": "44:31:92:dc:2e:c0",
                                "ports": []}
        self.bnp_switch_dict1 = {"mac_address": "11:31:92:aa:2e:c0",
                                 "ports": []}

    '''def _create_switch(self, data, bnp_switch_dict):
        create_req = self.new_create_request('bnp-switches', data, 'json')
        with contextlib.nested(
            mock.patch.object(bnp_switch.BNPSwitchController,
                              '_discover_switch',
                              return_value=bnp_switch_dict),
            mock.patch.object(bnp_switch.BNPSwitchController,
                              '_add_physical_port')):
            result = self.bnp_wsgi_controller.create(create_req)
            bnp_switch.BNPSwitchController._discover_switch.called
            bnp_switch.BNPSwitchController._add_physical_port.called
            return result

    def _update_switch(self, data, switch_id):
        update_req = self.new_update_request('bnp-switches',
                                             data, switch_id)
        self.bnp_wsgi_controller.update(update_req, switch_id)

    def _delete_switch(self, switch_id):
        with mock.patch.object(db, 'get_bnp_switch_port_map_by_switchid',
                              return_value=[]):
            delete_req = self.new_delete_request('bnp-switches',
                                                 switch_id)
            self.bnp_wsgi_controller.delete(delete_req, switch_id)

    def _delete_switch_with_active_mappings(self, switch_id):
        with mock.patch.object(db, 'get_bnp_switch_port_map_by_switchid',
                               return_value=[{'switch_id': switch_id}]):
            delete_req = self.new_delete_request('bnp-switches',
                                                 switch_id)
            self.bnp_wsgi_controller.delete(delete_req, switch_id)

    def _show_switch(self, switch_id):
        ports_list = []
        show_req = self.new_show_request('bnp-switches', switch_id)
        with mock.patch.object(db, 'get_bnp_switch_port_map_by_switchid',
                               return_value=None), \
                mock.patch.object(discovery_driver.SNMPDiscoveryDriver,
                                  'get_ports_status',
                                  return_value=ports_list):
            self.bnp_wsgi_controller.show(show_req, switch_id)
            db.get_bnp_switch_port_map_by_switchid.called
            discovery_driver.SNMPDiscoveryDriver.get_ports_status.called

    def test_create_show_switch(self):
        switch = self._create_switch(self.data, self.bnp_switch_dict)
        switch = switch.pop('bnp_switch')
        switch_id = switch['id']
        self._show_switch(switch_id)

    def test_create_list_switch(self):
        self._create_switch(self.data, self.bnp_switch_dict)
        self._create_switch(self.data1, self.bnp_switch_dict1)
        list_req = self.new_list_request('bnp-switches')
        result = self.bnp_wsgi_controller.index(list_req)
        result = result.pop('bnp_switches')
        self.assertEqual(2, len(result))

    def test_create_update_delete_switch(self):
        switch = self._create_switch(self.data, self.bnp_switch_dict)
        switch_id = switch['bnp_switch']['id']
        data = {"bnp_switch": {"enable": "False"}}
        self._update_switch(data, switch_id)
        self._delete_switch(switch_id)

    def test_update_with_invalid_protocol(self):
        switch = self._create_switch(self.data, self.bnp_switch_dict)
        switch_id = switch['bnp_switch']['id']
        data = {"bnp_switch": {"access_protocol": "snmpv4"}}
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._update_switch, data, switch_id)

    def test_show_invalid_switch(self):
        self._create_switch(self.data, self.bnp_switch_dict)
        switch_id = 'foobar'
        show_req = self.new_show_request('bnp-switches', switch_id)
        self.assertRaises(webob.exc.HTTPNotFound,
                          self.bnp_wsgi_controller.show, show_req,
                          switch_id)

    def test_delete_invalid_switch(self):
        switch_id = 'foobar'
        self.assertRaises(webob.exc.HTTPNotFound,
                          self._delete_switch,
                          switch_id)

    def test_delete_switch_with_mappings(self):
        switch_id = 'foobar'
        self.assertRaises(webob.exc.HTTPConflict,
                          self._delete_switch_with_active_mappings,
                          switch_id)

    def test_create_with_invalid_vendor(self):
        data = self.data
        data['bnp_switch']['vendor'] = 'fake_vendor'
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._create_switch,
                          self.data, self.bnp_switch_dict)

    def test_create_with_same_ipaddress(self):
        self._create_switch(self.data, self.bnp_switch_dict)
        self.assertRaises(webob.exc.HTTPConflict,
                          self._create_switch,
                          self.data, self.bnp_switch_dict)

    def test_update_with_invalid_credentials(self):
        switch = self._create_switch(self.data, self.bnp_switch_dict)
        switch_id = switch['bnp_switch']['id']
        data = {"bnp_switch": {"access_protocol": "snmpv4",
                               "access_parameters": {
                                   "write_community": "public"}}}
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._update_switch, data, switch_id)'''
