# Copyright (c) 2015 OpenStack Foundation.
# Copyright (c) 2016 Hewlett-Packard Enterprise Development L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# service type constants:

from simplejson import scanner as json_scanner
import webob.exc

from copy import deepcopy
import os.path

from networking_hpe.common import constants as const

from oslo_utils import uuidutils


access_parameter_keys = ['write_community', 'security_name',
                         'auth_protocol', 'priv_protocol', 'auth_key',
                         'priv_key', 'security_level']


def access_parameter_validator(data, valid_values=None):
    """Validate the access parameters."""
    if not data:
        # Access parameters must be provided.
        msg = _("Cannot create a switch from the given input.")
        return msg
    if type(data) is not dict:
        msg = _("Given details is not in the form of a dictionary.")
        return msg


def validate_request(request):
    """Validate if the request is in proper format."""
    try:
        body = request.json_body
    except json_scanner.JSONDecodeError:
        raise webob.exc.HTTPBadRequest(
            _("Invalid JSON body"))
    try:
        keys = list(body.keys())
        if keys[0] in [const.BNP_SWITCH_RESOURCE_NAME,
                       const.BNP_CREDENTIAL_RESOURCE_NAME]:
            body = body.pop(keys[0])
    except KeyError:
        raise webob.exc.HTTPBadRequest(
            _("resource name not found in request body"))
    return body


def validate_attributes(keys, attr_keys):
    """Validate the keys in request body."""
    extra_keys = set(keys) - set(attr_keys)
    if extra_keys:
        msg = _("Unrecognized attribute(s) '%s'") % ', '.join(extra_keys)
        raise webob.exc.HTTPBadRequest(msg)


def validate_access_parameters(body):
    """Validate if the request body is in proper format."""
    protocol_dict = deepcopy(body)
    if const.NAME not in protocol_dict.keys():
        raise webob.exc.HTTPBadRequest(
            _("Name not found in request body"))
    if uuidutils.is_uuid_like(protocol_dict['name']):
        raise webob.exc.HTTPBadRequest(
            _("Name=%s should not be in uuid format") %
            protocol_dict['name'])
    protocol_dict.pop('name')
    keys = list(protocol_dict.keys())
    if not len(keys):
        raise webob.exc.HTTPBadRequest(
            _("Request body should have at least one protocol specified"))
    elif len(keys) > 1:
        raise webob.exc.HTTPBadRequest(
            _("multiple protocols in a single request is not supported"))
    key = keys[0]
    if key.lower() not in const.SUPPORTED_PROTOCOLS:
        raise webob.exc.HTTPBadRequest(
            _("'protocol %s' is not supported") % keys)
    if key.lower() == const.SNMP_V3:
        return validate_snmpv3_parameters(protocol_dict, key)
    elif key.lower() in [const.NETCONF_SSH, const.NETCONF_SOAP]:
        return validate_netconf_parameters(protocol_dict, key)
    else:
        return validate_snmp_parameters(protocol_dict, key)


def validate_snmp_parameters(protocol_dict, key):
    """Validate SNMP v1 and v2c parameters."""
    access_parameters = protocol_dict.pop(key)
    keys = access_parameters.keys()
    validate_attributes(keys, ['write_community'])
    if not access_parameters.get('write_community'):
        raise webob.exc.HTTPBadRequest(
            _("'write_community' not found in request body"))
    if key.lower() == const.SNMP_V1:
        return const.SNMP_V1
    else:
        return const.SNMP_V2C


def validate_snmpv3_parameters(protocol_dict, key):
    """Validate SNMP v3 parameters."""
    access_parameters = protocol_dict.pop(key)
    keys = access_parameters.keys()
    attr_keys = ['security_name', 'auth_protocol',
                 'auth_key', 'priv_protocol', 'priv_key']
    validate_attributes(keys, attr_keys)
    if not access_parameters.get('security_name'):
        raise webob.exc.HTTPBadRequest(
            _("security_name not found in request body"))
    if access_parameters.get('auth_protocol'):
        if access_parameters.get('auth_protocol').lower(
        ) not in const.SUPPORTED_AUTH_PROTOCOLS:
            raise webob.exc.HTTPBadRequest(
                _("auth_protocol %s is not supported") %
                access_parameters['auth_protocol'])
        elif not access_parameters.get('auth_key'):
            raise webob.exc.HTTPBadRequest(
                _("auth_key is required for auth_protocol %s") %
                access_parameters['auth_protocol'])
        elif len(access_parameters.get('auth_key')) < 8:
            raise webob.exc.HTTPBadRequest(
                _("auth_key %s should be equal or more than"
                  "8 characters") % access_parameters['auth_key'])
    if access_parameters.get('priv_protocol'):
        if access_parameters.get('priv_protocol').lower(
        ) not in const.SUPPORTED_PRIV_PROTOCOLS:
            raise webob.exc.HTTPBadRequest(
                _("priv_protocol %s is not supported") %
                access_parameters['priv_protocol'])
        elif not access_parameters.get('priv_key'):
            raise webob.exc.HTTPBadRequest(
                _("priv_key is required for priv_protocol %s") %
                access_parameters['priv_protocol'])
        elif len(access_parameters.get('priv_key')) < 8:
            raise webob.exc.HTTPBadRequest(
                _("'priv_key %s' should be equal or more than"
                  "8 characters") % access_parameters['priv_key'])
    return const.SNMP_V3


