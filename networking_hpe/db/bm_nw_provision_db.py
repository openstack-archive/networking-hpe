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
from oslo_utils import uuidutils
from sqlalchemy.orm import exc

from neutron.db import models_v2

from networking_hpe._i18n import _LE
from networking_hpe._i18n import _LI
from networking_hpe.db import bm_nw_provision_models as models


LOG = logging.getLogger(__name__)


def get_subnets_by_network(context, network_id):
    subnet_qry = context.session.query(models_v2.Subnet)
    return subnet_qry.filter_by(network_id=network_id).all()


def add_bnp_phys_switch(context, switch):
    """Add physical switch."""
    session = context.session
    with session.begin(subtransactions=True):
        uuid = uuidutils.generate_uuid()
        phy_switch = models.BNPPhysicalSwitch(
            id=uuid,
            name=switch['name'],
            ip_address=switch['ip_address'],
            mac_address=switch['mac_address'],
            port_provisioning=switch['port_provisioning'],
            management_protocol=switch['management_protocol'],
            credentials=switch['credentials'],
            validation_result=switch['validation_result'],
            vendor=switch['vendor'],
            family=switch['family'])
        session.add(phy_switch)
    return phy_switch


def add_bnp_neutron_port(context, port):
    """Add neutron port."""
    session = context.session
    with session.begin(subtransactions=True):
        neutron_port = models.BNPNeutronPort(
            neutron_port_id=port['neutron_port_id'],
            lag_id=port['lag_id'],
            access_type=port['access_type'],
            segmentation_id=port['segmentation_id'],
            bind_status=port['bind_status'])
        session.add(neutron_port)


def add_bnp_switch_port_map(context, mapping):
    """Add switch port to neutron port mapping."""
    session = context.session
    with session.begin(subtransactions=True):
        port_map = models.BNPSwitchPortMapping(
            neutron_port_id=mapping['neutron_port_id'],
            switch_port_name=mapping['switch_port_name'],
            ifindex=mapping['ifindex'],
            switch_id=mapping['switch_id'])
        session.add(port_map)


def get_bnp_phys_switch(context, switch_id):
    """Get physical switch that matches id."""
    try:
        query = context.session.query(models.BNPPhysicalSwitch)
        switch = query.filter_by(id=switch_id).one()
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found with id: %s"), switch_id)
        return
    return switch


def get_bnp_phys_switch_name(context, name):
    """Get physical switch that matches name."""
    try:
        query = context.session.query(models.BNPPhysicalSwitch)
        switch = query.filter_by(name=name).all()
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found with name: %s"), name)
        return
    return switch


def get_bnp_phys_switch_by_ip(context, ip_addr):
    """Get physical switch that matches ip address."""
    try:
        query = context.session.query(models.BNPPhysicalSwitch)
        switch = query.filter_by(ip_address=ip_addr).one()
    except exc.NoResultFound:
        LOG.info(_LI("no physical switch found with ip address: %s"), ip_addr)
        return
    return switch


def get_if_bnp_phy_switch_exists(context, **args):
    """check if physical switch exists for a given filter."""
    try:
        query = context.session.query(
            models.BNPPhysicalSwitch).filter_by(**args)
        switch_exists = context.session.query(query.exists()).scalar()
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found"))
        return
    return switch_exists


def get_bnp_neutron_port(context, neutron_port_id):
    """Get bnp neutron port that matches neutron_port_id."""
    try:
        query = context.session.query(models.BNPNeutronPort)
        port_map = query.filter_by(neutron_port_id=neutron_port_id).one()
    except exc.NoResultFound:
        LOG.error(_LE('no port map found with id: %s'), port_map)
        return
    return port_map


def get_bnp_neutron_port_by_seg_id(context, segmentation_id):
    """Get bnp neutron port that matches seg_id."""
    try:
        query = context.session.query(models.BNPNeutronPort)
        port_map = query.filter_by(segmentation_id=segmentation_id).all()
    except exc.NoResultFound:
        LOG.error(_LE('no port map found with id: %s'), segmentation_id)
        return
    return port_map


