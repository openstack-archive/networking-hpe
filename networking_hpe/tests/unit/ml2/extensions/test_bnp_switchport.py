# Copyright (c) 2016 Hewlett-Packard Enterprise Development, L.P.
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

from neutron_lib import context

from neutron.tests.unit.db import test_db_base_plugin_v2 as test_plugin
from neutron.tests.unit import testlib_api

from networking_hpe.db import bm_nw_provision_db as db
from networking_hpe.ml2.extensions import bnp_switchport


class TestBnpSwitchPort(test_plugin.NeutronDbPluginV2TestCase,
                        testlib_api.WebTestCase):

    def setUp(self):
        super(TestBnpSwitchPort, self).setUp()
        self.bnp_wsgi_controller = bnp_switchport.BNPSwitchPortController()
        self.ctx = context.get_admin_context()

    def test_list_switch_port(self):
        self.data = {'vendor': "hpe",
                     'name': "switch1",
                     'family': "hp5900",
                     'management_protocol': "snmpv1",
                     'port_provisioning': "ENABLED",
                     'mac_address': "44:31:92:61:89:d2",
                     'credentials': "cred1",
                     'ip_address': "105.0.1.109",
                     'validation_result': "success"}
        self.mapping_dict = {'neutron_port_id': "24",
                             'switch_port_name': "TenGigabitEthernet",
                             'lag_id': None,
                             'access_type': "access",
                             'segmentation_id': 3,
                             'bind_status': 0,
                             'ifindex': "8"}
        sw = db.add_bnp_phys_switch(self.ctx, self.data)
        self.mapping_dict['switch_id'] = sw['id']
        db.add_bnp_switch_port_map(self.ctx, self.mapping_dict)
        db.add_bnp_neutron_port(self.ctx, self.mapping_dict)
        list_req = self.new_list_request('bnp-switch-ports')
        result = self.bnp_wsgi_controller.index(list_req)
        result = result.pop('bnp_switch_ports')
        self.assertEqual(1, len(result))
