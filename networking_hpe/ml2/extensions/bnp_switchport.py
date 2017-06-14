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

from neutron_lib.api import extensions
import webob.exc

from neutron.api.v2 import base
from neutron.api.v2 import resource
from neutron import wsgi

from networking_hpe.common import constants as const
from networking_hpe.db import bm_nw_provision_db as db
from networking_hpe.db import bm_nw_provision_models as models


RESOURCE_ATTRIBUTE_MAP = {
    'bnp-switch-ports': {
        'switch_name': {'allow_post': False, 'allow_put': False,
                        'is_visible': True},
        'neutron_port_id': {'allow_post': False, 'allow_put': False,
                            'is_visible': True},
        'switch_port_name': {'allow_post': False, 'allow_put': False,
                             'is_visible': True},
        'segmentation_id': {'allow_post': False, 'allow_put': False,
                            'is_visible': True},
        'lag_id': {'allow_post': False, 'allow_put': False,
                   'is_visible': True},
        'bind_status': {'allow_post': False, 'allow_put': False,
                        'is_visible': True},
        'access_type': {'allow_post': False, 'allow_put': False,
                        'is_visible': True}

    },
}


class BNPSwitchPortController(wsgi.Controller):

    """WSGI Controller for the extension bnp-switch-port."""

    def index(self, request, **kwargs):
        context = request.context
        req_dict = dict(request.GET)
        filter_dict = self.get_filter_dict(**req_dict)
        port_maps = db.get_all_bnp_switch_port_maps(context, filter_dict)
        port_list = []
        for port_map in port_maps:
            if (port_map[5] == 0):
                bind_val = const.BIND_SUCCESS
            else:
                bind_val = const.BIND_FAILURE
            port_dict = {'neutron_port_id': port_map[0],
                         'switch_port_name': port_map[1],
                         'lag_id': port_map[2],
                         'segmentation_id': str(port_map[3]),
                         'access_type': port_map[4],
                         'bind_status': bind_val,
                         'switch_name': port_map[6]}
            port_list.append(port_dict)
        return {'bnp_switch_ports': port_list}

    def get_filter_dict(self, **args):
        switchportmap = models.BNPSwitchPortMapping
        neutronport = models.BNPNeutronPort
        physwitch = models.BNPPhysicalSwitch
        filter_dict = {}
        for key in args:
            val = args[key]
            if key == 'switch_name':
                field = physwitch.name
            elif key == 'neutron_port_id':
                field = switchportmap.neutron_port_id
            elif key == 'switch_port_name':
                field = switchportmap.switch_port_name
            elif key == 'segmentation_id':
                field = neutronport.segmentation_id
            elif key == 'lag_id':
                field = neutronport.lag_id
            elif key == 'bind_status':
                field = neutronport.bind_status
                if val == 'bind_success':
                    val = '0'
                else:
                    val = '1'
            elif key == 'access_type':
                field = neutronport.access_type
            else:
                raise webob.exc.HTTPBadRequest(_("Invalid field value"))
            filter_dict[field] = val
        return filter_dict

    def create(self, request, **kwargs):
        raise webob.exc.HTTPBadRequest(
            _("This operation is not allowed"))

    def show(self, request, id, **kwargs):
        raise webob.exc.HTTPBadRequest(
            _("This operation is not allowed"))

    def delete(self, request, id, **kwargs):
        raise webob.exc.HTTPBadRequest(
            _("This operation is not allowed"))

    def update(self, request, id, **kwargs):
        raise webob.exc.HTTPBadRequest(
            _("This operation is not allowed"))


class Bnp_switchport(extensions.ExtensionDescriptor):

    """API extension for Neutron Port Mapping support."""

    @classmethod
    def get_name(cls):
        return "Neutron Port Mapping"

    @classmethod
    def get_alias(cls):
        return "bnp-switch-port"

    @classmethod
    def get_description(cls):
        return ("Abstraction for physical switch ports"
                "which are mapped to neutron port bindings"
                "for a given switch")

    @classmethod
    def get_updated(cls):
        return "2016-05-26T00:00:00-00:00"

    def get_resources(self):
        exts = []
        controller = resource.Resource(BNPSwitchPortController(),
                                       base.FAULT_MAP)
        exts.append(extensions.ResourceExtension(
            'bnp-switch-ports', controller))
        return exts

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}