def get_bnp_switch_port_map_by_switchid(context, switch_id):
    """Get switch port map by switch_id."""
    try:
        query = context.session.query(models.BNPSwitchPortMapping)
        port_map = query.filter_by(switch_id=switch_id).all()
    except exc.NoResultFound:
        LOG.error(_LE("no switch port mapping found for switch: %s"),
                  switch_id)
        return
    return port_map


def get_bnp_switch_port_mappings(context, neutron_port_id):
    """Get switch port map by neutron_port_id."""
    try:
        query = context.session.query(models.BNPSwitchPortMapping)
        port_map = query.filter_by(neutron_port_id=neutron_port_id).all()
    except exc.NoResultFound:
        LOG.error(_LE("no switch port mapping found for switch: %s"),
                  neutron_port_id)
        return
    return port_map


def get_all_bnp_switch_port_maps(context, filter_dict):
    """Get all switch port maps."""
    try:
        switchportmap = models.BNPSwitchPortMapping
        neutronport = models.BNPNeutronPort
        physwitch = models.BNPPhysicalSwitch
        query = context.session.query(switchportmap.neutron_port_id,
                                      switchportmap.switch_port_name,
                                      neutronport.lag_id,
                                      neutronport.segmentation_id,
                                      neutronport.access_type,
                                      neutronport.bind_status, physwitch.name)
        query = query.join(neutronport,
                           neutronport.neutron_port_id ==
                           switchportmap.neutron_port_id)
        query = query.join(physwitch, switchportmap.switch_id == physwitch.id)
        for key, value in filter_dict.items():
            query = query.filter(key == value)
        port_maps = query.all()
    except exc.NoResultFound:
        LOG.error(_LE("no switch port mappings found"))
        return
    return port_maps


def get_bnp_phys_switch_by_mac(context, mac):
    """Get physical switch that matches mac address."""
    try:
        query = context.session.query(models.BNPPhysicalSwitch)
        switch = query.filter_by(mac_address=mac).one()
    except exc.NoResultFound:
        LOG.error(_LE('no physical switch found with mac address: %s'), mac)
        return
    return switch


def delete_bnp_switch_port_mappings(context, neutron_port_id):
    """Delete mappings that matches neutron_port_id."""
    session = context.session
    with session.begin(subtransactions=True):
        if neutron_port_id:
            session.query(models.BNPSwitchPortMapping).filter_by(
                neutron_port_id=neutron_port_id).delete()


def delete_bnp_phys_switch(context, switch_id):
    """Delete physical switch that matches switch_id."""
    try:
        session = context.session
        with session.begin(subtransactions=True):
            if switch_id:
                session.query(models.BNPPhysicalSwitch).filter_by(
                    id=switch_id).delete()
    except exc.NoResultFound:
        LOG.error(_LE("no switch found for switch id: %s"), switch_id)


def delete_bnp_neutron_port(context, nport_id):
    """Delete neutron port that matches_id."""
    session = context.session
    with session.begin(subtransactions=True):
        if nport_id:
            session.query(models.BNPNeutronPort).filter_by(
                neutron_port_id=nport_id).delete()


def get_all_bnp_phys_switches(context, **args):
    """Get all physical switches."""
    try:
        query = context.session.query(
            models.BNPPhysicalSwitch).filter_by(**args)
        switches = query.all()
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found"))
        return
    return switches


def update_bnp_phy_switch(context, sw_id, switch):
    """Update physical switch name."""
    try:
        with context.session.begin(subtransactions=True):
            (context.session.query(models.BNPPhysicalSwitch).filter_by(
                id=sw_id).update(
                    {'name': switch['name'],
                     'ip_address': switch['ip_address'],
                     'mac_address': switch['mac_address'],
                     'port_provisioning': switch['port_provisioning'],
                     'management_protocol': switch['management_protocol'],
                     'credentials': switch['credentials'],
                     'validation_result': switch['validation_result'],
                     'vendor': switch['vendor'],
                     'family': switch['family']},
                    synchronize_session=False))
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found for id: %s"), sw_id)


