# Copyright (c) 2015 OpenStack Foundation.
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

import mock
from oslo_config import cfg

from neutron.tests import base

from neutron_lib.api.definitions import portbindings

from networking_hpe.common import constants as hp_const
from networking_hpe.db import bm_nw_provision_db as db
from networking_hpe.db import bm_nw_provision_models as models
from networking_hpe.ml2 import mechanism_hpe as hpe_mech


CONF = cfg.CONF


class TestHPEMechDriver(base.BaseTestCase):
    """Test class for mech driver."""

    def setUp(self):
        super(TestHPEMechDriver, self).setUp()
        self.driver = hpe_mech.HPEMechanismDriver()

    def _get_port_context(self, tenant_id, net_id, vm_id, network):
        """Get port context."""
        port = {'device_id': vm_id,
                'device_owner': 'compute',
                'binding:host_id': 'ironic',
                'name': 'test-port',
                'tenant_id': tenant_id,
                'id': 123456,
                'network_id': net_id,
                'binding:profile':
                {'local_link_information': [{'switch_id': '11:22:33:44:55:66',
                                             'port_id': 'Tengig0/1'}]},
                'binding:vnic_type': 'baremetal',
                'admin_state_up': True,
                }
        return FakePortContext(port, port, network)

    def _get_network_context(self, tenant_id, net_id, seg_id, shared):
        """Get network context."""
        network = {'id': net_id,
                   'tenant_id': tenant_id,
                   'name': 'test-net',
                   'shared': shared}
        network_segments = [{'segmentation_id': seg_id}]
        return FakeNetworkContext(network, network_segments, network)

    def _get_port_dict(self):
        """Get port dict."""
        port_dict = {'port':
                     {'segmentation_id': 1001,
                      'host_id': 'ironic',
                      'access_type': hp_const.ACCESS,
                      'switchports':
                      [{'port_id': 'Tengig0/1',
                          'switch_id': '11:22:33:44:55:66'}],
                      'id': 123456,
                      'network_id': "net1-id",
                      'is_lag': False}}
        return port_dict

    def test_create_port_precommit(self):
        """Test create_port_precommit method."""
        tenant_id = 'ten-1'
        network_id = 'net1-id'
        segmentation_id = 1001
        vm_id = 'vm1'
        bnp_phys_port = self._get_port_dict()
        bnp_phys_switch = models.BNPPhysicalSwitch
        bnp_phys_switch.port_prov = 'ENABLED'
        network_context = self._get_network_context(tenant_id,
                                                    network_id,
                                                    segmentation_id,
                                                    False)
        port_context = self._get_port_context(tenant_id,
                                              network_id, vm_id,
                                              network_context)
        with mock.patch.object(hpe_mech.HPEMechanismDriver,
                              '_is_port_of_interest',
                              return_value=True), \
                mock.patch.object(hpe_mech.HPEMechanismDriver,
                                  '_construct_port',
                                  return_value=self._get_port_dict()), \
                mock.patch.object(db, 'get_subnets_by_network',
                                  return_value=["subnet"]), \
                mock.patch.object(db, 'get_bnp_phys_switch_by_mac',
                                  return_value=bnp_phys_switch), \
                mock.patch.object(hpe_mech.HPEMechanismDriver,
                                  '_create_port',
                                  return_value=bnp_phys_port):
            self.driver.create_port_precommit(port_context)

    def test_delete_port_precommit(self):
        """Test delete_port_precommit method."""
        tenant_id = 'ten-1'
        network_id = 'net1-id'
        segmentation_id = 1001
        vm_id = 'vm1'
        network_context = self._get_network_context(tenant_id,
                                                    network_id,
                                                    segmentation_id,
                                                    False)

        port_context = self._get_port_context(tenant_id,
                                              network_id,
                                              vm_id,
                                              network_context)
        with mock.patch.object(hpe_mech.HPEMechanismDriver,
                               '_get_vnic_type',
                               return_value=portbindings.VNIC_BAREMETAL):
            self.driver.delete_port_precommit(port_context)

    def test__get_binding_profile(self):
        """Test _get_binding_profile method."""
        tenant_id = 'ten-1'
        network_id = 'net1-id'
        segmentation_id = 1001
        vm_id = 'vm1'
        network_context = self._get_network_context(tenant_id,
                                                    network_id,
                                                    segmentation_id,
                                                    False)

        port_context = self._get_port_context(tenant_id,
                                              network_id,
                                              vm_id,
                                              network_context)
        fake_profile = {'local_link_information':
                        [{'switch_id': '11:22:33:44:55:66',
                          'port_id': 'Tengig0/1'}]}
        profile = self.driver._get_binding_profile(port_context)
        self.assertEqual(profile, fake_profile)

    def test__get_vnic_type(self):
        """Test _get_binding_profile method."""
        tenant_id = 'ten-1'
        network_id = 'net1-id'
        segmentation_id = 1001
        vm_id = 'vm1'
        network_context = self._get_network_context(tenant_id,
                                                    network_id,
                                                    segmentation_id,
                                                    False)

        port_context = self._get_port_context(tenant_id,
                                              network_id,
                                              vm_id,
                                              network_context)
        vnic_type = self.driver._get_vnic_type(port_context)
        self.assertEqual(vnic_type, 'baremetal')


class FakeNetworkContext(object):
    """To generate network context for testing purposes only."""

    def __init__(self, network, segments=None, original_network=None):
        self._network = network
        self._original_network = original_network
        self._segments = segments

    @property
    def current(self):
        return self._network

    @property
    def original(self):
        return self._original_network

    @property
    def network_segments(self):
        return self._segments


class FakePortContext(object):
    """To generate port context for testing purposes only."""

    def __init__(self, port, original_port, network):
        self._port = port
        self._original_port = original_port
        self._network_context = network

    @property
    def current(self):
        port = {'device_id': '',
                'device_owner': 'compute',
                'binding:host_id': '',
                'name': 'test-port',
                'tenant_id': '',
                'id': 123456,
                'network_id': '',
                'binding:profile':
                {'local_link_information': [{'switch_id': '11:22:33:44:55:66',
                                             'port_id': 'Tengig0/1'}]},
                'binding:vnic_type': 'baremetal',
                'admin_state_up': True,
                }
        return port

    @property
    def original(self):
        return self._original_port

    @property
    def network(self):
        return self._network_context
