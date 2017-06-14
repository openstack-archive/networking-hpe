# Copyright (c) 2015 Hewlett-Packard Enterprise LP
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


"""Exceptions used by the networking-hpe ML2 Mechanism Driver."""

from neutron_lib import exceptions
from webob import exc


class HPNetProvisioningConfigError(exceptions.NeutronException):
    message = _('%(msg)s')


class HPNetProvisioningDriverError(exceptions.NeutronException):
    message = _('%(msg)s')


class SslCertificateValidationError(exceptions.NeutronException):
    message = _("SSL certificate validation has failed: %(msg)s")


class ConnectionFailed(exceptions.NeutronException):
    message = _(" Connection has failed: %(msg)s")


class SNMPFailure(exc.HTTPBadRequest):

    def __init__(self, **kwargs):
        self.explanation = self.explanation % (kwargs)
        super(SNMPFailure, self).__init__()

    explanation = ("SNMP operation '%(operation)s'"
                   "failed: Either device is not reacheable"
                   " or invalid credentials")
