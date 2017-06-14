# Copyright (c) 2016 Hewlett-Packard Enterprise Development, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron_lib.api import extensions as nl_extensions
from neutron_lib.api import validators as nl_validators
from oslo_log import log as logging
from oslo_utils import uuidutils
import webob.exc

from neutron.api import extensions
from neutron.api.v2 import base
from neutron.api.v2 import resource
from neutron import wsgi

from networking_hpe.common import constants as const
from networking_hpe.common import validators
from networking_hpe.db import bm_nw_provision_db as db


LOG = logging.getLogger(__name__)


RESOURCE_ATTRIBUTE_MAP = {
    'bnp-credentials': {
        'id': {'allow_post': False, 'allow_put': False,
               'is_visible': True},
        'name': {'allow_post': True, 'allow_put': True,
                 'validate': {'type:string': None},
                 'is_visible': True},
        'snmpv1': {'allow_post': True, 'allow_put': True,
                   'validate': {'type:access_dict': None},
                   'is_visible': True},
        'snmpv2c': {'allow_post': True, 'allow_put': True,
                    'validate': {'type:access_dict': None},
                    'is_visible': True},
        'snmpv3': {'allow_post': True, 'allow_put': True,
                   'validate': {'type:access_dict': None},
                   'is_visible': True},
        'netconf_ssh': {'allow_post': True, 'allow_put': True,
                        'validate': {'type:access_dict': None},
                        'is_visible': True},
        'netconf_soap': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:access_dict': None},
                         'is_visible': True},
    },
}

validator_func = validators.access_parameter_validator
nl_validators.add_validator('type:access_dict', validator_func)


