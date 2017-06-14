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

from neutron.api import extensions as neutron_extensions
from neutron.plugins.ml2 import driver_api as api

from networking_hpe.ml2 import extensions

from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class HPEIronicCredentialExtDriver(api.ExtensionDriver):
    _supported_extension_aliases = "bnp-credential"

    def initialize(self):
        neutron_extensions.append_api_extensions_path(extensions.__path__)
        LOG.info(_("HPEIronicCredentialExtDriver initialization complete"))

    @property
    def extension_alias(self):
        """Supported extension alias.

        identifying the core API extension supported
                  by this BNP driver
        """
        return self._supported_extension_aliases[:]
