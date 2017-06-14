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


from mox3 import mox

from networking_hpe.bnpclient.bnp_client_ext.v2_0 import (
    client as bnpswitchclient)

from neutronclient import shell as neutronshell
from neutronclient.tests.unit import test_cli20 as neutron_test_cli20

TOKEN = neutron_test_cli20.TOKEN
end_url = neutron_test_cli20.end_url


class MyResp(neutron_test_cli20.MyResp):

    pass


class MyApp(neutron_test_cli20.MyApp):

    pass


class MyComparator(neutron_test_cli20.MyComparator):

    pass


class CLITestV20Base(neutron_test_cli20.CLITestV20Base):

    format = 'json'
    test_id = 'fake_id'
    id_field = 'id'

    def setUp(self, plurals=None):
        """Prepare the test environment."""
        super(CLITestV20Base, self).setUp()
        self.client = bnpswitchclient.Client(
            token=TOKEN, endpoint_url=self.endurl)

    def _get_resource_plural(self, resource, client):
        plurals = getattr(client, 'EXTED_PLURALS', [])
        for k in plurals:
            if plurals[k] == resource:
                return k
        return resource + 'es'

    def _test_create_resource(self, resource, cmd, name, myid, args,
                              position_names, position_values,
                              tags=None, admin_state_up=True,
                              extra_body=None, cmd_resource=None,
                              parent_id=None, no_api_call=False,
                              expected_exception=None,
                              **kwargs):
        self.mox.StubOutWithMock(cmd, "get_client")
        self.mox.StubOutWithMock(self.client.httpclient, "request")
        cmd.get_client().MultipleTimes().AndReturn(self.client)
        if not cmd_resource:
            cmd_resource = resource
        body = {resource: {}, }
        body[resource].update(kwargs)

        for i in range(len(position_names)):
            body[resource].update({position_names[i]: position_values[i]})
        ress = {resource:
                {self.id_field: myid}, }
        if name:
            ress[resource].update({'name': name})
        self.client.format = self.format
        resstr = self.client.serialize(ress)
        resource_plural = self._get_resource_plural(cmd_resource, self.client)
        path = getattr(self.client, resource_plural + "_path")
        if self.format == 'json':
            mox_body = MyComparator(body, self.client)
        else:
            mox_body = self.client.serialize(body)
        self.client.httpclient.request(
            end_url(path), 'POST',
            body=mox_body,
            headers=mox.ContainsKeyValue(
                'X-Auth-Token', TOKEN)).AndReturn((MyResp(200), resstr))
        args.extend(['--request-format', self.format])
        self.mox.ReplayAll()
        cmd_parser = cmd.get_parser('create_' + resource)
        neutronshell.run_command(cmd, cmd_parser, args)
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        _str = self.fake_stdout.make_string()
        self.assertIn(myid, _str)
        if name:
            self.assertIn(name, _str)
