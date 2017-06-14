# Copyright (c) 2015 Hewlett-Packard Enterprise Development, L.P.
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

from networking_hpe.common import constants as hp_const
from networking_hpe.common import exceptions
from networking_hpe.common import snmp_client
from networking_hpe.drivers import (snmp_provisioning_driver as prov_driver)

from neutron.tests import base

from pysnmp.proto import rfc1902


class TestSnmpDriver(base.BaseTestCase):

    def setUp(self):
        super(TestSnmpDriver, self).setUp()
        self.snmp_info = {'ip_address': '00.00.00.00',
                          'management_protocol': hp_const.SNMP_V3,
                          'access_protocol': 'snmpv1',
                          'write_community': 'public',
                          'security_name': 'user_name',
                          'auth_key': 'halo1234',
                          'priv_key': 'test1234',
                          'auth_protocol': 'md5',
                          'priv_protocol': 'des56'}
        self.driver = prov_driver.SNMPProvisioningDriver()

    def test_delete_isolation(self):
        self.port = self._get_port_payload()
        self.client = snmp_client.get_client(self.snmp_info)
        egress_byte = []
        prov_driver_instance = prov_driver.SNMPProvisioningDriver
        with mock.patch.object(snmp_client, 'get_client',
                               return_value=self.client), \
                mock.patch.object(snmp_client.SNMPClient, 'set',
                                  return_value=None), \
                mock.patch.object(prov_driver_instance,
                                  '_get_device_nibble_map',
                                  return_value=None), \
                mock.patch.object(snmp_client.SNMPClient,
                                  'get_bit_map_for_del',
                                  return_value=egress_byte):
            self.driver.delete_isolation(self.port)

    def test_delete_isolation_exception(self):
        self.port = self._get_port_payload()
        self.client = snmp_client.get_client(self.snmp_info)
        egress_byte = []
        with mock.patch.object(snmp_client, 'get_client',
                               return_value=self.client), \
                mock.patch.object(prov_driver.SNMPProvisioningDriver,
                                  '_snmp_get',
                                  return_value=None), \
                mock.patch.object(prov_driver.SNMPProvisioningDriver,
                                  '_get_device_nibble_map',
                                  return_value=None), \
                mock.patch.object(snmp_client.SNMPClient,
                                  'get_bit_map_for_del',
                                  return_value=egress_byte), \
                mock.patch.object(snmp_client.SNMPClient, 'set',
                                  side_effect=exceptions.SNMPFailure):
            self.assertRaises(exceptions.SNMPFailure,
                              self.driver.delete_isolation,
                              self.port)

    def test_set_isolation(self):
        self.port = self._get_port_payload()
        self.client = snmp_client.get_client(self.snmp_info)
        egress_byte = []
        prov_driver_instance = prov_driver.SNMPProvisioningDriver
        with mock.patch.object(snmp_client, 'get_client',
                              return_value=self.client), \
            mock.patch.object(prov_driver_instance, '_snmp_get',
                              return_value=None), \
            mock.patch.object(snmp_client.SNMPClient, 'set',
                              return_value=None), \
            mock.patch.object(prov_driver_instance,
                              '_get_device_nibble_map',
                              return_value=None), \
            mock.patch.object(snmp_client.SNMPClient,
                              'get_bit_map_for_add',
                              return_value=egress_byte):
            self.driver.set_isolation(self.port)

    def test_set_isolation_exception(self):
        self.port = self._get_port_payload()
        # print repr(self.snmp_info)
        self.client = snmp_client.get_client(self.snmp_info)
        with mock.patch.object(snmp_client, 'get_client',
                               return_value=self.client), \
                mock.patch.object(prov_driver.SNMPProvisioningDriver,
                                  '_snmp_get', return_value=None), \
                mock.patch.object(snmp_client.SNMPClient, 'set',
                                  side_effect=exceptions.SNMPFailure):
            self.assertRaises(exceptions.SNMPFailure,
                              self.driver.set_isolation,
                              self.port)

    def test__get_device_nibble_map(self):
        self.client = snmp_client.get_client(self.snmp_info)
        seg_id = 1001
        egrs_oid = hp_const.OID_VLAN_EGRESS_PORT + '.' + str(seg_id)
        varbinds = [(rfc1902.ObjectName('1.3.6.1.2.1.17.7.1.4.3.1.2.1001'),
                     rfc1902.OctetString(hexValue='80'))]
        with mock.patch.object(snmp_client.SNMPClient, 'get',
                               return_value=varbinds):
            egbytes = self.driver._get_device_nibble_map(self.client, egrs_oid)
        self.assertEqual(egbytes, b'\x80')

    def _get_port_payload(self):
        """Get port payload for processing requests."""
        port_dict = {'port':
                     {'segmentation_id': '1001',
                      'ifindex': '1',
                      'host_id': 'ironic',
                      'access_type': hp_const.ACCESS,
                      'credentials': self._get_credentials_dict(),
                      'switchports':
                      [{'port_id': 'Ten-GigabitEthernet1/0/35',
                        'ifindex': '1',
                          'switch_id': '44:31:92:61:89:d2'}],
                      'id': '321f506f-5f0d-435c-9c23-c2a11f78c3e3',
                      'network_id': 'net-id',
                      'is_lag': False}}
        return port_dict

    def _get_credentials_dict(self):
        creds_dict = {}
        creds_dict['ip_address'] = "1.1.1.1"
        creds_dict['write_community'] = 'public'
        creds_dict['security_name'] = 'test'
        creds_dict['security_level'] = 'test'
        creds_dict['auth_protocol'] = 'md5'
        creds_dict['access_protocol'] = 'test1'
        creds_dict['auth_key'] = 'test'
        creds_dict['priv_protocol'] = 'aes'
        creds_dict['priv_key'] = 'test_priv'
        creds_dict['management_protocol'] = hp_const.SNMP_V3
        return creds_dict