class BNPCredentialController(wsgi.Controller):

    """WSGI Controller for the extension bnp-credential."""

    def _check_admin(self, context):
        reason = _("Only admin can configure Bnp-credential")
        if not context.is_admin:
            raise webob.exc.HTTPForbidden(reason)

    def index(self, request, **kwargs):
        context = request.context
        filters = {}
        creds = []
        req_dict = dict(request.GET)
        if req_dict and req_dict.get('fields', None):
            req_dict.pop('fields')
        filters = req_dict
        creds = db.get_all_snmp_creds(context, **filters)
        netconf_creds = db.get_all_netconf_creds(context, **filters)
        for i in netconf_creds:
            creds.append(i)
        creds = self._creds_to_show(creds)
        creds_dict = {'bnp_credentials': creds}
        return creds_dict

    def _creds_to_show(self, creds):
        attr_list = ['security_name', 'auth_protocol', 'auth_key',
                     'priv_protocol', 'priv_key', 'write_community',
                     'security_level', 'user_name', 'password', 'key_path']
        creds_list = []
        if isinstance(creds, list):
            for cred in creds:
                cred = dict(cred)
                for key in attr_list:
                    if key in cred:
                        cred.pop(key)
                creds_list.append(cred)
            return creds_list
        else:
            cred = dict(creds)
            for key in attr_list:
                if key in cred:
                    cred.pop(key)
            return cred

    def show(self, request, id, **kwargs):
        context = request.context
        snmp_cred = db.get_snmp_cred_by_id(context, id)
        netconf_cred = db.get_netconf_cred_by_id(context, id)
        if snmp_cred:
            cred = self._creds_to_show(snmp_cred)
        elif netconf_cred:
            cred = self._creds_to_show(netconf_cred)
        else:
            raise webob.exc.HTTPNotFound(
                _("Credential with id=%s does not exist") % id)
        return {const.BNP_CREDENTIAL_RESOURCE_NAME: cred}

    def delete(self, request, id, **kwargs):
        context = request.context
        self._check_admin(context)
        filters = {'credentials': id}
        switch_exists = db.get_if_bnp_phy_switch_exists(context, **filters)
        if switch_exists:
            raise webob.exc.HTTPConflict(
                _("credential with id=%s is associated with a switch."
                  "Hence can't be deleted.") % id)
        snmp_cred = db.get_snmp_cred_by_id(context, id)
        netconf_cred = db.get_netconf_cred_by_id(context, id)
        if snmp_cred:
            db.delete_snmp_cred_by_id(context, id)
        elif netconf_cred:
            db.delete_netconf_cred_by_id(context, id)
        else:
            raise webob.exc.HTTPNotFound(
                _("Credential with id=%s does not exist") % id)

    def create(self, request, **kwargs):
        """Create a new Credential."""
        context = request.context
        self._check_admin(context)
        body = validators.validate_request(request)
        key_list = ['name', 'snmpv1', 'snmpv2c',
                    'snmpv3', 'netconf_ssh', 'netconf_soap']
        keys = body.keys()
        validators.validate_attributes(keys, key_list)
        protocol = validators.validate_access_parameters(body)
        if protocol in ['snmpv1', 'snmpv2c', 'snmpv3']:
            db_snmp_cred = self._create_snmp_creds(context, body, protocol)
            db_snmp_cred = self._creds_to_show(db_snmp_cred)
            return {const.BNP_CREDENTIAL_RESOURCE_NAME: dict(db_snmp_cred)}
        else:
            db_netconf_cred = self._create_netconf_creds(
                context, body, protocol)
            db_netconf_cred = self._creds_to_show(db_netconf_cred)
            return {const.BNP_CREDENTIAL_RESOURCE_NAME: dict(db_netconf_cred)}

    def _create_snmp_creds(self, context, body, protocol):
        """Create a new SNMP Credential."""
        access_parameters = body.pop(protocol)
        snmp_cred_dict = self._create_snmp_cred_dict()
        for key, value in access_parameters.items():
            body[key] = value
        body['protocol_type'] = protocol
        snmp_cred = self._update_dict(body, snmp_cred_dict)
        db_snmp_cred = db.add_bnp_snmp_cred(context, snmp_cred)
        return db_snmp_cred

    def _create_netconf_creds(self, context, body, protocol):
        """Create a new NETCONF Credential."""
        access_parameters = body.pop(protocol)
        netconf_cred_dict = self._create_netconf_cred_dict()
        for key, value in access_parameters.items():
            body[key] = value
        body['protocol_type'] = protocol
        netconf_cred = self._update_dict(body, netconf_cred_dict)
        db_netconf_cred = db.add_bnp_netconf_cred(context, netconf_cred)
        return db_netconf_cred

    def _create_snmp_cred_dict(self):
        """Create SNMP credential dict."""
        snmp_cred_dict = {
            'name': None,
            'protocol_type': None,
            'security_name': None,
            'write_community': None,
            'auth_protocol': None,
            'auth_key': None,
            'priv_protocol': None,
            'priv_key': None,
            'security_level': None}
        return snmp_cred_dict

    def _create_netconf_cred_dict(self):
        """Create NETCONF credential dict."""
        netconf_cred_dict = {
            'name': None,
            'protocol_type': None,
            'user_name': None,
            'password': None,
            'key_path': None}
        return netconf_cred_dict

    def check_creds_proto_type(self, switch_creds, id, protocol):
        if not switch_creds or (switch_creds.get('protocol_type')
                                != protocol.lower()):
            raise webob.exc.HTTPBadRequest(
                _("protocol type cannot be updated for the id %s") % id)

    def _update_dict(self, body, cred_dict):
        """Update the existing dict."""
        for key in cred_dict.keys():
            if key in body.keys():
                cred_dict[key] = body[key]
        return cred_dict

    def update(self, request, id, **kwargs):
        context = request.context
        self._check_admin(context)
        body = validators.validate_request(request)
        protocol = validators.validate_access_parameters_for_update(body)
        key_list = ['name', 'snmpv1', 'snmpv2c',
                    'snmpv3', 'netconf_ssh', 'netconf_soap']
        keys = body.keys()
        validators.validate_attributes(keys, key_list)
        if not uuidutils.is_uuid_like(id):
            raise webob.exc.HTTPBadRequest(
                _("Invalid Id"))
        if not protocol:
            switch_creds = db.get_snmp_cred_by_id(context, id)
            if switch_creds:
                switch_creds_dict = self._update_dict(body, dict(switch_creds))
                db.update_bnp_snmp_cred_by_id(context, id, switch_creds_dict)
                return switch_creds_dict
            switch_creds = db.get_netconf_cred_by_id(context, id)
            if switch_creds:
                switch_creds_dict = self._update_dict(body, dict(switch_creds))
                db.update_bnp_netconf_cred_by_id(
                    context, id, switch_creds_dict)
                return switch_creds_dict
            raise webob.exc.HTTPNotFound(
                _("Credential with id=%s does not exist") % id)

        elif protocol in [const.SNMP_V1, const.SNMP_V2C]:
            switch_creds = db.get_snmp_cred_by_id(context, id)
            if not switch_creds:
                raise webob.exc.HTTPNotFound(
                    _("Credential with id=%s does not exist") % id)
            self.check_creds_proto_type(switch_creds, id, protocol)
            params = body.pop(protocol)
            for key, value in params.items():
                body[key] = value
            creds_dict = self._update_dict(body, dict(switch_creds))
            db.update_bnp_snmp_cred_by_id(context, id, creds_dict)
            return creds_dict

        elif protocol == const.SNMP_V3:
            switch_creds = db.get_snmp_cred_by_id(context, id)
            if not switch_creds:
                raise webob.exc.HTTPNotFound(
                    _("Credential with id=%s does not exist") % id)
            self.check_creds_proto_type(switch_creds, id, protocol)
            params = body.pop(protocol)
            if ('auth_protocol' in params.keys()) ^ (
                    'auth_key' in params.keys()):
                if (not switch_creds['auth_protocol']) and (
                        not switch_creds['auth_key']):
                    raise webob.exc.HTTPBadRequest(
                        _("auth_protocol and auth_key values does not exist,"
                          " so both has to be provided"))
            if ('priv_protocol' in params.keys()) ^ ('priv_key'
                                                     in params.keys()):
                if (not switch_creds['priv_protocol']) and (
                        not switch_creds['priv_key']):
                    raise webob.exc.HTTPBadRequest(
                        _("priv_protocol and priv_key values does not exist,"
                          " so both has to be provided"))
            for key, value in params.items():
                body[key] = value
            creds_dict = self._update_dict(body, dict(switch_creds))
            db.update_bnp_snmp_cred_by_id(context, id, creds_dict)
            return creds_dict

        elif protocol == const.NETCONF_SOAP:
            switch_creds = db.get_netconf_cred_by_id(context, id)
            if not switch_creds:
                raise webob.exc.HTTPNotFound(
                    _("Credential with id=%s does not exist") % id)
            self.check_creds_proto_type(switch_creds, id, protocol)
            params = body.pop(protocol)
            for key, value in params.items():
                body[key] = value
            creds_dict = self._update_dict(body, dict(switch_creds))
            db.update_bnp_netconf_cred_by_id(context, id, creds_dict)
            return creds_dict

        elif protocol == const.NETCONF_SSH:
            switch_creds = db.get_netconf_cred_by_id(context, id)
            if not switch_creds:
                raise webob.exc.HTTPNotFound(
                    _("Credential with id=%s does not exist") % id)
            self.check_creds_proto_type(switch_creds, id, protocol)
            params = body.pop(protocol)
            if ('user_name' in params.keys()) ^ ('password' in params.keys()):
                if (not switch_creds['user_name']) and (
                        not switch_creds['password']):
                    raise webob.exc.HTTPBadRequest(
                        _("user_name and password values does not exist, so"
                          " both has to be provided"))
            for key, value in params.items():
                body[key] = value
            creds_dict = self._update_dict(body, dict(switch_creds))
            db.update_bnp_netconf_cred_by_id(context, id, creds_dict)
            return creds_dict


class Bnp_credential(nl_extensions.ExtensionDescriptor):

    """API extension for Baremetal Switch Credential support."""

    @classmethod
    def get_name(cls):
        return "Bnp-Credential"

    @classmethod
    def get_alias(cls):
        return "bnp-credential"

    @classmethod
    def get_description(cls):
        return ("Abstraction for protocol credentials"
                " for bare metal instance network provisioning")

    @classmethod
    def get_updated(cls):
        return "2016-03-22T00:00:00-00:00"

    def get_resources(self):
        exts = []
        controller = resource.Resource(BNPCredentialController(),
                                       base.FAULT_MAP)
        exts.append(extensions.ResourceExtension(
            'bnp-credentials', controller))
        return exts

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}
