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

from neutron_lib.api.definitions import portbindings
from neutron_lib import context as neutron_context
from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import uuidutils
import webob.exc as wexc

from neutron.api.v2 import base
from neutron.common import constants as n_const
from neutron.plugins.common import constants
from neutron.plugins.ml2.common import exceptions as ml2_exc
from neutron.plugins.ml2 import driver_api as api

from networking_hpe._i18n import _LE
from networking_hpe._i18n import _LI
from networking_hpe.common import constants as hp_const
from networking_hpe.db import bm_nw_provision_db as db
from networking_hpe import managers
from networking_hpe.ml2.extensions import bnp_switch as bnp_sw


LOG = logging.getLogger(__name__)
driver_opts = [
    cfg.StrOpt('provisioning_driver',
               default='networking_hpe.drivers'
               '.snmp_provisioning_driver.SNMPProvisioningDriver',
               help=_("Driver to provision networks on the switches in"
                      "the cloud fabric")),
]
cfg.CONF.register_opts(driver_opts, "ml2_hpe")
param_opts = [
    cfg.IntOpt('snmp_retries',
               default=5,
               help=_("Number of retries to be done")),
    cfg.IntOpt('snmp_timeout',
               default=3,
               help=_("Timeout in seconds to wait for SNMP request"
                      "completion."))]
cfg.CONF.register_opts(param_opts, "default")


