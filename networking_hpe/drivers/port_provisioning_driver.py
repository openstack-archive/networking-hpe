# Copyright (c) 2015 OpenStack Foundation
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


import abc

import six


@six.add_metaclass(abc.ABCMeta)
class PortProvisioningDriver(object):
    """Interface between Back-end driver and other generic

    network-provisioning drivers.
    """

    def initialize(self):
        pass

    @abc.abstractmethod
    def set_isolation(self, port):
        """set_isolation create the vlan and the  associate vlan to

         the physical ports.
         """
        pass

    @abc.abstractmethod
    def delete_isolation(self, port):
        """delete_isolation deletes the vlan from the physical ports."""

        pass

    @abc.abstractmethod
    def create_lag(self, port):
        """create_lag  creates the link aggregation for the physical ports."""

        pass

    @abc.abstractmethod
    def delete_lag(self, port):
        """delete_lag  delete the link aggregation for the physical ports."""
        pass

    @abc.abstractmethod
    def get_driver_name(self):
        """get driver name for stevedore loading."""
        pass

    @abc.abstractmethod
    def get_protocol_validation_result(self, credentials):
        """Returns the protocol validation result."""
        pass

    @abc.abstractmethod
    def get_device_info(self, credentials):
        """get device information needed for provisioning."""
        pass
