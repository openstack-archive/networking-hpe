# Copyright (c) 2015 Hewlett-Packard Enterprise Development, L.P.
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

from networking_hpe.common import constants
from networking_hpe.common import exceptions

import struct

from oslo_config import cfg
from oslo_log import log as logging
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp import error as snmp_error
from pysnmp.proto import rfc1902

LOG = logging.getLogger(__name__)

Auth_protocol = {None: cmdgen.usmNoAuthProtocol,
                 'md5': cmdgen.usmHMACMD5AuthProtocol,
                 'sha': cmdgen.usmHMACSHAAuthProtocol}

Priv_protocol = {None: cmdgen.usmNoPrivProtocol,
                 'des': cmdgen.usmDESPrivProtocol,
                 'des56': cmdgen.usmDESPrivProtocol,
                 '3des': cmdgen.usm3DESEDEPrivProtocol,
                 'aes': cmdgen.usmAesCfb128Protocol,
                 'aes128': cmdgen.usmAesCfb128Protocol,
                 'aes192': cmdgen.usmAesCfb192Protocol,
                 'aes256': cmdgen.usmAesCfb256Protocol}


class SNMPClient(object):

    """SNMP client object.

    """
    def __init__(self, ip_address, access_protocol,
                 write_community=None, security_name=None,
                 auth_protocol=None, auth_key=None,
                 priv_protocol=None, priv_key=None):
        self.conf = cfg.CONF
        self.ip_address = ip_address
        self.access_protocol = access_protocol
        self.timeout = cfg.CONF.default.snmp_timeout
        self.retries = cfg.CONF.default.snmp_retries
        if self.access_protocol == constants.SNMP_V3:
            self.security_name = security_name
            self.auth_protocol = Auth_protocol[auth_protocol]
            self.auth_key = auth_key
            self.priv_protocol = Priv_protocol[priv_protocol]
            self.priv_key = priv_key
        else:
            self.write_community = write_community
        self.cmd_gen = cmdgen.CommandGenerator()

    def _get_auth(self):
        """Return the authorization data for an SNMP request.

        """
        if self.access_protocol == constants.SNMP_V3:
            return cmdgen.UsmUserData(self.security_name,
                                      authKey=self.auth_key,
                                      privKey=self.priv_key,
                                      authProtocol=self.auth_protocol,
                                      privProtocol=self.priv_protocol)
        else:
            mp_model = 1 if self.access_protocol == constants.SNMP_V2C else 0
            return cmdgen.CommunityData(self.write_community,
                                        mpModel=mp_model)

    def _get_transport(self):
        """Return the transport target for an SNMP request.

        """
        return cmdgen.UdpTransportTarget(
            (self.ip_address, constants.SNMP_PORT),
            timeout=self.timeout,
            retries=self.retries)

    def get(self, oid):
        """Use PySNMP to perform an SNMP GET operation on a single object.

        """
        try:
            results = self.cmd_gen.getCmd(self._get_auth(),
                                          self._get_transport(),
                                          oid)
        except snmp_error.PySnmpError as e:
            raise exceptions.SNMPFailure(operation="GET", error=e)

        error_indication, error_status, error_index, var_binds = results

        if error_indication:
            raise exceptions.SNMPFailure(operation="GET",
                                         error=error_indication)

        if error_status:
            raise exceptions.SNMPFailure(operation="GET",
                                         error=error_status.prettyPrint())

        return var_binds

    def get_bulk(self, *oids):
        try:
            results = self.cmd_gen.bulkCmd(self._get_auth(),
                                           self._get_transport(),
                                           0, 52,
                                           *oids
                                           )
        except snmp_error.PySnmpError as e:
            raise exceptions.SNMPFailure(operation="GET_BULK", error=e)

        error_indication, error_status, error_index, var_binds = results

        if error_indication:
            raise exceptions.SNMPFailure(operation="GET_BULK",
                                         error=error_indication)

        if error_status:
            raise exceptions.SNMPFailure(operation="GET_BULK",
                                         error=error_status.prettyPrint())

        return var_binds

    def set(self, oid, value):
        """Use PySNMP to perform an SNMP SET operation on a single object.

        :param oid: The OID of the object to set.
        :param value: The value of the object to set.
        :raises: SNMPFailure if an SNMP request fails.
        """
        try:
            # oid = tuple(map(string.atoi, string.split(oid, '.')[1:]))
            results = self.cmd_gen.setCmd(self._get_auth(),
                                          self._get_transport(),
                                          (oid, value))
        except Exception as e:
            raise exceptions.SNMPFailure(operation="SET", error=e)
        except snmp_error.PySnmpError as e:
            raise exceptions.SNMPFailure(operation="SET", error=e)

        error_indication, error_status, error_index, var_binds = results
        if error_indication:
            # SNMP engine-level error.
            raise exceptions.SNMPFailure(operation="SET",
                                         error=error_indication)

        if error_status:
            # SNMP PDU error.
            raise exceptions.SNMPFailure(operation="SET",
                                         error=error_status.prettyPrint())

    def get_rfc1902_integer(self, value):
        return rfc1902.Integer32(value)

    def get_rfc1902_octet_string(self, value):
        return rfc1902.OctetString(value)

    def get_bit_map_for_add(self, val, egress_byte):
        ifindex = val
        byte_index = int(ifindex - 1) / 8
        bit_index = int(ifindex) % 8
        if bit_index == 0:
            bit_index = 8
        target_byte = egress_byte[byte_index]
        mask = 0x80
        if bit_index >= 1:
            mask = ((mask & 0xFF) >> (bit_index - 1))
            target_byte = int('%x' % ord(target_byte), base=16)
            target_byte = ((target_byte) | mask)
            egress_byte = list(egress_byte)
            hex_repr = []
            while target_byte:
                hex_repr.append(struct.pack('B', target_byte & 255))
                target_byte >>= 8
        egress_byte[byte_index] = hex_repr[0]
        return egress_byte

    def get_bit_map_for_del(self, val, egress_byte):
        ifindex = val
        byte_index = int(ifindex - 1) / 8
        bitindex = int(ifindex) % 8
        if bitindex == 0:
            bitindex = 8
        target_byte = egress_byte[byte_index]
        mask = 0x80
        if bitindex > 1:
            mask = ((mask & 0xFF) >> (bitindex - 1))
        mask = ~ mask
        target_byte = int('%x' % ord(target_byte), base=16)
        target_byte = ((target_byte) & mask)
        egress_byte = list(egress_byte)
        hex_repr = []
        hex_repr.append(struct.pack('B', target_byte & 255))
        egress_byte[byte_index] = hex_repr[0]
        return egress_byte


def get_client(snmp_info):
    """Create and return an SNMP client object.

    """
    return SNMPClient(snmp_info['ip_address'],
                      snmp_info['management_protocol'],
                      snmp_info['write_community'],
                      snmp_info['security_name'],
                      snmp_info['auth_protocol'],
                      snmp_info['auth_key'],
                      snmp_info['priv_protocol'],
                      snmp_info['priv_key']
                      )
