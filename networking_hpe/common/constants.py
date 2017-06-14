# Copyright 2015 OpenStack Foundation
# Copyright (c) 2016 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# service type constants:

BNP_SWITCH_RESOURCE_NAME = 'bnp_switch'
BNP_CREDENTIAL_RESOURCE_NAME = 'bnp_credential'

NAME = 'name'
TRUNK = 'trunk'
ACCESS = 'access'
BIND_IGNORE = 'bind_ignore'
BIND_SUCCESS = 'bind_success'
BIND_FAILURE = 'bind_failure'
HP_VIF_TYPE = 'hp-ironic'

SUPPORTED_PROTOCOLS = ['snmpv1', 'snmpv2c',
                       'snmpv3', 'netconf_ssh', 'netconf_soap']
SUPPORTED_AUTH_PROTOCOLS = [None, 'md5', 'sha', 'sha1']
SUPPORTED_PRIV_PROTOCOLS = [None, 'des', '3des', 'aes',
                            'des56', 'aes128', 'aes192', 'aes256']

SNMP_V1 = 'snmpv1'
SNMP_V2C = 'snmpv2c'
SNMP_V3 = 'snmpv3'
SNMP_PORT = 161
PHY_PORT_TYPE = '6'
SNMP_NO_SUCH_INSTANCE = 'No Such'

NETCONF_SSH = 'netconf_ssh'
NETCONF_SOAP = 'netconf_soap'

OID_MAC_ADDRESS = '1.0.8802.1.1.2.1.3.2.0'
OID_IF_INDEX = '1.3.6.1.2.1.2.2.1.1'
OID_PORTS = '1.3.6.1.2.1.2.2.1.2'
OID_IF_TYPE = '1.3.6.1.2.1.2.2.1.3'
OID_PORT_STATUS = '1.3.6.1.2.1.2.2.1.8'
OID_VLAN_CREATE = '1.3.6.1.2.1.17.7.1.4.3.1.5'
OID_VLAN_EGRESS_PORT = '1.3.6.1.2.1.17.7.1.4.3.1.2'
OID_SYS_NAME = '1.3.6.1.2.1.1.5.0'
PROTOCOL_SNMP = 'snmp'
PORT_STATUS = {'1': 'UP',
               '2': 'DOWN',
               '3': 'TESTING',
               '4': 'UNKNOWN',
               '5': 'DORMANT',
               '6': 'NOTPRESENT',
               '7': 'LOWERLAYERDOWN'}

PORT_PROVISIONING_STATUS = {'enable': 'ENABLED',
                            'disable': 'DISABLED'}
SUCCESS = 'Success'
REQUEST_TIMED_OUT = 'Request Timed Out'
NO_DRVR_FOUND = 'No Provisioning driver found for given Vendor/Family/Protocol'
FAMILY = 'family'
DEVICE_NOT_REACHABLE = 'Either device is not reacheable or invalid credentials'
