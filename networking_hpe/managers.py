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

from oslo_config import cfg
from oslo_log import log
import stevedore

from networking_hpe._i18n import _LE
from networking_hpe._i18n import _LI


LOG = log.getLogger(__name__)


class ProvisioningManager(stevedore.named.NamedExtensionManager):
    """Manage provisioning drivers for BNP."""

    def __init__(self):
        # Mapping from provisioning driver name to DriverManager
        self.drivers = {}
        conf = cfg.CONF.ml2_hpe
        LOG.info(_LI("Configured provisioning driver names: %s"),
                 conf.provisioning_driver)
        super(ProvisioningManager, self).__init__('bnp.provisioning_driver',
                                                  conf.provisioning_driver,
                                                  invoke_on_load=True)
        LOG.info(_LI("Loaded provisioning driver names: %s"), self.names())
        self._register_provisioning()

    def _register_provisioning(self):
        for ext in self:
            provisioning_type = ext.obj.get_driver_name()
            if provisioning_type in self.drivers:
                LOG.error(_LE("provisioning driver '%(new_driver)s' ignored "
                              " provisioning driver '%(old_driver)s' already"
                              " registered for provisioning '%(type)s'"),
                          {'new_driver': ext.name,
                           'old_driver': self.drivers[provisioning_type].name,
                           'type': provisioning_type})
            else:
                self.drivers[provisioning_type] = ext
        LOG.info(_LI("Registered provisioning driver: %s"),
                 self.drivers.keys())

    def provisioning_driver(self, provisioning_type):
        """provisioning driver instance."""
        driver = self.drivers.get(provisioning_type)
        LOG.info(_LI("Loaded provisioning driver type: %s"), driver.obj)
        return driver
