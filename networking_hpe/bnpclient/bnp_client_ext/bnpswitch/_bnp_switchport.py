# Copyright (c) 2016 OpenStack Foundation
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

from neutronclient.common import extension


class BnpSwitchPort(extension.NeutronClientExtension):
    resource = 'bnp_switch_port'
    resource_plural = '%ss' % resource
    path = 'bnp-switch-ports'
    object_path = '/%s' % path
    resource_path = '/%s/%%s' % path
    versions = ['2.0']


class BnpSwitchPortList(extension.ClientExtensionList, BnpSwitchPort):
    """List all switch ports information."""

    shell_command = 'switch-port-list'
    allow_names = False
    list_columns = ['switch_name',
                    'neutron_port_id',
                    'switch_port_name',
                    'segmentation_id',
                    'lag_id', 'bind_status',
                    'access_type']
    pagination_support = True
    sorting_support = True