def update_bnp_phys_switch_result_status(context, sw_id, sw_status):
    """Update physical switch validation result status."""
    try:
        with context.session.begin(subtransactions=True):
            (context.session.query(models.BNPPhysicalSwitch).filter_by(
                id=sw_id).update(
                    {'validation_result': sw_status},
                    synchronize_session=False))
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found for id: %s"), sw_id)


def update_bnp_phys_switch_access_params(context, switch_id, params):
    """Update physical switch with access params."""
    try:
        with context.session.begin(subtransactions=True):
            (context.session.query(models.BNPPhysicalSwitch).filter_by(
                id=switch_id).update(
                    {'access_protocol': params['access_protocol'],
                     'write_community': params['write_community'],
                     'security_name': params['security_name'],
                     'auth_protocol': params['auth_protocol'],
                     'auth_key': params['auth_key'],
                     'priv_protocol': params['priv_protocol'],
                     'priv_key': params['priv_key'],
                     'security_level': params['security_level']},
                    synchronize_session=False))
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found for id: %s"), switch_id)


def update_bnp_snmp_cred_by_id(context, cred_id, creds):
    """Update snmp switch credentials."""
    try:
        with context.session.begin(subtransactions=True):
            (context.session.query(models.BNPSNMPCredential).filter_by(
             id=cred_id).update(
                {'name': creds['name'],
                 'protocol_type': creds['protocol_type'],
                 'write_community': creds['write_community'],
                 'security_name': creds['security_name'],
                 'auth_protocol': creds['auth_protocol'],
                 'auth_key': creds['auth_key'],
                 'priv_protocol': creds['priv_protocol'],
                 'priv_key': creds['priv_key'],
                 'security_level': creds['security_level']},
             synchronize_session=False))
    except exc.NoResultFound:
        LOG.error(_LE("no snmp switch credentials found for id: %s"), cred_id)


def get_snmp_cred_by_name_and_protocol(context, name, proto_type):
    """Get SNMP Credential that matches name and protocol."""
    try:
        query = context.session.query(models.BNPSNMPCredential)
        snmp_creds = query.filter_by(name=name, protocol_type=proto_type).all()
    except exc.NoResultFound:
        LOG.info(
            _LI("no snmp credential found with name:"
                " %(name)s and protocol: %(proto_type)s"), {'name': name,
                                                            'proto_type':
                                                            proto_type})
        return
    return snmp_creds


def get_netconf_cred_by_name_and_protocol(context, name, proto_type):
    """Get NETCONF Credentials that matches name and protocol."""
    try:
        query = context.session.query(models.BNPNETCONFCredential)
        netconf_creds = query.filter_by(name=name,
                                        protocol_type=proto_type).all()
    except exc.NoResultFound:
        LOG.info(_LI("no netconf credential found with name:"
                     " %(name)s and protocol:  %(proto_type)s"), {'name': name,
                                                                  'proto_type':
                                                                  proto_type})
        return
    return netconf_creds


def update_bnp_netconf_cred_by_id(context, cred_id, creds):
    """Update netconf switch credentials."""
    try:
        with context.session.begin(subtransactions=True):
            (context.session.query(models.BNPNETCONFCredential).filter_by(
             id=cred_id).update(
             {'name': creds['name'],
              'protocol_type': creds['protocol_type'],
              'user_name': creds['user_name'],
              'password': creds['password'],
              'key_path': creds['key_path']},
             synchronize_session=False))
    except exc.NoResultFound:
        LOG.error(
            _LE("no netconf switch credentials found for id: %s"), cred_id)


def add_bnp_snmp_cred(context, snmp_cred):
    """Add SNMP Credential."""
    session = context.session
    with session.begin(subtransactions=True):
        uuid = uuidutils.generate_uuid()
        snmp_cred = models.BNPSNMPCredential(
            id=uuid,
            name=snmp_cred['name'],
            protocol_type=snmp_cred['protocol_type'],
            write_community=snmp_cred['write_community'],
            security_name=snmp_cred['security_name'],
            auth_protocol=snmp_cred['auth_protocol'],
            auth_key=snmp_cred['auth_key'],
            priv_protocol=snmp_cred['priv_protocol'],
            priv_key=snmp_cred['priv_key'],
            security_level=snmp_cred['security_level'])
        session.add(snmp_cred)
    return snmp_cred


