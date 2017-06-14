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
from oslo_config import cfg

from networking_hpe.common import constants
from networking_hpe.common import snmp_client
from networking_hpe.ml2 import mechanism_hpe

from neutron.tests import base

from pysnmp.entity.rfc3413.oneliner import cmdgen

CONF = cfg.CONF


class TestSNMPClient(base.BaseTestCase):

    def setUp(self):
        super(TestSNMPClient, self).setUp()
        self.ip_address = '00.00.00.00'
        self.access_protocol = 'snmpv1'
        self.timeout = 3
        self.retries = 5
        self.security_name = 'user_name'
        self.auth_protocol = 'md5'
        self.auth_key = 'test'
        self.priv_protocol = 'des'
        self.priv_key = 'test123'
        self.write_community = 'public'
        CONF.register_opts(mechanism_hpe.param_opts, group='default')
        CONF.set_override('snmp_timeout', 3, 'default')
        CONF.set_override('snmp_retries', 5, 'default')
        self.client = snmp_client.SNMPClient(self.ip_address,
                                             self.access_protocol,
                                             self.write_community)

    def test___init__(self):
        client = snmp_client.SNMPClient(self.ip_address,
                                        self.access_protocol,
                                        self.write_community)
        self.assertEqual(self.ip_address, client.ip_address)
        self.assertEqual(self.access_protocol, client.access_protocol)
        self.assertEqual(self.timeout, client.timeout)
        self.assertEqual(self.retries, client.retries)
        self.assertEqual(self.write_community, client.write_community)

    def test__get_auth_for_v1(self):
        with mock.patch.object(cmdgen, 'CommunityData',
                               return_value=None):
            self.client._get_auth()
            cmdgen.CommunityData.assert_called_once_with(self.write_community,
                                                         mpModel=0)

    def test__get_auth_for_v2(self):
        client = snmp_client.SNMPClient(self.ip_address,
                                        constants.SNMP_V2C,
                                        self.write_community)
        with mock.patch.object(cmdgen, 'CommunityData',
                               return_value=None):
            client._get_auth()
            cmdgen.CommunityData.assert_called_once_with(self.write_community,
                                                         mpModel=1)

    def test__get_auth_for_v3(self):
        client = snmp_client.SNMPClient(self.ip_address,
                                        constants.SNMP_V3,
                                        self.write_community,
                                        self.security_name,
                                        self.auth_protocol,
                                        self.auth_key,
                                        self.priv_protocol,
                                        self.priv_key)
        md5 = cmdgen.usmHMACMD5AuthProtocol
        des = cmdgen.usmDESPrivProtocol
        with mock.patch.object(cmdgen, 'UsmUserData',
                               return_value=None):
            client._get_auth()
            cmdgen.UsmUserData.assert_called_once_with(self.security_name,
                                                       authKey=self.auth_key,
                                                       authProtocol=md5,
                                                       privKey=self.priv_key,
                                                       privProtocol=des)

    def test__get_transport(self):
        with mock.patch.object(cmdgen, 'UdpTransportTarget',
                               return_value=None):
            self.client._get_transport()
            cmdgen.UdpTransportTarget.assert_called_once_with(
                (self.ip_address,
                 constants.SNMP_PORT),
                timeout=self.timeout,
                retries=self.retries)

    def test_get(self):
        result = (0, 0, 0, ('oid', 'value'))
        with mock.patch.object(cmdgen.CommandGenerator,
                               'getCmd',
                               return_value=result),\
                mock.patch.object(snmp_client.SNMPClient,
                                  '_get_auth',
                                  return_value='fake'),\
                mock.patch.object(snmp_client.SNMPClient,
                                  '_get_transport',
                                  return_value='tcp'):
            self.client.get('oid')
            cmdgen.CommandGenerator.getCmd.called

    def test_get_bulk(self):
        result = (0, 0, 0, ('oid', 'value'))
        with mock.patch.object(cmdgen.CommandGenerator,
                               'bulkCmd',
                               return_value=result),\
                mock.patch.object(snmp_client.SNMPClient,
                                  '_get_auth',
                                  return_value='fake'),\
                mock.patch.object(snmp_client.SNMPClient,
                                  '_get_transport',
                                  return_value='tcp'):
            self.client.get_bulk('oid1', 'oid2')
            cmdgen.CommandGenerator.bulkCmd.called
