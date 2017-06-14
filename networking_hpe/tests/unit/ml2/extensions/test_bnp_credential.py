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

from neutron.tests.unit.db import test_db_base_plugin_v2 as test_plugin
from neutron.tests.unit import testlib_api

from oslo_utils import uuidutils

from networking_hpe.ml2.extensions import bnp_credential

import os.path

import mock
import webob.exc


class TestBnpCredential(test_plugin.NeutronDbPluginV2TestCase,
                        testlib_api.WebTestCase):

    def setUp(self):
        super(TestBnpCredential, self).setUp()
        self.bnp_wsgi_controller = bnp_credential.BNPCredentialController()
        self.snmpv1_data = {"bnp_credential": {
            "name": "CRED1", "snmpv1": {"write_community": "public"}}}
        self.snmpv2c_data = {"bnp_credential": {
            "name": "CRED1", "snmpv2c": {"write_community": "public"}}}
        self.snmpv3_data = {"bnp_credential": {
            "name": "CRED1", "snmpv3": {"security_name": "FakeSecName"}}}
        self.netconf_ssh_data = {"bnp_credential": {"name": "CRED1",
                                                    "netconf_ssh": {
                                                        "user_name":
                                                        "FakeUserName",
                                                        "password":
                                                        "FakePassword",
                                                        "key_path": ("/home/"
                                                                     "fakedir"
                                                                     "/key1."
                                                                     "rsa")}}}
        self.netconf_soap_data = {"bnp_credential": {"name": "CRED1",
                                                     "netconf_soap": {
                                                         "user_name":
                                                         "FakeUserName",
                                                         "password":
                                                         "FakePassword"}}}

    def _test_update_credential(self, update_data, credential_id):
        update_request = self.new_update_request(
            'bnp-credentials', update_data, credential_id)
        return self.bnp_wsgi_controller.update(update_request, credential_id)

    def _test_update_credential_for_netconf_ssh(self, update_data,
                                                credential_id):
        update_request = self.new_update_request(
            'bnp-credentials', update_data, credential_id)
        with mock.patch.object(os.path, 'isfile', return_value=True):
            result = self.bnp_wsgi_controller.update(
                update_request, credential_id)
            os.path.isfile.called
        return result

    def _test_raised_exception_message(self, update_data, credential_id,
                                       error_string):
        test_status = False
        try:
            self._test_update_credential(update_data, credential_id)
        except Exception as raised_exception:
            test_status = True
            self.assertEqual(error_string, str(raised_exception))
        self.assertTrue(test_status)

    def _test_create_credential_for_snmp(self, body):
        create_req = self.new_create_request('bnp-credentials', body,
                                             'json')
        return self.bnp_wsgi_controller.create(create_req)

    def _test_create_credential_for_netconf(self, body):
        create_req = self.new_create_request('bnp-credentials', body,
                                             'json')
        with mock.patch.object(os.path, 'isfile', return_value=True):
            result = self.bnp_wsgi_controller.create(create_req)
            os.path.isfile.called
            return result

    def test_create_valid_cred_for_snmp(self):
        body_snmpv3 = {"bnp_credential":
                       {"name": "CRED1",
                        "snmpv3":
                        {"security_name": "xyz",
                         "auth_protocol": "md5",
                         "auth_key": "abcd1234",
                         "priv_protocol": "des",
                         "priv_key": "dummy_key"}}}
        body_snmpv1 = {"bnp_credential":
                       {"name": "CRED2",
                        "snmpv1":
                        {"write_community": "public"}}}
        body_snmpv2c = {"bnp_credential":
                        {"name": "CRED3",
                         "snmpv2c":
                         {"write_community": "public"}}}
        result_snmpv3 = self._test_create_credential_for_snmp(body_snmpv3)
        result_snmpv1 = self._test_create_credential_for_snmp(body_snmpv1)
        result_snmpv2c = self._test_create_credential_for_snmp(body_snmpv2c)
        self.assertEqual(result_snmpv3['bnp_credential']['name'],
                         body_snmpv3['bnp_credential']['name'])
        self.assertEqual(result_snmpv1['bnp_credential']['name'],
                         body_snmpv1['bnp_credential']['name'])
        self.assertEqual(result_snmpv2c['bnp_credential']['name'],
                         body_snmpv2c['bnp_credential']['name'])

    def test_create_valid_cred_for_netconf(self):
        body_netssh = {"bnp_credential":
                       {"name": "CRED1",
                        "netconf_ssh":
                        {"key_path": "/home/fakedir/key1.rsa"}}}
        body_netsoap = {"bnp_credential":
                        {"name": "CRED2",
                         "netconf_soap":
                         {"user_name": "fake_user",
                          "password": "fake_password"}}}
        result_netssh = self._test_create_credential_for_netconf(body_netssh)
        result_netsoap = self._test_create_credential_for_netconf(body_netsoap)
        self.assertEqual(result_netssh['bnp_credential']['name'],
                         body_netssh['bnp_credential']['name'])
        self.assertEqual(result_netsoap['bnp_credential']['name'],
                         body_netsoap['bnp_credential']['name'])

    def test_create_cred_with_invalid_protocol(self):
        body_snmp = {"bnp_credential":
                     {"name": "CRED1",
                      "snmpv4":
                      {"write_community": "public"}}}
        body_netconf = {"bnp_credential":
                        {"name": "CRED2",
                         "netconf-abc":
                         {"key_path": "/home/fakedir/key1.rsa"}}}
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_snmp,
                          body_snmp)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_netconf,
                          body_netconf)

    def test_create_cred_with_no_name(self):
        body_snmp = {"bnp_credential":
                     {"snmpv2c":
                      {"write_community": "public"}}}
        body_netconf = {"bnp_credential":
                        {"netconf-ssh":
                         {"key_path": "/home/fakedir/key1.rsa"}}}
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_snmp,
                          body_snmp)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_netconf,
                          body_netconf)

    def test_create_cred_with_invalid_parameters(self):
        body_snmpv2 = {"bnp_credential":
                       {"name": "CRED1",
                        "snmpv2c":
                        {"write_community": "public",
                         "fake_key": "/home/fakedir/key1.rsa"}}}
        body_snmpv3 = {"bnp_credential":
                       {"name": "CRED2",
                        "snmpv3":
                        {"security_name": "xyz",
                         "auth_protocol": "md5",
                         "priv_protocol": "des",
                         "priv_key": "dummy_key"}}}
        body_netssh = {"bnp_credential":
                       {"name": "CRED3",
                        "fake_key": "fake_value",
                        "netconf-ssh":
                        {"key_path": "/home/fakedir/key1.rsa"}}}
        body_netsoap = {"bnp_credential":
                        {"name": "CRED4",
                         "netconf-soap":
                         {"user_name": "fake_user"}}}
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_snmp,
                          body_snmpv2)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_snmp,
                          body_snmpv3)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_netconf,
                          body_netssh)
        self.assertRaises(webob.exc.HTTPBadRequest,
                          self._test_create_credential_for_netconf,
                          body_netsoap)

    def test_update_credential_snmpv1(self):
        credential = self._test_create_credential_for_snmp(self.snmpv1_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"snmpv1": {
            "write_community": "private"}, "name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "snmpv1",
                         "write_community": "private", "name": "NewCredName",
                         "security_name": None, "auth_protocol": None,
                         "auth_key": None, "priv_protocol": None,
                         "priv_key": None, "security_level": None}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_snmpv2c(self):
        credential = self._test_create_credential_for_snmp(self.snmpv2c_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"snmpv2c": {
            "write_community": "private"}, "name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "snmpv2c",
                         "write_community": "private", "name": "NewCredName",
                         "security_name": None, "auth_protocol": None,
                         "auth_key": None, "priv_protocol": None,
                         "priv_key": None, "security_level": None}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_snmpv3(self):
        credential = self._test_create_credential_for_snmp(self.snmpv3_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"snmpv3": {"security_name":
                                                     "NewFakeSecurityName",
                                                     "auth_protocol": "md5",
                                                     "auth_key": "FakeAuthKey",
                                                     "priv_protocol": "aes192",
                                                     "priv_key": "FakePrivKey"
                                                     }, "name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "snmpv3",
                         "write_community": None, "name": "NewCredName",
                         "security_name": "NewFakeSecurityName",
                         "auth_protocol": "md5", "auth_key": "FakeAuthKey",
                         "priv_protocol": "aes192", "priv_key": "FakePrivKey",
                         "security_level": None}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_netconf_ssh(self):
        credential = self._test_create_credential_for_netconf(
            self.netconf_ssh_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"netconf_ssh": {"user_name":
                                                          "NewFakeUserName",
                                                          "password":
                                                          "NewFakePassword",
                                                          "key_path": ("/home/"
                                                                       "faked"
                                                                       "ir/key"
                                                                       "1.rsa")
                                                          }, "name":
                                                             "NewCredName"}}
        updated_dict = self._test_update_credential_for_netconf_ssh(
            update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "netconf_ssh",
                         "user_name": "NewFakeUserName",
                         "password": "NewFakePassword", "key_path":
                         "/home/fakedir/key1.rsa", "name": "NewCredName"}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_netconf_soap(self):
        credential = self._test_create_credential_for_netconf(
            self.netconf_soap_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"netconf_soap": {
            "user_name": "NewFakeUserName", "password": "NewFakePassword"},
            "name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "netconf_soap",
                         "user_name": "NewFakeUserName",
                         "password": "NewFakePassword", "key_path": None,
                         "name": "NewCredName"}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_snmpv1_only_name(self):
        credential = self._test_create_credential_for_snmp(self.snmpv1_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "snmpv1",
                         "write_community": "public", "name": "NewCredName",
                         "security_name": None, "auth_protocol": None,
                         "auth_key": None, "priv_protocol": None,
                         "priv_key": None, "security_level": None}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_snmpv2c_only_name(self):
        credential = self._test_create_credential_for_snmp(self.snmpv2c_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "snmpv2c",
                         "write_community": "public", "name": "NewCredName",
                         "security_name": None, "auth_protocol": None,
                         "auth_key": None, "priv_protocol": None,
                         "priv_key": None, "security_level": None}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_snmpv3_only_name(self):
        credential = self._test_create_credential_for_snmp(self.snmpv3_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "snmpv3",
                         "write_community": None, "name": "NewCredName",
                         "security_name": "FakeSecName", "auth_protocol": None,
                         "auth_key": None, "priv_protocol": None,
                         "priv_key": None, "security_level": None}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_netconf_ssh_only_name(self):
        credential = self._test_create_credential_for_netconf(
            self.netconf_ssh_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"name": "NewCredName"}}
        updated_dict = self._test_update_credential_for_netconf_ssh(
            update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "netconf_ssh",
                         "user_name": "FakeUserName",
                         "password": "FakePassword", "key_path":
                         "/home/fakedir/key1.rsa", "name": "NewCredName"}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_netconf_soap_only_name(self):
        credential = self._test_create_credential_for_netconf(
            self.netconf_soap_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"name": "NewCredName"}}
        updated_dict = self._test_update_credential(update_data, credential_id)
        expected_dict = {"id": credential_id, "protocol_type": "netconf_soap",
                         "user_name": "FakeUserName",
                         "password": "FakePassword", "key_path": None,
                         "name": "NewCredName"}
        self.assertDictEqual(updated_dict, expected_dict)

    def test_update_credential_snmpv1_proto_type(self):
        credential = self._test_create_credential_for_snmp(self.snmpv1_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {
            "snmpv2c": {"write_community": "private"}}}
        error_string = ("protocol type cannot be updated for the id " +
                        str(credential_id))
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_snmpv2c_proto_type(self):
        credential = self._test_create_credential_for_snmp(self.snmpv2c_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {
            "snmpv1": {"write_community": "private"}}}
        error_string = ("protocol type cannot be updated for the id " +
                        str(credential_id))
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_snmpv3c_proto_type(self):
        credential = self._test_create_credential_for_snmp(self.snmpv3_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {
            "snmpv1": {"write_community": "private"}}}
        error_string = ("protocol type cannot be updated for the id " +
                        str(credential_id))
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_netconf_ssh_proto_type(self):
        credential = self._test_create_credential_for_netconf(
            self.netconf_ssh_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"netconf_soap": {
            "user_name": "FakeUserName", "password": "FakePassword"}}}
        error_string = ("protocol type cannot be updated for the id " +
                        str(credential_id))
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_netconf_soap_proto_type(self):
        credential = self._test_create_credential_for_netconf(
            self.netconf_soap_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"netconf_ssh": {
            "user_name": "FakeUserName", "password": "FakePassword"}}}
        error_string = ("protocol type cannot be updated for the id " +
                        str(credential_id))
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_auth_proto_or_auth_key_before_both_none(self):
        credential = self._test_create_credential_for_snmp(self.snmpv3_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {"snmpv3": {"auth_protocol": "md5"}}}
        error_string = ("auth_protocol and auth_key values does not exist,"
                        " so both has to be provided")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {
            "snmpv3": {"auth_key": "FakeAuthKey"}}}
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_priv_proto_or_priv_key_before_both_none(self):
        credential = self._test_create_credential_for_snmp(self.snmpv3_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {
            "snmpv3": {"priv_protocol": "aes192"}}}
        error_string = ("priv_protocol and priv_key values does not exist,"
                        " so both has to be provided")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {
            "snmpv3": {"priv_key": "FakePrivKey"}}}
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_user_name_or_password_before_both_none(self):
        netconf_ssh_data = {"bnp_credential": {
            "name": "CRED1", "netconf_ssh": {"key_path":
                                             "/home/fakedir/key1.rsa"}}}
        credential = self._test_create_credential_for_netconf(netconf_ssh_data)
        credential_id = credential["bnp_credential"]["id"]
        update_data = {"bnp_credential": {
            "netconf_ssh": {"user_name": "FakeUerName"}}}
        error_string = ("user_name and password values does not exist,"
                        " so both has to be provided")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {
            "netconf_ssh": {"password": "FakePassword"}}}
        self._test_raised_exception_message(
            update_data, credential_id, error_string)

    def test_update_credential_access_parameters(self):
        credential_id = uuidutils.generate_uuid()
        update_data = {"bnp_credential": {}}
        error_string = "Request must have name or one protocol type"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"snmpv1": {
            "write_community": "private"}, "snmpv2c": {"write_community":
                                                       "private"}}}
        error_string = ("Multiple protocols in a single request"
                        " is not supported")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        name = uuidutils.generate_uuid()
        update_data = {"bnp_credential": {
            "name": name, "snmpv1": {"write_community": "public"}}}
        error_string = "Name=" + str(name) + (" should not be in uuid"
                                              " format")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"fake_protocol_type": {
            "user_name": "FakeUserName", "password": "FakePassword"}}}
        fake_proto_str = u"fake_protocol_type"
        fake_proto_list = [fake_proto_str]
        error_string = str("Protocol ") + str(fake_proto_list) + str(
            " is not supported")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"snmpv3": {
            "auth_protocol": "FakeAuthProtocol", "auth_key": "AuthKey123"}}}
        error_string = "auth_protocol FakeAuthProtocol is not supported"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"snmpv3": {
            "auth_protocol": "sha", "auth_key": "AuthKey"}}}
        error_string = ("auth_key AuthKey should be equal or"
                        " more than 8 characters")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"snmpv3": {
            "priv_protocol": "FakePrivProto", "priv_key": "PrivKey123"}}}
        error_string = "priv_protocol FakePrivProto is not supported"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"snmpv3": {
            "priv_protocol": "aes192", "priv_key": "PrivKey"}}}
        error_string = ("priv_key PrivKey should be equal or more than 8"
                        " characters")
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"netconf_ssh": {
            "key_path": "/home/FaKeDiR/FaKeFiLe.fakeExtension"}}}
        error_string = "Invalid key path"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {
            "snmpv1": {"fake_attribute": "private"}}}
        error_string = "Unrecognized attribute(s) 'fake_attribute'"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {
            "snmpv2c": {"fake_attribute": "private"}}}
        error_string = "Unrecognized attribute(s) 'fake_attribute'"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"snmpv3": {
            "fake_attr1": "FakeValue1", "auth_protocol": "md5", "auth_key":
            "FakeAuthKey"}}}
        error_string = "Unrecognized attribute(s) 'fake_attr1'"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"netconf_ssh": {
            "user_name": "FakeUserName", "password": "FakePassword",
            "fake_attr": "FakeValue"}}}
        error_string = "Unrecognized attribute(s) 'fake_attr'"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
        update_data = {"bnp_credential": {"netconf_soap": {
            "user_name": "FakeUserName", "password": "FakePassword",
            "fake_attr": "FakeValue"}}}
        error_string = "Unrecognized attribute(s) 'fake_attr'"
        self._test_raised_exception_message(
            update_data, credential_id, error_string)