def add_bnp_netconf_cred(context, netconf_cred):
    """Add NETCONF Credential."""
    session = context.session
    with session.begin(subtransactions=True):
        uuid = uuidutils.generate_uuid()
        netconf_cred = models.BNPNETCONFCredential(
            id=uuid,
            name=netconf_cred['name'],
            protocol_type=netconf_cred['protocol_type'],
            user_name=netconf_cred['user_name'],
            password=netconf_cred['password'],
            key_path=netconf_cred['key_path'])
        session.add(netconf_cred)
    return netconf_cred


def get_all_snmp_creds(context, **args):
    """Get all SNMP Credentials."""
    try:
        query = context.session.query(
            models.BNPSNMPCredential).filter_by(**args)
        snmp_creds = query.all()
    except exc.NoResultFound:
        LOG.error(_LE("no snmp credential found"))
        return
    return snmp_creds


def get_all_netconf_creds(context, **args):
    """Get all NETCONF Credentials."""
    try:
        query = context.session.query(
            models.BNPNETCONFCredential).filter_by(**args)
        netconf_creds = query.all()
    except exc.NoResultFound:
        LOG.error(_LE("no netconf credential found"))
        return
    return netconf_creds


def get_snmp_cred_by_name(context, name):
    """Get SNMP Credential that matches name."""
    try:
        query = context.session.query(models.BNPSNMPCredential)
        snmp_creds = query.filter_by(name=name).all()
    except exc.NoResultFound:
        LOG.info(_LI("no snmp credential found with name: %s"), name)
        return
    return snmp_creds


def get_snmp_cred_by_id(context, id):
    """Get SNMP Credential that matches id."""
    try:
        query = context.session.query(models.BNPSNMPCredential)
        snmp_cred = query.filter_by(id=id).one()
    except exc.NoResultFound:
        LOG.info(_LI("no snmp credential found with id: %s"), id)
        return
    return snmp_cred


def get_netconf_cred_by_name(context, name):
    """Get NETCONF Credential that matches name."""
    try:
        query = context.session.query(models.BNPNETCONFCredential)
        netconf_creds = query.filter_by(name=name).all()
    except exc.NoResultFound:
        LOG.info(_LI("no netconf credential found with name: %s"), name)
        return
    return netconf_creds


def get_netconf_cred_by_id(context, id):
    """Get NETCONF Credential that matches id."""
    try:
        query = context.session.query(models.BNPNETCONFCredential)
        netconf_cred = query.filter_by(id=id).one()
    except exc.NoResultFound:
        LOG.info(_LI("no netconf credential found with id: %s"), id)
        return
    return netconf_cred


def delete_snmp_cred_by_id(context, id):
    """Delete SNMP credential by id."""
    session = context.session
    with session.begin(subtransactions=True):
        session.query(models.BNPSNMPCredential).filter_by(
            id=id).delete()


def delete_netconf_cred_by_id(context, id):
    """Delete NETCONF credential by id."""
    session = context.session
    with session.begin(subtransactions=True):
        session.query(models.BNPNETCONFCredential).filter_by(
            id=id).delete()


def get_bnp_phys_switch_by_name(context, name):
    """Get physical switch that matches name."""
    try:
        query = context.session.query(models.BNPPhysicalSwitch)
        switch = query.filter_by(name=name).all()
    except exc.NoResultFound:
        LOG.error(_LE("no physical switch found with name: %s"), name)
        return
    return switch


def delete_bnp_phys_switch_by_name(context, name):
    """Delete physical switch that matches name."""
    try:
        session = context.session
        with session.begin(subtransactions=True):
            if name:
                session.query(models.BNPPhysicalSwitch).filter_by(
                    name=name).delete()
    except exc.NoResultFound:
        LOG.error(_LE("no switch found for switch name: %s"), name)