def _validate_user_name_password(access_parameters):
    """Validate if the request contains user_name and password."""
    if not access_parameters.get('user_name'):
        raise webob.exc.HTTPBadRequest(
            _("user_name not found in request body"))
    elif not access_parameters.get('password'):
        raise webob.exc.HTTPBadRequest(
            _("password not found in request body"))


def validate_netconf_parameters(protocol_dict, key):
    """Validate NETCONF SSH/SOAP parameters."""
    access_parameters = protocol_dict.pop(key)
    if key.lower() == const.NETCONF_SSH:
        if access_parameters.get('key_path'):
            if not os.path.isfile(access_parameters.get('key_path')):
                raise webob.exc.HTTPBadRequest(
                    _("Invalid key path"))
            return const.NETCONF_SSH
        _validate_user_name_password(access_parameters)
        return const.NETCONF_SSH
    else:
        if access_parameters.get('key_path'):
            raise webob.exc.HTTPBadRequest(
                _("Invalid attribute key_path"))
        _validate_user_name_password(access_parameters)
        return const.NETCONF_SOAP


def validate_access_parameters_for_update(body):
    """Validate if the request body is in proper format."""

    protocol_dict = deepcopy(body)
    if (const.NAME not in protocol_dict.keys() and
       not len(protocol_dict.keys())):
        raise webob.exc.HTTPBadRequest(
            _("Request must have name or one protocol type"))
    if const.NAME in protocol_dict.keys():
        if uuidutils.is_uuid_like(protocol_dict['name']):
            raise webob.exc.HTTPBadRequest(
                _("Name=%s should not be in uuid format") %
                protocol_dict['name'])
        protocol_dict.pop('name')
    if protocol_dict:
        keys = list(protocol_dict.keys())
        if len(keys) > 1:
            raise webob.exc.HTTPBadRequest(
                _("Multiple protocols in a single request is not supported"))
        key = keys[0]
        if key.lower() not in const.SUPPORTED_PROTOCOLS:
            raise webob.exc.HTTPBadRequest(
                _("Protocol %s is not supported") % keys)
        if key.lower() == const.SNMP_V3:
            return validate_snmpv3_parameters_for_update(protocol_dict, key)
        elif key.lower() in [const.NETCONF_SSH, const.NETCONF_SOAP]:
            return validate_netconf_parameters_for_update(protocol_dict, key)
        else:
            return validate_snmp_parameters_for_update(protocol_dict, key)
    else:
        return None


def validate_snmpv3_parameters_for_update(protocol_dict, key):
    """Validate SNMP v3 parameters."""
    access_parameters = protocol_dict.pop(key)
    keys = list(access_parameters.keys())
    attr_keys = ['security_name', 'auth_protocol',
                 'auth_key', 'priv_protocol', 'priv_key']
    validate_attributes(keys, attr_keys)
    if access_parameters.get('auth_protocol'):
        if access_parameters.get('auth_protocol').lower(
        ) not in const.SUPPORTED_AUTH_PROTOCOLS:
            raise webob.exc.HTTPBadRequest(
                _("auth_protocol %s is not supported") %
                access_parameters['auth_protocol'])
    if access_parameters.get('auth_key'):
        if len(access_parameters.get('auth_key')) < 8:
            raise webob.exc.HTTPBadRequest(
                _("auth_key %s should be equal or more than"
                  " 8 characters") % access_parameters['auth_key'])
    if access_parameters.get('priv_protocol'):
        if access_parameters.get('priv_protocol').lower(
        ) not in const.SUPPORTED_PRIV_PROTOCOLS:
            raise webob.exc.HTTPBadRequest(
                _("priv_protocol %s is not supported") %
                access_parameters['priv_protocol'])
    if access_parameters.get('priv_key'):
        if len(access_parameters.get('priv_key')) < 8:
            raise webob.exc.HTTPBadRequest(
                _("priv_key %s should be equal or more than"
                  " 8 characters") % access_parameters['priv_key'])
    return const.SNMP_V3


def validate_netconf_parameters_for_update(protocol_dict, key):
    """Validate NETCONF SSH/SOAP parameters."""
    access_parameters = protocol_dict.pop(key)
    if key.lower() == const.NETCONF_SSH:
        keys = access_parameters.keys()
        attr_keys = ['user_name', 'password', 'key_path']
        validate_attributes(keys, attr_keys)
        if access_parameters.get('key_path'):
            if not os.path.isfile(access_parameters.get('key_path')):
                raise webob.exc.HTTPBadRequest(
                    _("Invalid key path"))
        return const.NETCONF_SSH
    else:
        keys = access_parameters.keys()
        attr_keys = ['user_name', 'password']
        validate_attributes(keys, attr_keys)
        return const.NETCONF_SOAP


def validate_snmp_parameters_for_update(protocol_dict, key):
    """Validate SNMP v1 and v2c parameters."""
    access_parameters = protocol_dict.pop(key)
    keys = access_parameters.keys()
    validate_attributes(keys, ['write_community'])
    if key.lower() == const.SNMP_V1:
        return const.SNMP_V1
    else:
        return const.SNMP_V2C
