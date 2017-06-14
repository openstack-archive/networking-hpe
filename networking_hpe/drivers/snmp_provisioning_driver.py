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

from oslo_log import log as logging

from networking_hpe._i18n import _LE
from networking_hpe.common import constants
from networking_hpe.common import exceptions
from networking_hpe.common import snmp_client
from networking_hpe.drivers import (port_provisioning_driver as driver)


LOG = logging.getLogger(__name__)


class SNMPProvisioningDriver(driver.PortProvisioningDriver):
    """SNMP Facet driver implementation for bare

    metal provisioning.
    """

    def set_isolation(self, port):
        """set_isolation ."""
        try:
            client = snmp_client.get_client(self._get_switch_dict(port))
            seg_id = port['port']['segmentation_id']
            vlan_oid = constants.OID_VLAN_CREATE + '.' + str(seg_id)
            egress_oid = constants.OID_VLAN_EGRESS_PORT + '.' + str(seg_id)
            snmp_response = self._snmp_get(client, vlan_oid)
            no_such_instance_exists = False
            if snmp_response:
                for oid, val in snmp_response:
                    value = val.prettyPrint()
                    if constants.SNMP_NO_SUCH_INSTANCE in value:
                        # Fixed for pysnmp versioning issue
                        no_such_instance_exists = True
                        break
            if not snmp_response or no_such_instance_exists:
                client.set(vlan_oid, client.get_rfc1902_integer(4))
            nibble_byte = self._get_device_nibble_map(client, egress_oid)
            ifindex = self._get_ifindex_for_port(port)
            bit_map = client.get_bit_map_for_add(int(ifindex), nibble_byte)
            bit_list = []
            for line in bit_map:
                bit_list.append(line)
            set_string = client.get_rfc1902_octet_string(''.join(bit_list))
            client.set(egress_oid, set_string)
        except Exception as e:
            LOG.error(_LE("Exception in configuring VLAN '%s' "), e)
            # print 'set isolation exception: ' + repr(e)
            raise exceptions.SNMPFailure(operation="SET", error=e)

    def delete_isolation(self, port):
        """delete_isolation deletes the vlan from the physical ports."""
        try:
            client = snmp_client.get_client(self._get_switch_dict(port))
            seg_id = port['port']['segmentation_id']
            egress_oid = constants.OID_VLAN_EGRESS_PORT + '.' + str(seg_id)
            nibble_byte = self._get_device_nibble_map(client, egress_oid)
            ifindex = port['port']['ifindex']
            bit_map = client.get_bit_map_for_del(int(ifindex), nibble_byte)
            bit_list = []
            for line in bit_map:
                bit_list.append(line)
            set_string = client.get_rfc1902_octet_string(''.join(bit_list))
            client.set(egress_oid, set_string)
            # On port delete removing interface from target vlan,
            #  not deleting global vlan on device
        except Exception as e:
            LOG.error(_LE("Exception in deleting VLAN '%s' "), e)
            raise exceptions.SNMPFailure(operation="SET", error=e)

    def create_lag(self, port):
        """create_lag  creates the link aggregation for the physical ports."""

        pass

    def delete_lag(self, port):
        """delete_lag  delete the link aggregation for the physical ports."""
        pass

    def _get_switch_dict(self, port):
        creds_dict = port['port']['credentials']
        ip_address = creds_dict['ip_address']
        write_community = creds_dict['write_community']
        security_name = creds_dict['security_name']
        auth_protocol = creds_dict['auth_protocol']
        auth_key = creds_dict['auth_key']
        priv_protocol = creds_dict['priv_protocol']
        priv_key = creds_dict['priv_key']
        management_protocol = creds_dict['management_protocol']
        switch_dict = {
            'ip_address': ip_address,
            'management_protocol': management_protocol,
            'write_community': write_community,
            'security_name': security_name,
            'auth_protocol': auth_protocol,
            'auth_key': auth_key,
            'priv_protocol': priv_protocol,
            'priv_key': priv_key}
        return switch_dict

    def _get_device_nibble_map(self, snmp_client_info, egress_oid):
        try:
            var_binds = snmp_client_info.get(egress_oid)
        except exceptions.SNMPFailure as e:
            LOG.error(_LE("Exception in _get_device_nibble_map '%s' "), e)
            return
        for name, val in var_binds:
            value = snmp_client_info.get_rfc1902_octet_string(val)
            egress_bytes = (vars(value)['_value'])
        return egress_bytes

    def _get_ifindex_for_port(self, port):
        switchport = port['port']['switchports']
        if not switchport:
            return
        # TODO(selva) for LAG we need to change this code
        ifindex = switchport[0]['ifindex']
        return ifindex

    def _snmp_get(self, snmp_client, oid):
        try:
            snmp_response = snmp_client.get(oid)
            LOG.debug(" snmp_response %s ", snmp_response)
        except Exception as e:
            LOG.error(_LE("Error in get response '%s' "), e)
            return str(e)
        return snmp_response

    def get_driver_name(self):
        """get driver name for loading the driver using stevedore."""
        return 'hpe' + '_' + constants.PROTOCOL_SNMP

    def get_protocol_validation_result(self, credentials):
        """Get protocol validation result by fetching device MAC."""
        client = snmp_client.get_client(credentials)
        oid = constants.OID_MAC_ADDRESS
        var_binds = self._snmp_get(client, oid)
        for name, val in var_binds:
            mac = val.prettyPrint().zfill(12)
            mac = mac[2:]
            mac_addr = ':'.join([mac[i:i + 2] for i in range(0, 12, 2)])
            return mac_addr

    def get_device_info(self, credentials):
        """Get device information for provisioning."""
        device_ports_list = self._get_ports_info(credentials)
        return device_ports_list

    def _get_ports_info(self, snmp_info):
        """retrieves switch port information."""
        client = snmp_client.get_client(self._get_switch_dict(snmp_info))
        oids = [constants.OID_IF_INDEX,
                constants.OID_PORTS,
                constants.OID_IF_TYPE,
                constants.OID_PORT_STATUS]
        var_binds = client.get_bulk(*oids)
        ports_list = []
        for var_bind_table_row in var_binds:
            if_index = (var_bind_table_row[0][1]).prettyPrint()
            port_name = (var_bind_table_row[1][1]).prettyPrint()
            if_type = (var_bind_table_row[2][1]).prettyPrint()
            if if_type == constants.PHY_PORT_TYPE:
                ports_list.append(
                    {'ifindex': if_index,
                     'interface_name': port_name,
                     'port_status': var_bind_table_row[3][1].prettyPrint()})
        return ports_list