class HPEMechanismDriver(api.MechanismDriver):

    """Ml2 Mechanism front-end driver interface for bare

    metal provisioning.
    """

    def initialize(self):
        self.vif_type = hp_const.HP_VIF_TYPE
        self.vif_details = {portbindings.CAP_PORT_FILTER: True}
        self.prov_manager = managers.ProvisioningManager()

    def create_port_precommit(self, context):
        """create_port_precommit."""
        if not self._is_port_of_interest(context):
            return
        port_dict = self._construct_port(context)
        self._create_port(port_dict)

    def create_port_postcommit(self, context):
        """create_port_postcommit."""
        pass

    def update_port_precommit(self, context):
        """update_port_precommit."""
        vnic_type = self._get_vnic_type(context)
        profile = self._get_binding_profile(context)
        if vnic_type != portbindings.VNIC_BAREMETAL or not profile:
            return
        port_dict = self._construct_port(context)
        host_id = context.current['binding:host_id']
        bind_port_dict = port_dict.get('port')
        bind_port_dict['host_id'] = host_id
        self.update_port(port_dict)

    def update_port_postcommit(self, context):
        """update_port_postcommit."""
        pass

    def delete_port_precommit(self, context):
        """delete_port_postcommit."""
        vnic_type = self._get_vnic_type(context)
        port_id = context.current['id']
        if vnic_type == portbindings.VNIC_BAREMETAL:
            self.delete_port(port_id)

    def delete_port_postcommit(self, context):
        pass

    def bind_port(self, context):
        """bind_port for claiming the ironic port."""
        LOG.debug("HPMechanismDriver Attempting to bind port %(port)s on "
                  "network %(network)s",
                  {'port': context.current['id'],
                   'network': context.network.current['id']})
        port_id = context.current['id']
        for segment in context.segments_to_bind:
            segmentation_id = segment.get(api.SEGMENTATION_ID)
            if self._is_vlan_segment(segment, context):
                port_status = n_const.PORT_STATUS_ACTIVE
                if not self._is_port_of_interest(context):
                    return
                host_id = context.current['binding:host_id']
                if host_id:
                    port = self._construct_port(context, segmentation_id)
                    b_status = self.bind_port_to_segment(port)
                    if b_status == hp_const.BIND_SUCCESS:
                        context.set_binding(segment[api.ID],
                                            self.vif_type,
                                            self.vif_details,
                                            status=port_status)
                        LOG.debug("port bound using segment for port %(port)s",
                                  {'port': port_id})
                        return
                    else:
                        LOG.debug("port binding pass for %(segment)s",
                                  {'segment': segment})
                        return
            else:
                LOG.debug("Ignoring %(seg)s  for port %(port)s",
                          {'seg': segmentation_id,
                           'port': port_id})
        return

    def _is_vlan_segment(self, segment, context):
        """Verify a segment is valid for the HP MechanismDriver.

        Verify the requested segment is supported by HP and return True or
        False to indicate this to callers.
        """
        network_type = segment[api.NETWORK_TYPE]
        if network_type in [constants.TYPE_VLAN]:
            return True
        else:
            False

    def _construct_port(self, context, segmentation_id=None):
        """"Contruct port dict."""
        port = context.current
        port_id = port['id']
        network_id = port['network_id']
        is_lag = False
        bind_port_dict = None
        profile = self._get_binding_profile(context)
        local_link_information = profile.get('local_link_information')
        host_id = context.current['binding:host_id']
        LOG.debug("_construct_port local link info %(local_info)s",
                  {'local_info': local_link_information})
        if local_link_information and len(local_link_information) > 1:
            is_lag = True
        port_dict = {'port':
                     {'id': port_id,
                      'network_id': network_id,
                      'is_lag': is_lag,
                      'switchports': local_link_information,
                      'host_id': host_id
                      }
                     }
        if segmentation_id:
            bind_port_dict = port_dict.get('port')
            bind_port_dict['segmentation_id'] = segmentation_id
            bind_port_dict['access_type'] = hp_const.ACCESS
        else:
            return port_dict
        final_dict = {'port': bind_port_dict}
        LOG.debug("final port dict  %(final_dict)s",
                  {'final_dict': final_dict})
        return final_dict

    def _get_binding_profile(self, context):
        """get binding profile from port context."""
        profile = context.current.get(portbindings.PROFILE, {})
        if not profile:
            LOG.debug("Missing profile in port binding")
        return profile

    def _get_vnic_type(self, context):
        """get vnic type for baremetal."""
        vnic_type = context.current.get(portbindings.VNIC_TYPE, "")
        if not vnic_type:
            return None
        else:
            return vnic_type

    def _is_port_of_interest(self, context):
        vnic_type = self._get_vnic_type(context)
        binding_profile = self._get_binding_profile(context)
        if vnic_type != portbindings.VNIC_BAREMETAL or not binding_profile:
            return False
        local_link_information = binding_profile.get('local_link_information')
        if not local_link_information:
            LOG.debug("local_link_information list does not exist in profile")
            return False
        return True

    def _create_port(self, port):
        switchports = port['port']['switchports']
        LOG.debug(_LE("_create_port switch: %s"), port)
        network_id = port['port']['network_id']
        db_context = neutron_context.get_admin_context()
        subnets = db.get_subnets_by_network(db_context, network_id)
        if not subnets:
            LOG.error(_LE("Subnet not found for the network"))
            self._raise_ml2_error(wexc.HTTPNotFound, 'create_port')
        for switchport in switchports:
            switch_mac_id = switchport['switch_id']
            bnp_switch = db.get_bnp_phys_switch_by_mac(db_context,
                                                       switch_mac_id)
            # check for port and switch level existence
            if not bnp_switch:
                LOG.error(_LE("No physical switch found '%s' "), switch_mac_id)
                self._raise_ml2_error(wexc.HTTPNotFound, 'create_port')
            self.sw_obj = bnp_sw.BNPSwitchController()
            mgmt_proto = bnp_switch['management_protocol']
            creds = bnp_switch['credentials']
            access_parameters = self.sw_obj._get_access_param(db_context,
                                                              mgmt_proto,
                                                              creds)
            for key, value in access_parameters.items():
                if key == hp_const.NAME:
                    continue
                bnp_switch[key] = value
            driver_key = self.sw_obj._protocol_driver(bnp_switch)
            try:
                if driver_key:
                    dr_obj = driver_key.obj
                    mac_val = dr_obj.get_protocol_validation_result(bnp_switch)
                    if mac_val != bnp_switch['mac_address']:
                        self._raise_ml2_error(wexc.HTTPBadRequest,
                                              'Invalid mac address')
            except Exception as e:
                LOG.error(e)
                self._raise_ml2_error(wexc.HTTPBadRequest, 'create_port')
            port_provisioning_db = bnp_switch.port_provisioning
            if (port_provisioning_db !=
                    hp_const.PORT_PROVISIONING_STATUS['enable']):
                LOG.error(_LE("Physical switch is not Enabled '%s' "),
                          bnp_switch.port_provisioning)
                self._raise_ml2_error(wexc.HTTPBadRequest, 'create_port')

    def bind_port_to_segment(self, port):
        """bind_port_to_segment ."""
        db_context = neutron_context.get_admin_context()
        LOG.info(_LI('bind_port_to_segment called from back-end mech driver'))
        switchports = port['port']['switchports']
        for switchport in switchports:
            switch_id = switchport['switch_id']
            bnp_switch = db.get_bnp_phys_switch_by_mac(db_context,
                                                       switch_id)
            port_name = switchport['port_id']
            if not bnp_switch:
                self._raise_ml2_error(wexc.HTTPNotFound, 'create_port')
            credentials_dict = port.get('port')
            cred_dict = self._get_credentials_dict(bnp_switch, 'create_port')
            credentials_dict['credentials'] = cred_dict
            try:
                prov_protocol = bnp_switch.management_protocol
                vendor = bnp_switch.vendor
                family = bnp_switch.family
                prov_driver = self._provisioning_driver(prov_protocol, vendor,
                                                        family)
                if not prov_driver:
                    LOG.error(_LE("No suitable provisioning driver found"
                                  ))
                    self._raise_ml2_error(wexc.HTTPNotFound, 'create_port')
                port_list = prov_driver.obj.get_device_info(port)
                ifindex = self._get_if_index(port_list, port_name)
                switchport['ifindex'] = ifindex
                if not port_list:
                    LOG.error(_LE("No physical port found for '%s' "),
                              switch_id)
                    self._raise_ml2_error(wexc.HTTPNotFound, 'create_port')
                prov_driver.obj.set_isolation(port)
                port_id = port['port']['id']
                segmentation_id = port['port']['segmentation_id']
                mapping_dict = {'neutron_port_id': port_id,
                                'switch_port_name': port_name,
                                'switch_id': bnp_switch.id,
                                'lag_id': None,
                                'access_type': hp_const.ACCESS,
                                'segmentation_id': int(segmentation_id),
                                'bind_status': 0,
                                'ifindex': ifindex
                                }
                db.add_bnp_switch_port_map(db_context, mapping_dict)
                db.add_bnp_neutron_port(db_context, mapping_dict)
                if bnp_switch.validation_result != hp_const.SUCCESS:
                    db.update_bnp_phys_switch_result_status(db_context,
                                                            bnp_switch.id,
                                                            hp_const.SUCCESS)
                return hp_const.BIND_SUCCESS
            except Exception as e:
                LOG.error(_LE("Exception in configuring VLAN '%s' "), e)
                return hp_const.BIND_FAILURE

    def update_port(self, port):
        """update_port ."""
        db_context = neutron_context.get_admin_context()
        port_id = port['port']['id']
        bnp_sw_map = db.get_bnp_switch_port_mappings(db_context, port_id)
        if not bnp_sw_map:
            # We are creating the switch ports because initial ironic
            # port-create will not supply local link information for tenant .
            # networks . Later ironic port-update , the local link information
            # value will be supplied.
            self._create_port(port)

    def delete_port(self, port_id):
        """delete_port ."""
        db_context = neutron_context.get_admin_context()
        try:
            port_map = db.get_bnp_neutron_port(db_context, port_id)
        except Exception:
            LOG.error(_LE("No neutron port is associated with the phys port"))
            return
        is_last_port_in_vlan = False
        seg_id = port_map.segmentation_id
        bnp_sw_map = db.get_bnp_switch_port_mappings(db_context, port_id)
        bnp_switch = db.get_bnp_phys_switch(db_context,
                                            bnp_sw_map[0].switch_id)
        cred_dict = self._get_credentials_dict(bnp_switch, 'delete_port')
        result = db.get_bnp_neutron_port_by_seg_id(db_context, seg_id)
        if not result:
            LOG.error(_LE("No neutron port is associated with the phys port"))
            self._raise_ml2_error(wexc.HTTPNotFound, 'delete_port')
        if len(result) == 1:
            # to prevent snmp set from the same VLAN
            is_last_port_in_vlan = True
        port_dict = {'port':
                     {'id': port_id,
                      'segmentation_id': seg_id,
                      'ifindex': bnp_sw_map[0].ifindex,
                      'is_last_port_vlan': is_last_port_in_vlan
                      }
                     }
        credentials_dict = port_dict.get('port')
        credentials_dict['credentials'] = cred_dict
        try:
            prov_protocol = bnp_switch.management_protocol
            vendor = bnp_switch.vendor
            family = bnp_switch.family
            prov_driver = self._provisioning_driver(prov_protocol, vendor,
                                                    family)
            if not prov_driver:
                LOG.error(_LE("No suitable provisioning driver found"
                              ))
                self._raise_ml2_error(wexc.HTTPNotFound, 'create_port')
            prov_driver.obj.delete_isolation(port_dict)
            db.delete_bnp_neutron_port(db_context, port_id)
            db.delete_bnp_switch_port_mappings(db_context, port_id)
        except Exception as e:
            LOG.error(_LE("Error in deleting the port '%s' "), e)
            self._raise_ml2_error(wexc.HTTPNotFound, 'delete_port')

    def _provisioning_driver(self, protocol, vendor, family):
        """Get the provisioning driver instance."""
        try:
            if hp_const.PROTOCOL_SNMP in protocol:
                driver_key = self._driver_key(vendor, hp_const.PROTOCOL_SNMP,
                                              family)
                driver = self.prov_manager.provisioning_driver(driver_key)
            else:
                driver_key = self._driver_key(vendor, protocol,
                                              family)
                driver = self.prov_manager.provisioning_driver(driver_key)
        except Exception as e:
            LOG.error(_LE("No suitable provisioning driver loaded'%s' "), e)
            return
        return driver

    def _driver_key(self, vendor, protocol, family):
        if family:
            driver_key = vendor + '_' + protocol + '_' + family
        else:
            driver_key = vendor + '_' + protocol
        return driver_key

    def _raise_ml2_error(self, err_type, method_name):
        base.FAULT_MAP.update({ml2_exc.MechanismDriverError: err_type})
        raise ml2_exc.MechanismDriverError(method=method_name)

    def _get_credentials_dict(self, bnp_switch, func_name):
        if not bnp_switch:
            self._raise_ml2_error(wexc.HTTPNotFound, func_name)
        db_context = neutron_context.get_admin_context()
        creds_dict = {}
        creds_dict['ip_address'] = bnp_switch.ip_address
        prov_creds = bnp_switch.credentials
        prov_protocol = bnp_switch.management_protocol
        if hp_const.PROTOCOL_SNMP in prov_protocol:
            if not uuidutils.is_uuid_like(prov_creds):
                snmp_cred = db.get_snmp_cred_by_name(db_context, prov_creds)
                snmp_cred = snmp_cred[0]
            else:
                snmp_cred = db.get_snmp_cred_by_id(db_context, prov_creds)
            if not snmp_cred:
                LOG.error(_LE("Credentials does not match"))
                self._raise_ml2_error(wexc.HTTPNotFound, '')
            creds_dict['write_community'] = snmp_cred.write_community
            creds_dict['security_name'] = snmp_cred.security_name
            creds_dict['security_level'] = snmp_cred.security_level
            creds_dict['auth_protocol'] = snmp_cred.auth_protocol
            creds_dict['management_protocol'] = prov_protocol
            creds_dict['auth_key'] = snmp_cred.auth_key
            creds_dict['priv_protocol'] = snmp_cred.priv_protocol
            creds_dict['priv_key'] = snmp_cred.priv_key
        else:
            if not uuidutils.is_uuid_like(prov_creds):
                netconf_cred = db.get_netconf_cred_by_name(db_context,
                                                           prov_creds)
            else:
                netconf_cred = db.get_netconf_cred_by_id(db_context,
                                                         prov_creds)
            if not netconf_cred:
                LOG.error(_LE("Credentials does not match"))
                self._raise_ml2_error(wexc.HTTPNotFound, '')
            creds_dict['user_name'] = netconf_cred.write_community
            creds_dict['password'] = netconf_cred.security_name
            creds_dict['key_path'] = netconf_cred.security_level
        return creds_dict

    def _get_if_index(self, port_list, port_name):
        if_index = ''
        if not port_list:
            LOG.error(_LE("No Physical ports found."))
            return
        for port_dict in port_list:
            interface_name = port_dict['interface_name']
            if port_name == interface_name:
                if_index = port_dict['ifindex']
                break
        return if_index
